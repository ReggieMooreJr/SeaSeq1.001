"""
BOOK: SEA-SEC Letters of Report

CHAPTER 1: Purpose
  V1  Convert raw findings into a decision we can read later.
  V2  Store it so we can learn over time.

CHAPTER 2: Tiers
  V1  Tier 3 = high risk (PHI or crypto or severity ≥ 3).
  V2  Tier 2 = medium risk.
  V3  Tier 1 = low risk.
  V4  Pass if overall tier ≤ 1. Fail otherwise.
"""

from uuid import uuid4
from datetime import datetime
from .db import pool

def tier_for(f):
    # CHAPTER 3: Simple tier map
    if f["category"] in ("phi", "crypto"):
        return 3
    if f["severity"] >= 3:
        return 3
    if f["severity"] == 2:
        return 2
    return 1

def save_run(target_url, pages, extra_findings):
    """
    CHAPTER 4: Save the Story
      V1  Make a run id.
      V2  Merge findings.
      V3  Detect simple PHI/crypto paths.
      V4  Compute tier and pass/fail.
      V5  Insert run and findings into Postgres.
    """
    run_id = uuid4()
    started = datetime.utcnow()

    findings = list(extra_findings)

    # Verse: quick tag by path names
    for p in pages:
        u = p["url"].lower()
        if any(k in u for k in ("/patient", "/phi", "/ssn")):
            findings.append({"category": "phi", "severity": 3, "detail": {"url": p["url"]}})
        if any(k in u for k in ("/wallet", "/crypto", "/payments")):
            findings.append({"category": "crypto", "severity": 2, "detail": {"url": p["url"]}})

    for f in findings:
        f["tier"] = tier_for(f)

    overall_tier = max((f["tier"] for f in findings), default=1)
    passed = overall_tier <= 1

    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO run_reports (run_id, started_at, target_url, pass, overall_tier, totals, notes) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                str(run_id), started, target_url, passed, overall_tier,
                {"pages": len(pages), "findings": len(findings)}, None,
            ),
        )
        for f in findings:
            cur.execute(
                "INSERT INTO findings (run_id, url, ip, category, severity, tier, detail) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (str(run_id), f.get("detail", {}).get("url"), None, f["category"], f["severity"], f["tier"], f["detail"]),
            )

    return {"run_id": str(run_id), "pass": passed, "overall_tier": overall_tier, "pages": len(pages), "findings": len(findings)}
