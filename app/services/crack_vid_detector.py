import cv2
import numpy as np
from urllib.parse import urlparse
import requests
import tempfile
import os
from app.utils.uploads import upload_file

# TUNABLE PARAMETERS
CANNY_THRESHOLD1 = 50
CANNY_THRESHOLD2 = 150
BLUR_KERNEL = (5, 5)
DILATE_ITERATIONS = 2
NOISE_FILTER = 500

LOW_THRESHOLD = 1500
MILD_THRESHOLD = 3000
HIGH_THRESHOLD = 6000

MAX_CRACK_AREA = 8000


def detect_cracks(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, BLUR_KERNEL, 0)
    edges = cv2.Canny(blurred, CANNY_THRESHOLD1, CANNY_THRESHOLD2)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=DILATE_ITERATIONS)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def classify_severity_and_probability(area):
    if area < NOISE_FILTER:
        return None
    probability = min(area / MAX_CRACK_AREA, 1.0) * 100
    if area < LOW_THRESHOLD:
        return "Low", (0, 255, 0), probability
    elif area < MILD_THRESHOLD:
        return "Mild", (0, 255, 255), probability
    else:
        return "High", (0, 0, 255), probability


def resolve_video_path(video_input: str):
    """
    If URL → download to temp file
    If local path → return as-is
    """
    parsed_url = urlparse(video_input)

    # Local file
    if parsed_url.scheme == "":
        if not os.path.exists(video_input):
            raise FileNotFoundError(f"File not found: {video_input}")
        return video_input

    # Remote URL
    if parsed_url.scheme in ("http", "https"):
        try:
            response = requests.get(video_input, stream=True, timeout=30)
            response.raise_for_status()

            suffix = os.path.splitext(parsed_url.path)[1] or ".mp4"

            fd, temp_path = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return temp_path

        except Exception as e:
            raise RuntimeError("Failed to download video") from e

    raise ValueError(f"Unsupported video input: {video_input}")


def analyze_crack_video(video_input: str):
    local_input_path = resolve_video_path(video_input)
    temp_output_path = None

    try:
        cap = cv2.VideoCapture(local_input_path)
        if not cap.isOpened():
            raise RuntimeError("Failed to open video")

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Create temp output video
        fd, temp_output_path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)  # close OS fd; VideoWriter will write
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

        overall_max_probability = 0
        overall_max_severity = "Low"
        severity_rank = {"Low": 1, "Mild": 2, "High": 3}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            contours = detect_cracks(frame)

            for contour in contours:
                area = cv2.contourArea(contour)
                result = classify_severity_and_probability(area)
                if result is None:
                    continue

                label, color, probability = result

                if (
                    severity_rank[label] > severity_rank[overall_max_severity]
                    or probability > overall_max_probability
                ):
                    overall_max_severity = label
                    overall_max_probability = probability

                cv2.drawContours(frame, [contour], -1, color, 2)
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(
                    frame,
                    f"{label} ({int(area)})",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

            out.write(frame)

        # Release video objects
        out.release()
        cap.release()

        # Ensure OS flush
        os.sync()

        # Upload video to Cloudinary
        upload_result = upload_file(temp_output_path, resource_type="video")
        file_url = upload_result["secure_url"]
        filename = upload_result["original_filename"]

        if not file_url:
            raise RuntimeError(
                "Cloudinary upload failed or did not return a secure URL"
            )

        return {
            "file_url": file_url,
            "filename": filename,
            "severity": overall_max_severity,
            "probability": overall_max_probability,
        }

    finally:
        # Cleanup temp files
        if temp_output_path and os.path.exists(temp_output_path):
            os.remove(temp_output_path)
        if local_input_path != video_input and os.path.exists(local_input_path):
            os.remove(local_input_path)
