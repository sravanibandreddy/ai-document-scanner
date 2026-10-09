
import cv2


def preprocess_image(image):
    """
    Improve image contrast and readability for OCR.
    Accepts an OpenCV image array.
    """
    if image is None:
        raise ValueError("The input image is empty.")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Improve contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    contrast = clahe.apply(gray)

    # Reduce noise
    denoised = cv2.medianBlur(contrast, 3)

    # Convert to black and white
    _, processed = cv2.threshold(
        denoised,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return processed
