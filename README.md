# AI Document Scanner and Smart Text Extractor

An AI-powered document scanning application that detects document boundaries, corrects perspective, extracts text using Optical Character Recognition (OCR), and identifies important information such as email addresses, phone numbers, and dates.

## Features

- Upload document images.
- Detect document boundaries and correct perspective using OpenCV.
- Extract text using Tesseract OCR.
- Preprocess images to improve text recognition.
- Automatically identify email addresses, phone numbers, and dates.
- Save scan results and view scan history using SQLite.
- Download extracted text.
- Simple web interface built with FastAPI.

## Technologies Used

- **Language:** Python
- **Backend:** FastAPI
- **Image Processing:** OpenCV, NumPy, Pillow
- **OCR:** Tesseract OCR, pytesseract
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Development Tool:** Visual Studio Code

## Project Structure

```text
ai-document-scanner/
├── app.py
├── database.py
├── document_scanner.py
├── preprocessing.py
├── smart_extraction.py
├── ocr_test.py
├── compare_ocr.py
├── document_photo.jpg
├── requirements.txt
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or newer
- Tesseract OCR
- Git
- Visual Studio Code (recommended)

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sravanibandreddy/ai-document-scanner.git
cd ai-document-scanner
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install Tesseract OCR

Install Tesseract OCR on your computer. On Windows, the executable is commonly located at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Make sure the path configured in your Python application matches your installation.

### 5. Run the application

```bash
python -m uvicorn app:app --reload
```

Open the following URL in your browser:

http://127.0.0.1:8000

## How to Use

1. Start the application.
2. Upload a document image.
3. Scan the document and extract its text.
4. Review the extracted information.
5. Download the extracted text.
6. Visit `/history` to view previously saved scans.

## Database

The application uses SQLite to store scan history, extracted text, and detected information. The database file is created locally when the application initializes.

## Future Enhancements

- Support PDF documents.
- Improve OCR accuracy for different languages.
- Add user authentication and access control.
- Export extracted information to PDF or Excel.
- Deploy the application online.
- Develop a mobile-friendly or installable app interface.

## Author

**Sravani Bandreddy**

GitHub: https://github.com/sravanibandreddy

## License

This project is available for educational and portfolio purposes. Add an open-source license if you wish to formally permit reuse and redistribution.