"""
BOOK: SEA-SEC Epistle of Email

CHAPTER 1: Purpose
  V1  Grab the newest run from Postgres.
  V2  Turn it into a readable text.
  V3  Send it by email using SMTP (the internet's mailman rules).
"""

import os, ssl, smtplib
from email.message import EmailMessage
from psycopg_pool import ConnectionPool

DB_URL   = os.getenv("DATABASE_URL")
SMTP_HOST= os.getenv("SMTP_HOST")
SMTP_PORT= int(os.getenv("SMTP_PORT", "587"))
SMTP_USER= os.getenv("SMTP_USER")
SMTP_PASS= os.getenv("SMTP_PASS")
SMTP_FROM= os.getenv("SMTP_FROM", "SEA-SEC Reports <no-reply@example.com>")
REPORT_TO= os.getenv("REPORT_TO_EMAIL", "mikodad@icloud.com")

if not all([DB_URL, SMTP_HOST, SMTP_USER, SMTP_PASS, REPORT_TO]):
    raise SystemExit("Missing .env settings for DB or email.")

pool = ConnectionPool(DB_URL, min_size=1, max_size=2, kwargs={"autocommit": True})

def fetch_latest():
    # CHAPTER 2: Read last run and its findings
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute("""
          SELECT run_id, started_at, target_url, pass, overall_tier, totals
          FROM run_reports ORDER BY started_at DESC LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            return None
        run = {
            "run_id": str(row[0]),
            "started_at": row[1],
            "target_url": row[2],
            "passed": bool(row[3]),
            "overall_tier": int(row[4]),
            "totals": row[5] or {},
        }
        cur.execute("""
          SELECT category, severity, tier, detail
FROM findings WHERE run_id=%s
          ORDER BY severity DESC, category ASC
        """,(run["run_id"],))
        run["findings"] = [
            {"category": r[0], "severity": int(r[1]), "tier": int(r[2]), "detail": r[3]}
            for r in cur.fetchall()
        ]
        return run

def format_body(run):
    # CHAPTER 3: Simple text email
    lines = [
        "SEA-SEC Run Report",
        f"Run ID: {run['run_id']}",
        f"Target: {run['target_url']}",
        f"Started: {run['started_at']}",
        f"Passed: {'YES' if run['passed'] else 'NO'}",
        f"Overall Tier: {run['overall_tier']}",
        f"Pages: {run['totals'].get('pages','?')}, Findings: {run['totals'].get('findings','?')}",
        "",
        "Findings:"
    ]
    if not run["findings"]:
        lines.append("  None")
    else:
        for f in run["findings"]:
            lines.append(f"  - {f['category']} | sev {f['severity']} | tier {f['tier']} | {(f.get('detail') or {}).get('url','')}")
    return "\n".join(lines)

def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = REPORT_TO
    msg["Subject"] = subject
    msg.set_content(body)
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(context=ctx)
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

def main():
    run = fetch_latest()
    if not run:
        raise SystemExit("No run in database.")
    body = format_body(run)
    subject = f"SEA-SEC Report | {run['target_url']} | Tier {run['overall_tier']} | {'PASS' if run['passed'] else 'FAIL'}"
    send_email(subject, body)
    print("Report sent to", REPORT_TO)

if __name__ == "__main__":
    main()

