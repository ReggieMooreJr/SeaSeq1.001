"""
BOOK: SEA-SEC Gospel of API

CHAPTER 1: Purpose
  V1  This file is the "front door" to SEA-SEC. It starts a small web server.
  V2  Other programs or scripts call this server to run a site scan.
  V3  Think: "Doorbell" that triggers a scan and saves a report.

CHAPTER 2: Big Picture
  V1  /health  -> quick check the app is alive.
  V2  /run     -> crawl site, run checks, save report, optional screenshots.

CHAPTER 3: How to Read
  V1  Each import = a helper scroll.
  V2  Each function = a verse you can call.
"""

from fastapi import FastAPI
from app.services.db import migrate_once, pool
from app.models.schemas import RunRequest
from app.services.crawl import crawl
from app.services.rate_guard import detect_rate_abuse
from app.services.vuln_scan import scan_headers
from app.services.report import save_run

app = FastAPI(title="SEA-SEC API")

# CHAPTER 4: Startup prayers
# V1  Run simple migrations so tables exist even on a fresh machine.
@app.on_event("startup")
def _startup():
    migrate_once()

# CHAPTER 5: Health check
# V1  Quick heartbeat to see if DB and API are awake.
@app.get("/health")
def health():
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1;")
        cur.fetchone()
    return {"ok": True}

# CHAPTER 6: Main run endpoint
# V1  Inputs: a URL and an optional "capture screenshots" flag.
# V2  Steps: crawl -> checks -> tier + pass/fail -> save -> optional screenshots.
# V3  Output: a small summary for the caller.
@app.post("/run")
async def run(req: RunRequest):
    # Verse 1: Crawl the website starting at the requested URL.
    pages = crawl(str(req.url))

    # Verse 2: Prepare header objects for the simple header scan.
    pages_for_headers = [{"url": p["url"], "headers": {}} for p in pages]

    # Verse 3: Run security checks.
    f_rate = detect_rate_abuse(pages)         # looks for heavy use patterns
    f_hdrs = scan_headers(pages_for_headers)  # looks for missing safe headers
    findings = f_rate + f_hdrs

    # Verse 4: Turn raw results into a report with pass/fail and tier.
    result = save_run(str(req.url), pages, findings)

    # Verse 5: Optional screenshots through MCP Chrome server.
    if req.capture:
        try:
            from app.services.mcp_capture import capture
            await capture([p["url"] for p in pages[:10]])  # small sample
        except Exception:
            # We keep the test results even if screenshots fail.
            pass

    # Verse 6: Return a simple summary to the caller.
    return result
