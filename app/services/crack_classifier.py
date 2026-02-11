import os
import requests
import threading
import numpy as np
import cv2
import tensorflow as tf
from urllib.parse import urlparse
from PIL import Image

import tempfile

from app.utils.uploads import upload_file


class CrackClassifier:
    def __init__(self, model_path: str):
        """
        Constructor: loads the TFLite model ONCE.
        """
        self.interpreter = tf.lite.Interpreter(model_path=model_path, num_threads=1)
        self.interpreter.allocate_tensors()

        self.input_details  = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self._lock = threading.Lock()


    def _resolve_image_path(self, image_input: str) -> str:
        """
        Downloads an image from a URL and saves it to a temp file.
        Returns the local file path.
        """

        parsed = urlparse(image_input)

        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL: {image_input}")

        try:
            response = requests.get(image_input, timeout=10)
            response.raise_for_status()

            suffix = os.path.splitext(parsed.path)[1]
            if suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                suffix = ".jpg"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(response.content)
                return temp_file.name

        except Exception as e:
            raise RuntimeError(f"Failed to download image: {image_input}") from e
        

    # ---------- PREPROCESS FUNCTIONS ----------
    def _mobilenet_standard_scaling(self, image_array_rgb):
        x = image_array_rgb.astype(np.float32)
        x /= 127.5
        x -= 1.0
        return x

    def _preprocess_image(self, image_path, target_size=(256, 256)):
        if not image_path or not os.path.exists(image_path):
            raise FileNotFoundError(f"Invalid image path: {image_path}")

        try:
            img = Image.open(image_path).convert("RGB")
        except Exception as e:
            raise RuntimeError(f"PIL failed to open image: {image_path}") from e

        img = img.resize(target_size, Image.Resampling.LANCZOS)
        img_array = np.array(img)
        return self._mobilenet_standard_scaling(img_array)


    # ---------- PREDICT FUNCTION ----------
    def predict(self, image_path: str) -> float:
        img = self._preprocess_image(image_path)
        img = np.expand_dims(img, axis=0)

        with self._lock:
            self.interpreter.set_tensor(self.input_details[0]['index'], img)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])

        return float(output[0][0])

        
    def analyze_and_save(self, image_path: str, confidence_threshold: float = 0.4) -> dict:
        """
        Analyzes image, draws crack contours if confidence > threshold,
        saves processed image, uploads to Cloudinary, and returns info.
        """
        resolved_path = self._resolve_image_path(image_path)

        try:
            # Run prediction
            prob = self.predict(resolved_path)  # 0.0 to 1.0

            # Load image
            img = cv2.imread(resolved_path)
            if img is None:
                raise RuntimeError(f"Failed to load image: {resolved_path}")
            output = img.copy()

            # Draw contours / text
            if prob >= confidence_threshold:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                binary = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV, 99, 15
                )
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
                binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 200]

                cv2.drawContours(output, valid_contours, -1, (200, 0, 0), 3)
                for cnt in valid_contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(output, (x, y), (x + w, y + h), (100, 255, 100), 3)

                cv2.putText(
                    output,
                    f"Crack: {prob*100:.1f}%",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255) if prob > 0.8 else (0, 165, 255),
                    2
                )
            else:
                cv2.putText(
                    output,
                    f"No Crack ({prob*100:.1f}%)",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2
                )

            # Save processed image temporarily
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            cv2.imwrite(temp_file.name, output)

            # Upload to Cloudinary
            result = upload_file(temp_file.name)
            file_url = result.get("secure_url")

            # Determine severity
            if prob >= 0.8:
                severity = "High"
            elif prob >= 0.4:
                severity = "Mild"
            else:
                severity = "Low"

            return {
                "file_url": file_url,
                "severity": severity,
                "probability": prob
            }

        finally:
            # Cleanup temp files
            if resolved_path != image_path and os.path.exists(resolved_path):
                os.remove(resolved_path)
            if 'temp_file' in locals() and os.path.exists(temp_file.name):
                os.remove(temp_file.name)
