
import pytesseract
from PIL import Image

# Tell Python where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Ask the user for an image path
image_path = input("Enter your document image path: ").strip().strip('"')

try:
    # Open the document image
    image = Image.open(image_path).convert("RGB")

    # Extract English text using OCR
    text = pytesseract.image_to_string(image, lang="eng")

    print("\n========== EXTRACTED TEXT ==========")

    if text.strip():
        print(text)
    else:
        print("No text detected. Try a clearer document image.")

    # Save the extracted text
    with open("extracted_text.txt", "w", encoding="utf-8") as file:
        file.write(text)

    print("\nText saved to extracted_text.txt")

except FileNotFoundError:
    print("Image not found. Please check the image path.")

except Exception as error:
    print(f"An error occurred: {error}")
