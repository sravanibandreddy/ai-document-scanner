
import cv2
import pytesseract
from smart_extraction import extract_information

# Configure the Tesseract OCR application
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def process_document(image_path):
    # Check whether the image exists and can be opened
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Image not found.")
        return

    # Extract text from the image
    extracted_text = pytesseract.image_to_string(image)

    print("\n========== EXTRACTED TEXT ==========")
    print(extracted_text)

    # Identify important information
    information = extract_information(extracted_text)

    print("\n========== SMART EXTRACTION ==========")
    print("Emails:", information["emails"])
    print("Phone numbers:", information["phone_numbers"])
    print("Dates:", information["dates"])

    # Save extracted text to a file
    with open("extracted_text.txt", "w", encoding="utf-8") as file:
        file.write(extracted_text)

    print("\nText saved to extracted_text.txt")


if __name__ == "__main__":
    image_path = "scanned.png"
    process_document(image_path)
