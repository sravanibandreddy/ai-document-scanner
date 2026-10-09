
import cv2
import numpy as np


def preprocess_image(image):
    if image is None or image.size == 0:
        return image

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Enlarge small documents to help OCR recognize text.
    height, width = gray.shape
    if max(height, width) < 1400:
        scale = min(2.0, 1400 / max(height, width))
        gray = cv2.resize(
            gray, None, fx=scale, fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    # Improve local contrast.
    clahe = cv2.createCLAHE(
        clipLimit=2.0, tileGridSize=(8, 8)
    )
    enhanced = clahe.apply(gray)

    # Reduce small image noise.
    denoised = cv2.fastNlMeansDenoising(
        enhanced, None, 10, 7, 21
    )

    # Convert to black and white while keeping dark text.
    result = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return result
