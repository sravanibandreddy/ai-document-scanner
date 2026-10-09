
from io import BytesIO

from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def make_sample_image():
    image = Image.new("RGB", (900, 300), "white")
    draw = ImageDraw.Draw(image)
    draw.text((30, 100), "INVOICE TEST 12345", fill="black")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_png_upload_is_processed():
    response = client.post(
        "/scan",
        files={
            "file": (
                "sample.png",
                make_sample_image(),
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    assert "INVOICE" in response.text.upper()


def test_unsupported_extension_is_rejected():
    response = client.post(
        "/scan",
        files={
            "file": (
                "sample.exe",
                b"not an image",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code in (400, 413, 415, 422)
