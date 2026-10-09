from pathlib import Path
import io
import html

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse

from document_scanner import scan_document
from preprocessing import preprocess_image
from smart_extraction import extract_information
from database import init_db, save_scan, get_all_scans, get_scan_by_id


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

# Update this path only if Tesseract is installed somewhere else.
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

app = FastAPI(title="AI Document Scanner")
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEXT_FILE = UPLOAD_DIR / "extracted_text.txt"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

# Create the SQLite database/table when the app starts.
init_db()


# --------------------------------------------------
# HTML PAGE
# --------------------------------------------------

def make_page(result="", error="", information=None, scan_id=None):
    safe_result = html.escape(result or "")
    safe_error = html.escape(error or "")
    error_html = f'<div class="error">{safe_error}</div>' if safe_error else ""
    result_html = ""

    if result or information is not None:
        info_html = ""
        if information is not None:
            info_rows = []
            for label, values in information.items():
                if isinstance(values, (list, tuple, set)):
                    display = ", ".join(str(value) for value in values)
                else:
                    display = str(values) if values else ""
                safe_label = html.escape(str(label).replace("_", " ").title())
                safe_values = html.escape(display or "None found")
                info_rows.append(
                    f'<div class="info-item"><strong>{safe_label}</strong>'
                    f'<span>{safe_values}</span></div>'
                )
            info_html = (
                '<section class="info-panel"><span class="eyebrow">AUTOMATIC ANALYSIS</span>'
                '<h3>Smart Information Extraction</h3>'
                '<p class="muted">Contact information and dates identified in your document.</p>'
                + "".join(info_rows) + "</section>"
            )

        safe_id_html = (
            f'<p class="muted">Saved to database as scan #{int(scan_id)}.</p>'
            if scan_id is not None else ""
        )
        result_html = f"""
        <section class="card" id="results">
          <div class="section-heading"><div><span class="eyebrow">SCAN RESULTS</span><h2>Extracted Text</h2></div><span class="status">Processed</span></div>
          <textarea id="resultText" readonly>{safe_result or 'No text detected. Please try a clearer image.'}</textarea>
          <div class="actions"><button type="button" onclick="copyText()">Copy Text</button><a class="button-link" href="/download">Download TXT</a></div>
          <p id="copyMessage" class="muted" aria-live="polite"></p>
          {safe_id_html}
          {info_html}
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Document Scanner</title>
<style>
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family: "Segoe UI", Arial, sans-serif; background:#f3f6fc; color:#172033; line-height:1.6; }}
header {{ padding:44px 20px 64px; text-align:center; color:white; background:linear-gradient(135deg,#10264f,#2563eb); }}
.brand {{ color:#bfdbfe; font-size:12px; font-weight:800; letter-spacing:2px; text-transform:uppercase; }}
header h1 {{ margin:12px 0; font-size:clamp(30px,5vw,46px); line-height:1.2; }}
header p {{ max-width:620px; margin:12px auto; color:#dbeafe; }}
nav a {{ color:white; margin:0 8px; font-weight:600; }}
main {{ width:min(900px,100%); margin:-30px auto 35px; padding:0 18px; }}
.card {{ margin-bottom:22px; padding:28px; background:white; border:1px solid #e2e8f0; border-radius:18px; box-shadow:0 12px 35px rgba(15,23,42,.07); }}
.eyebrow {{ color:#2563eb; font-size:11px; font-weight:800; letter-spacing:1.5px; }}
h2 {{ margin:5px 0 8px; font-size:25px; }} h3 {{ margin:8px 0; font-size:20px; }}
.muted {{ color:#64748b; font-size:14px; }}
.upload-area {{ margin:22px 0; padding:28px 18px; text-align:center; background:#f8faff; border:2px dashed #93b4f7; border-radius:14px; }}
.upload-area.dragover {{ background:#eaf2ff; border-color:#2563eb; }}
.upload-icon {{ font-size:38px; margin-bottom:8px; }}
input[type=file] {{ display:block; width:100%; margin-top:16px; padding:12px; background:white; border:1px solid #dbe3ef; border-radius:9px; }}
button,.button-link {{ display:inline-block; padding:12px 20px; border:0; border-radius:9px; background:#2563eb; color:white; font:inherit; font-weight:650; text-decoration:none; cursor:pointer; }}
button:hover,.button-link:hover {{ background:#1d4ed8; }} button:disabled {{ opacity:.7; cursor:wait; }}
.preview-container {{ display:none; margin-top:22px; padding:15px; background:white; border:1px solid #dbe3ef; border-radius:12px; }}
.preview-image {{ display:block; max-width:100%; max-height:380px; margin:12px auto 0; object-fit:contain; border-radius:8px; }}
.section-heading {{ display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:18px; }}
.status {{ padding:5px 10px; border-radius:20px; background:#dcfce7; color:#166534; font-size:12px; font-weight:700; }}
textarea {{ display:block; width:100%; min-height:240px; padding:16px; border:1px solid #dbe3ef; border-radius:10px; background:#fbfdff; color:#1e293b; font:15px/1.7 Consolas,monospace; resize:vertical; }}
.actions {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:14px; }}
.info-panel {{ margin-top:28px; padding-top:22px; border-top:1px solid #e2e8f0; }}
.info-item {{ display:flex; justify-content:space-between; gap:16px; padding:13px 0; border-bottom:1px solid #edf2f7; overflow-wrap:anywhere; }}
.info-item strong {{ color:#334155; }} .info-item span {{ text-align:right; color:#475569; }}
.error {{ margin-bottom:20px; padding:14px 16px; border:1px solid #fecaca; border-radius:10px; background:#fef2f2; color:#991b1b; overflow-wrap:anywhere; }}
footer {{ padding:10px 20px 30px; text-align:center; color:#64748b; font-size:13px; }}
@media(max-width:520px) {{ .card {{ padding:20px; }} header {{ padding:38px 16px 52px; }} .info-item {{ flex-direction:column; gap:2px; }} .info-item span {{ text-align:left; }} .actions>* {{ flex:1; text-align:center; }} }}
</style></head>
<body>
<header><div class="brand">AI Powered Tool</div><h1>AI Document Scanner</h1><p>Scan, straighten, and extract text from documents with OCR and smart information extraction.</p><nav><a href="/">Scanner</a><a href="/history">Scan History</a></nav></header>
<main>{error_html}
<section class="card"><span class="eyebrow">DOCUMENT PROCESSING</span><h2>Upload Your Document</h2><p class="muted">Choose an image or drag it into the upload area. Preview it before scanning.</p>
<form id="uploadForm" action="/scan" method="post" enctype="multipart/form-data"><div class="upload-area" id="uploadArea"><div class="upload-icon">&#128196;</div><strong>Choose or drop your document image</strong><p class="muted">Supported formats: PNG, JPG, JPEG, TIFF, BMP</p>
<input type="file" id="documentFile" name="file" accept=".png,.jpg,.jpeg,.tif,.tiff,.bmp" required>
<div class="preview-container" id="previewContainer"><strong>Document Preview</strong><img id="documentPreview" class="preview-image" alt="Preview of selected document"><p id="fileName" class="muted"></p></div></div>
<button type="submit" id="scanButton">Scan Document</button><p class="muted" id="uploadMessage" aria-live="polite"></p></form></section>
{result_html}
</main><footer>AI Document Scanner | Computer Vision | OCR | SQLite Database</footer>
<script>
const fileInput=document.getElementById('documentFile'); const uploadArea=document.getElementById('uploadArea');
const previewContainer=document.getElementById('previewContainer'); const previewImage=document.getElementById('documentPreview');
const fileName=document.getElementById('fileName'); const uploadForm=document.getElementById('uploadForm');
const scanButton=document.getElementById('scanButton'); const uploadMessage=document.getElementById('uploadMessage'); let currentPreviewUrl=null;
function previewDocument(file) {{ if(!file)return; const allowed=['.png','.jpg','.jpeg','.tif','.tiff','.bmp']; const ext='.'+file.name.split('.').pop().toLowerCase();
if(!allowed.includes(ext)){{alert('Please select a supported image file.');fileInput.value='';previewContainer.style.display='none';return;}}
if(currentPreviewUrl){{URL.revokeObjectURL(currentPreviewUrl);currentPreviewUrl=null;}} fileName.textContent=file.name; uploadMessage.textContent='';
if(ext==='.tif'||ext==='.tiff'){{previewImage.removeAttribute('src');previewImage.alt='TIFF preview may not be supported by your browser';previewContainer.style.display='block';fileName.textContent=file.name+' (browser preview may not be supported)';return;}}
currentPreviewUrl=URL.createObjectURL(file);previewImage.src=currentPreviewUrl;previewImage.alt='Preview of '+file.name;previewContainer.style.display='block';}}
fileInput.addEventListener('change',function(){{if(this.files&&this.files.length)previewDocument(this.files[0]);}});
uploadArea.addEventListener('dragover',function(e){{e.preventDefault();uploadArea.classList.add('dragover');}});
uploadArea.addEventListener('dragleave',function(){{uploadArea.classList.remove('dragover');}});
uploadArea.addEventListener('drop',function(e){{e.preventDefault();uploadArea.classList.remove('dragover');const files=e.dataTransfer.files;if(files&&files.length){{try{{const transfer=new DataTransfer();transfer.items.add(files[0]);fileInput.files=transfer.files;previewDocument(files[0]);}}catch(err){{alert('Please use Choose File to select your image.');}}}}}});
uploadForm.addEventListener('submit',function(e){{if(!fileInput.files||!fileInput.files.length){{e.preventDefault();alert('Please select a document image first.');return;}}scanButton.disabled=true;scanButton.textContent='Scanning...';uploadMessage.textContent='Please wait while your document is processed.';}});
async function copyText(){{const box=document.getElementById('resultText');const msg=document.getElementById('copyMessage');if(!box)return;try{{await navigator.clipboard.writeText(box.value);msg.textContent='Text copied successfully.';}}catch(err){{box.focus();box.select();const copied=document.execCommand('copy');msg.textContent=copied?'Text copied successfully.':'Select the text and copy it manually.';}}}}
</script></body></html>"""


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return make_page()


# --------------------------------------------------
# SCAN DOCUMENT AND SAVE TO DATABASE
# --------------------------------------------------

@app.post("/scan", response_class=HTMLResponse)
async def scan_document_route(file: UploadFile = File(...)):
    filename = Path(file.filename or "document").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        await file.close()
        return HTMLResponse(
            make_page(error="Please upload a PNG, JPG, JPEG, TIFF, or BMP image."),
            status_code=400,
        )

    try:
        contents = await file.read()
        if not contents:
            return HTMLResponse(make_page(error="The uploaded file is empty."), status_code=400)

        try:
            with Image.open(io.BytesIO(contents)) as opened_image:
                pil_image = ImageOps.exif_transpose(opened_image).convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("The uploaded file is not a valid readable image.") from exc

        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(UPLOAD_DIR / "debug_original.png"), image)

        scanned_image = scan_document(image)
        if scanned_image is None or scanned_image.size == 0:
            raise ValueError("Document scanning returned an empty image.")
        cv2.imwrite(str(UPLOAD_DIR / "scanned_latest.png"), scanned_image)

        direct_text = pytesseract.image_to_string(scanned_image, config="--oem 3 --psm 6")
        processed_image = preprocess_image(scanned_image)
        if processed_image is None or processed_image.size == 0:
            raise ValueError("Image preprocessing returned an empty image.")
        cv2.imwrite(str(UPLOAD_DIR / "processed_latest.png"), processed_image)
        processed_text = pytesseract.image_to_string(processed_image, config="--oem 3 --psm 6")

        print("DEBUG - Direct OCR:", repr(direct_text))
        print("DEBUG - Processed OCR:", repr(processed_text))

        chosen_text = max((direct_text, processed_text), key=lambda value: len(value.strip()))
        cleaned_text = "\n".join(line.strip() for line in chosen_text.splitlines() if line.strip())
        if not cleaned_text:
            cleaned_text = "No text was detected. Try a clearer, well-lit image."

        TEXT_FILE.write_text(cleaned_text, encoding="utf-8")
        information = extract_information(cleaned_text)
        print("DEBUG - Extracted information:", information)

        # Save filename, OCR text, emails, phone numbers, dates and timestamp in SQLite.
        scan_id = save_scan(filename, cleaned_text, information)
        print("Saved scan ID:", scan_id)

        return make_page(result=cleaned_text, information=information, scan_id=scan_id)

    except pytesseract.TesseractNotFoundError:
        print("SCAN ERROR: Tesseract executable was not found at", TESSERACT_PATH)
        return HTMLResponse(
            make_page(error="Tesseract OCR was not found. Check TESSERACT_PATH near the top of app.py."),
            status_code=500,
        )
    except Exception as exc:
        print("SCAN ERROR:", repr(exc))
        return HTMLResponse(
            make_page(error="Could not scan the image. Check the VS Code terminal for the detailed error."),
            status_code=400,
        )
    finally:
        await file.close()


# --------------------------------------------------
# DOWNLOAD MOST RECENT EXTRACTED TEXT
# --------------------------------------------------

@app.get("/download")
async def download_text():
    if not TEXT_FILE.exists():
        return PlainTextResponse("No extracted text is available yet. Scan a document first.", status_code=404)
    return FileResponse(path=TEXT_FILE, media_type="text/plain", filename="extracted_text.txt")


# --------------------------------------------------
# VIEW SCAN HISTORY
# --------------------------------------------------

@app.get("/history", response_class=HTMLResponse)
async def scan_history():
    scans = get_all_scans()
    if scans:
        rows = "".join(
            "<tr>"
            f"<td>{scan['id']}</td>"
            f"<td>{html.escape(scan['filename'])}</td>"
            f"<td>{html.escape(scan['created_at'] or '')}</td>"
            f"<td><a href='/history/{scan['id']}'>View Result</a></td>"
            "</tr>"
            for scan in scans
        )
    else:
        rows = "<tr><td colspan='4'>No scans saved yet. Scan a document first.</td></tr>"

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Scan History</title>
<style>body{{font-family:Arial,sans-serif;background:#f3f6fc;color:#172033;margin:0;padding:25px}}main{{max-width:1000px;margin:20px auto;padding:25px;background:white;border-radius:14px;box-shadow:0 5px 20px #0000000d}}h1{{color:#1d4ed8}}.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;margin-top:20px}}th,td{{padding:12px;border-bottom:1px solid #e2e8f0;text-align:left}}th{{background:#eff6ff}}a{{color:#2563eb;text-decoration:none}}.back{{display:inline-block;margin-top:20px}}</style></head>
<body><main><h1>Document Scan History</h1><p>Previously scanned documents saved in your SQLite database.</p>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Filename</th><th>Scan Time (UTC)</th><th>Action</th></tr></thead><tbody>{rows}</tbody></table></div>
<a class="back" href="/">Back to Scanner</a></main></body></html>"""


# --------------------------------------------------
# VIEW ONE SAVED SCAN
# --------------------------------------------------

@app.get("/history/{scan_id}", response_class=HTMLResponse)
async def view_saved_scan(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if scan is None:
        return HTMLResponse("<h1>Scan not found</h1><a href='/history'>Back to history</a>", status_code=404)

    filename = html.escape(scan["filename"])
    created_at = html.escape(scan["created_at"] or "")
    extracted_text = html.escape(scan["extracted_text"])

    def display_values(values):
        if not values:
            return "None found"
        return ", ".join(html.escape(str(value)) for value in values)

    emails = display_values(scan["emails"])
    phones = display_values(scan["phone_numbers"])
    dates = display_values(scan["dates"])

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Saved Scan Result</title>
<style>body{{font-family:Arial,sans-serif;background:#f3f6fc;color:#172033;margin:0;padding:25px}}main{{max-width:850px;margin:20px auto;padding:25px;background:white;border-radius:14px}}textarea{{width:100%;min-height:250px;padding:12px;box-sizing:border-box;font:14px/1.6 Consolas,monospace}}.info{{padding:12px 0;border-bottom:1px solid #e2e8f0;overflow-wrap:anywhere}}a{{color:#2563eb}}</style></head>
<body><main><h1>Saved Scan Result</h1><p><strong>Filename:</strong> {filename}</p><p><strong>Scanned at (UTC):</strong> {created_at}</p>
<h2>Extracted Text</h2><textarea readonly>{extracted_text}</textarea><h2>Smart Information Extraction</h2>
<div class="info"><strong>Emails:</strong> {emails}</div><div class="info"><strong>Phone Numbers:</strong> {phones}</div><div class="info"><strong>Dates:</strong> {dates}</div>
<p><a href="/history">Back to Scan History</a></p><p><a href="/">Back to Scanner</a></p></main></body></html>"""
