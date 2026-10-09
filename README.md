# AI Document Scanner

An AI-powered document scanning application built with FastAPI, OpenCV, Pillow, and Tesseract OCR. Upload supported documents, extract text, and identify useful information such as email addresses, phone numbers, and dates.

## Features

- Upload and process supported document formats.
- Extract text using OCR for images.
- Preprocess images to improve text recognition.
- Extract emails, phone numbers, and dates.
- Identify document types using smart classification.
- View and download extracted text.
- Store scan information locally using SQLite, if enabled in the application.

## Technology Stack

- **Backend:** Python, FastAPI
- **Image processing:** OpenCV, Pillow, NumPy
- **OCR:** Tesseract OCR, pytesseract
- **Document processing:** PyMuPDF, python-docx, openpyxl, xlrd
- **Database:** SQLite
- **Testing:** pytest

## Requirements

- Python 3.10 or newer
- Tesseract OCR installed on your system
- Git
- Visual Studio Code (recommended)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sravanibandreddy/ai-document-scanner.git
cd ai-document-scanner
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Install Tesseract OCR

Install the Tesseract OCR engine separately. On Windows, the executable is commonly located at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Tesseract is not on your system PATH, configure its executable location in the application.

Verify the installation:

```powershell
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

### 5. Start the application

```powershell
python -m uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## How to Use

1. Start the application.
2. Open the local website.
3. Upload a supported document.
4. Start scanning and wait for processing to finish.
5. Review the extracted text and detected information.
6. Copy or download the results if the corresponding controls are available.

## Run Automated Tests

Run the test suite with:

```powershell
python -m pytest -v
```

The current test suite checks the homepage, health endpoint, unsupported file types, download behavior, missing files, and image uploads.

## Database and Privacy

The application may use a local SQLite database for scan-related information. Do not commit databases containing personal or confidential documents to GitHub.

## Limitations

- OCR accuracy depends on image quality, orientation, language, and document layout.
- Tesseract OCR must be installed separately from the Python dependencies.
- Supported file formats and application features depend on the current implementation.
- This project should undergo additional security testing before being exposed to public users.

## Future Enhancements

- Improve OCR accuracy and multilingual support.
- Add authentication and access controls.
- Expand export options.
- Improve document classification and extraction.
- Deploy the application with appropriate upload limits and security protections.

## Author

**Sravani Bandreddy**

GitHub: https://github.com/sravanibandreddy

## License

This project is intended for educational and portfolio use. No formal open-source license is specified yet.