
import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app
from backend.auth.auth_routes import create_access_token
import backend.routes as routes


client = TestClient(app)


# Generate authentication headers for protected API tests
def authenticated_headers():
    token = create_access_token("ci-test@example.com")

    return {
        "Authorization": f"Bearer {token}"
    }


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "Healthy"


def test_upload_invalid_file():
    response = client.post(
        "/upload",
        files={"file": ("sample.txt", b"Hello", "text/plain")},
        headers=authenticated_headers()
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only CSV files are allowed"


def test_upload_empty_file():
    response = client.post(
        "/upload",
        files={"file": ("sample.csv", b"", "text/csv")},
        headers=authenticated_headers()
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty"


def test_upload_valid_csv(monkeypatch):
    monkeypatch.setattr(
        routes,
        "read_csv_file",
        lambda content: pd.DataFrame({"Name": ["A", "B"]})
    )

    monkeypatch.setattr(
        routes,
        "save_uploaded_file",
        lambda file_id, content: "storage/uploads/sample.csv"
    )

    monkeypatch.setattr(
        routes,
        "add_dataset",
        lambda *args: None
    )

    response = client.post(
        "/upload",
        files={"file": ("sample.csv", b"Name\nA\nB", "text/csv")},
        headers=authenticated_headers()
    )

    assert response.status_code == 200
    assert response.json()["message"] == "CSV uploaded successfully"
    assert response.json()["rows"] == 2


def test_get_dataset(monkeypatch):
    monkeypatch.setattr(
        routes,
        "get_dataset",
        lambda file_id: {
            "file_id": file_id,
            "filename": "sample.csv"
        }
    )

    response = client.get(
        "/dataset/test123",
        headers=authenticated_headers()
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "sample.csv"


def test_upload_history(monkeypatch):
    monkeypatch.setattr(
        routes,
        "get_history",
        lambda: [{"filename": "sample.csv"}]
    )

    response = client.get(
        "/history",
        headers=authenticated_headers()
    )

    assert response.status_code == 200
    assert len(response.json()["history"]) == 1
