
import cv2
import pytesseract
from preprocessing import preprocess_image

# Set the Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Image to test
image_path = "document_photo.jpg"

# Load the original image
image = cv2.imread(image_path)

if image is None:
    print("Error: Image not found:", image_path)

else:
    # OCR on the original image
    original_text = pytesseract.image_to_string(image)

    # Preprocess the image
    processed_image = preprocess_image(image)

    # OCR on the processed image
    processed_text = pytesseract.image_to_string(
        processed_image
    )

    print("\n========== ORIGINAL OCR ==========")
    print(original_text)

    print("\n========== PREPROCESSED OCR ==========")
    print(processed_text)

    # Save both results
    with open("original_ocr.txt", "w", encoding="utf-8") as f:
        f.write(original_text)

    with open("processed_ocr.txt", "w", encoding="utf-8") as f:
        f.write(processed_text)

    print("\nComparison complete!")
    print("Saved: original_ocr.txt")
    print("Saved: processed_ocr.txt")
