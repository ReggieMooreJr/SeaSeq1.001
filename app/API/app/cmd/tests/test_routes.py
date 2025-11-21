import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Use TestClient to simulate requests
client = TestClient(app)

# Test constants
API_KEY = os.getenv("API_KEY", "changeme")
HEADERS = {"X-API-Key": API_KEY}


# ------------------------
# /health endpoint
# ------------------------
def test_health_check_creates_reports(tmp_path, monkeypatch):
    """Ensure /health works and generates sample reports if missing."""
    # Override reports directory to tmp_path
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))

    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "target_site" in data

    # Check files were created
    report_csv = tmp_path / "report.csv"
    report_html = tmp_path / "report.html"
    report_json = tmp_path / "report.json"
    assert report_csv.exists()
    assert report_html.exists()
    assert report_json.exists()


# ------------------------
# /set_site endpoint
# ------------------------
def test_set_site_with_valid_url():
    """Ensure /set_site sets the target site with valid URL."""
    payload = {"url": "https://mlbam-park.b12sites.com"}
    response = client.post("/api/set_site", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["target_site"] == "https://mlbam-park.b12sites.com"


def test_set_site_without_url():
    """Ensure /set_site returns 422 if URL is missing/invalid."""
    payload = {}  # no url
    response = client.post("/api/set_site", json=payload, headers=HEADERS)
    assert response.status_code in (400, 422)


# ------------------------
# /report/latest/... endpoints
# ------------------------
@pytest.mark.parametrize("endpoint, filename", [
    ("/api/report/latest/csv", "report.csv"),
    ("/api/report/latest/html", "report.html"),
    ("/api/report/latest/json", "report.json"),
])
def test_report_endpoints_generate_files(tmp_path, monkeypatch, endpoint, filename):
    """Ensure report endpoints auto-generate files if missing."""
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))

    response = client.get(endpoint, headers=HEADERS)
    assert response.status_code == 200

    file_path = tmp_path / filename
    assert file_path.exists()
    assert file_path.stat().st_size > 0
