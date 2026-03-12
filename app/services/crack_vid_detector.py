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

    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
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
    """Resolves the video path. If it's a URL, it downloads the video and returns the local path. If it's already a local path, it returns it directly."""
    parsed_url = urlparse(video_input)
    if parsed_url.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL format: {video_input}")

    try:
        response = requests.get(video_input, stream=True)
        response.raise_for_status()

        suffix = os.path.splitext(parsed_url.path)[1]
        if suffix.lower() not in ['.mp4', '.avi', '.mov']:
            suffix = '.mp4'

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(response.content)
            return temp_file.name
        
    except Exception as e:
        raise RuntimeError(f"Failed to download video: {video_input}") from e

# MAIN FUNCTION
def analyze_crack_video(video_path: str):
    video_path = resolve_video_path(video_path)

    cap = cv2.VideoCapture(video_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    overall_max_probability = 0
    overall_max_severity = "Low"
    severity_rank = {"Low": 1, "Mild": 2, "High": 3}

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        contours = detect_cracks(frame)
        crack_found = False

        for contour in contours:
            area = cv2.contourArea(contour)
            result = classify_severity_and_probability(area)

            if result is None:
                continue

            label, color, probability = result
            crack_found = True

            # Track overall result
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
                f"{label} (area: {int(area)})",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        status = "CRACK DETECTED" if crack_found else "NO CRACK"
        status_color = (0, 0, 255) if crack_found else (0, 255, 0)
        cv2.putText(frame, status, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)

        cv2.putText(frame, f"Frame: {frame_count}/{total_frames}",
                    (20, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()

    # Save processed video temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    cv2.VideoWriter(temp_file.name, fourcc, fps, (width, height))

    # Upload to Cloudinary
    result = upload_file(temp_file.name)
    output_path = result.get("secure_url")
    filename = result.get("original_filename")

    return {
        "file_url": output_path,
        "filename": filename,
        "severity": overall_max_severity,
        "probability": overall_max_probability
    }
