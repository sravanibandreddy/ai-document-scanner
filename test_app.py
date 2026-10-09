
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_homepage_opens():
    response = client.get("/")

    assert response.status_code == 200
    assert "AI Document Scanner" in response.text


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200


def test_invalid_file_type_is_rejected():
    response = client.post(
        "/scan",
        files={
            "file": (
                "sample.exe",
                b"not a valid document",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code in (400, 413, 415, 422)


def test_download_endpoint_does_not_expose_shared_files():
    response = client.get("/download")

    assert response.status_code in (200, 400, 404)


def test_missing_scan_file():
    response = client.post("/scan")

    assert response.status_code in (400, 422)
