import cv2
import numpy as np

# ============================================================
# TUNABLE PARAMETERS
# ============================================================
CANNY_THRESHOLD1 = 50       # lower = more sensitive, higher = less sensitive
CANNY_THRESHOLD2 = 150      # upper edge threshold
BLUR_KERNEL = (5, 5)        # (3,3) less blur, (7,7) more blur
DILATE_ITERATIONS = 2       # higher = more connected edges
NOISE_FILTER = 500          # minimum area to consider (ignore smaller)
MILD_THRESHOLD = 3000       # area below this = mild, above = severe
# ============================================================

video_path = "/home/joshua-jericho-barja/Documents/fix_ai/crack.mp4"      # change path

output_path = "wow.mp4"

cap = cv2.VideoCapture(video_path)

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

def detect_cracks(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, BLUR_KERNEL, 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, threshold1=CANNY_THRESHOLD1, threshold2=CANNY_THRESHOLD2)
    
    # Morphological operations to connect crack edges
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=DILATE_ITERATIONS)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return contours

def classify_severity(area):
    if area < NOISE_FILTER:
        return None                                         # too small, ignore
    elif area < MILD_THRESHOLD:
        return "Mild Crack", (0, 255, 255)                 # yellow
    else:
        return "Severe Crack", (0, 0, 255)                 # red

print(f"Processing video: {total_frames} frames...")

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    contours = detect_cracks(frame)

    crack_found = False
    for contour in contours:
        area = cv2.contourArea(contour)
        result = classify_severity(area)
        
        if result is None:
            continue
        
        label, color = result
        crack_found = True

        # Draw contour around crack
        cv2.drawContours(frame, [contour], -1, color, 2)

        # Draw bounding box
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Label above bounding box
        cv2.putText(frame, f"{label} (area: {int(area)})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Overall status on top of frame
    status = "CRACK DETECTED" if crack_found else "NO CRACK"
    status_color = (0, 0, 255) if crack_found else (0, 255, 0)
    cv2.putText(frame, status, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)

    # Frame counter
    cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    out.write(frame)

    frame_count += 1
    if frame_count % 100 == 0:
        print(f"Processed {frame_count}/{total_frames} frames")

cap.release()
out.release()
print(f"\nSaved to: {output_path}")