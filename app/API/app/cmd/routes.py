from fastapi import APIRouter, Body, HTTPException, Depends, Security
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, HttpUrl
import os, csv
from datetime import datetime

# Import services
from app.services.data_service import crawl_site, load_events, set_target_site, get_target_site
from app.services.learning_service import train, score
from app.services.reporting_service import generate

# Import Pydantic models
from app.models import TrainResult, ReportSummary  # adjust import if TrainResult lives elsewhere

# -------------------------------------------------
# Setup
# -------------------------------------------------
router = APIRouter()
reports_dir = Path("data/reports/latest")
reports_dir.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# Security (API Key demo)
# -------------------------------------------------
API_KEY = os.getenv("API_KEY", "changeme")

def verify_api_key(x_api_key: str = Security(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

# -------------------------------------------------
# Pydantic Models for Input
# -------------------------------------------------
class SitePayload(BaseModel):
    url: HttpUrl

class IngestPayload(BaseModel):
    max_pages: int = 15

# -------------------------------------------------
# Routes
# -------------------------------------------------

@router.get("/")
def root():
    return {"ok": True, "target_site": get_target_site()}

# 1. Set Target Site
@router.post("/set_site", dependencies=[Depends(verify_api_key)])
def api_set_site(payload: SitePayload):
    return {"target_site": set_target_site(str(payload.url))}

# 2. Crawl / Ingest Pages
@router.post("/ingest/run", dependencies=[Depends(verify_api_key)])
def api_ingest(payload: IngestPayload):
    if not (1 <= payload.max_pages <= 500):
        raise HTTPException(status_code=400, detail="max_pages must be between 1 and 500")
    events = crawl_site(max_pages=payload.max_pages)
    return {"collected": len(events), "target_site": get_target_site()}

# 3. Train Model
@router.post("/learn/train", response_model=TrainResult, dependencies=[Depends(verify_api_key)])
def api_train():
    events = load_events()
    return train(events)

# 4. Generate Risk Report
@router.post("/report/generate", response_model=ReportSummary, dependencies=[Depends(verify_api_key)])
def api_report():
    events = load_events()
    risks = score(events)
    return generate(events, risks)

# 5. Download Reports
def ensure_sample_reports():
    """Helper to auto-generate sample CSV/HTML if missing."""
    today = datetime.now().strftime("%B %d, %Y")
    month_year = datetime.now().strftime("%B %Y")

    csv_path = reports_dir / "report.csv"
    html_path = reports_dir / "report.html"
    json_path = reports_dir / "report.json"

    if not csv_path.exists():
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Risk Level", "Issue Summary", "Business Impact", "Action Required"])
            writer.writerow(["Critical", "Unprotected Customer Data",
                             "Data privacy breach, penalties, brand damage",
                             "Block access point and notify security team"])
            writer.writerow(["High", "Vulnerable Login System",
                             "Potential account takeovers",
                             "Update login system"])
            writer.writerow(["Medium", "Outdated Website Software",
                             "Minor gaps could be exploited",
                             "Schedule CMS update in 30-60 days"])
            writer.writerow(["Low", "Missing Security Headers",
                             "Increases risk of client-side attacks",
                             "Configure headers during maintenance"])
    if not html_path.exists():
        html_content = f"""<!DOCTYPE html>
<html><head><title>Website Security Report - {month_year}</title></head>
<body>
  <h1>Website Security Report - {month_year}</h1>
  <p>Report Date: {today} | Target: {get_target_site() or "No site set"}</p>
  <p>This is a sample HTML report for healthcheck/demo.</p>
</body></html>"""
        html_path.write_text(html_content)
    if not json_path.exists():
        json_path.write_text('[{"sample":"report"}]')

@router.get("/report/latest/html", dependencies=[Depends(verify_api_key)])
def api_report_html():
    ensure_sample_reports()
    return FileResponse(reports_dir / "report.html")

@router.get("/report/latest/csv", dependencies=[Depends(verify_api_key)])
def api_report_csv():
    ensure_sample_reports()
    return FileResponse(reports_dir / "report.csv")

@router.get("/report/latest/json", dependencies=[Depends(verify_api_key)])
def api_report_json():
    ensure_sample_reports()
    return FileResponse(reports_dir / "report.json")

# 6. Health endpoint (always open, no API key required)
@router.get("/health")
def health_check():
    ensure_sample_reports()
    return {"status": "ok", "target_site": get_target_site()}
