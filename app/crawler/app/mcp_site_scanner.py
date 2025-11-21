#!/usr/bin/env python3
"""
mcp_site_scanner.py

Minimal MCP-friendly HTTP tool that:
 - exposes two JSON endpoints for MCP/agent calls:
    POST /mcp/scrape    -> run link checks + form detection on target URL
    POST /mcp/add_member -> attempt to submit a detected "add member" form (or a user-specified form)
 - writes an HTML report to ./reports/report.html (uses report_template.html if present)
 - optional: send the report over SMTP (configure via env or YAML)
 
Dependencies:
  pip install requests beautifulsoup4 PyYAML flask lxml

Note: This is a *tool* server (not a full production MCP implementation). MCP clients
can call the endpoints to run scans. The JSON API is intentionally simple.
"""

import os
import re
import json
import socket
import uuid
import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory
import yaml

# Config defaults
OUT_DIR = os.environ.get("OUT_DIR", "reports")
REPORT_FILE = os.path.join(OUT_DIR, "report.html")
TEMPLATE_FILE = "report_template.html"  # optional template in working dir
DEFAULT_USER_AGENT = "MCP-Site-Scanner/1.0 (+https://example.com)"
TIMEOUT = 10  # seconds for requests

app = Flask(__name__)

# helper functions ----------------------------------------------------------

def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def fetch_url(url, method="GET", headers=None, allow_redirects=True, data=None):
    headers = headers or {}
    headers.setdefault("User-Agent", DEFAULT_USER_AGENT)
    try:
        resp = requests.request(method, url, headers=headers, timeout=TIMEOUT, allow_redirects=allow_redirects, data=data)
        return resp
    except Exception as e:
        return e

def same_origin(a, b):
    pa = urlparse(a)
    pb = urlparse(b)
    return (pa.scheme, pa.netloc) == (pb.scheme, pb.netloc)

def extract_links(base_url, html_text):
    soup = BeautifulSoup(html_text, "lxml")
    links = []
    for tag, attr in (("a", "href"), ("link", "href"), ("img", "src"), ("script", "src")):
        for node in soup.find_all(tag):
            url = node.get(attr)
            if not url:
                continue
            full = urljoin(base_url, url)
            links.append({"tag": tag, "raw": url, "url": full})
    # deduplicate while preserving order
    seen = set()
    dedup = []
    for l in links:
        if l["url"] not in seen:
            dedup.append(l)
            seen.add(l["url"])
    return dedup

def find_possible_member_forms(base_url, html_text):
    """Try to heuristically detect forms that look like 'add member' or 'signup' or 'invite' forms."""
    soup = BeautifulSoup(html_text, "lxml")
    candidate_forms = []
    keywords = ("member", "signup", "register", "join", "invite", "email", "add-member", "add-member", "new-member")
    for form in soup.find_all("form"):
        form_info = {"action": form.get("action") or base_url,
                     "method": form.get("method", "get").lower(),
                     "inputs": []}
        text = (form.get_text() or "").lower()
        # collect inputs
        for inp in form.find_all(["input", "textarea", "select"]):
            name = inp.get("name") or inp.get("id") or inp.get("type") or "field"
            typ = inp.get("type") or inp.name
            form_info["inputs"].append({"name": name, "type": typ})
        # if form has textual clues or input names contain email/name
        clue = False
        if any(k in text for k in keywords):
            clue = True
        if any("email" in (i["name"] or "").lower() or "name" in (i["name"] or "").lower() for i in form_info["inputs"]):
            clue = True
        # add score to help pick one later
        score = 1 + sum(3 for k in keywords if k in text)
        form_info["clue"] = clue
        form_info["score"] = score
        candidate_forms.append(form_info)
    # sort by score & clues first
    candidate_forms.sort(key=lambda x: (not x["clue"], -x["score"]))
    return candidate_forms

def check_links(links, base_url, max_checks=200):
    results = []
    count = 0
    for l in links:
        if count >= max_checks:
            break
        url = l["url"]
        # only HTTP/HTTPS
        if not urlparse(url).scheme.startswith("http"):
            results.append({**l, "status": "skipped", "code": None, "reason": "non-http(s) URI"})
            continue
        try:
            # HEAD first
            r = requests.head(url, timeout=TIMEOUT, allow_redirects=True, headers={"User-Agent": DEFAULT_USER_AGENT})
            code = r.status_code
            ok = 200 <= code < 400
            # If server does not respond to HEAD properly, fallback to GET
            if code >= 400 or r.status_code == 405:
                r = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers={"User-Agent": DEFAULT_USER_AGENT})
                code = r.status_code
                ok = 200 <= code < 400
            results.append({**l, "status": "ok" if ok else "broken", "code": code, "reason": None if ok else f"{code}"})
        except Exception as e:
            results.append({**l, "status": "error", "code": None, "reason": str(e)})
        count += 1
    return results

def render_report(context):
    """
    context: dict with keys:
      - target_url, fetched_title, fetched_time, host_ip
      - link_results (list)
      - forms (list)
      - add_member_attempts (list)
      - summary (dict)
    """
    ensure_out_dir()
    # if user supplied report template, use it and inject placeholders if present
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            template = f.read()
        # simple placeholder replacements ({{KEY}} style)
        html = template
        replacements = {
            "{{TARGET}}": context.get("target_url", ""),
            "{{REPORT_DATE}}": context.get("fetched_time", ""),
            "{{SUMMARY}}": json.dumps(context.get("summary", {}), indent=2),
            "{{LINKS_TABLE}}": links_table_html(context.get("link_results", [])),
            "{{FORMS}}": forms_table_html(context.get("forms", [])),
            "{{ATTEMPTS}}": attempts_table_html(context.get("add_member_attempts", [])),
        }
        for k, v in replacements.items():
            html = html.replace(k, v)
    else:
        # fallback: build a simple report like sample_report.html
        html = f"""
        <!doctype html>
        <html><head><meta charset="utf-8"><title>Scan Report - {context.get('target_url')}</title>
        <style>body{{font-family:sans-serif;padding:20px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px}}</style>
        </head><body>
        <h1>Website Security Scan Report</h1>
        <p>Target: {context.get('target_url')}</p>
        <p>Report time: {context.get('fetched_time')}</p>
        <h2>Summary</h2><pre>{json.dumps(context.get('summary', {}), indent=2)}</pre>
        <h2>Links</h2>{links_table_html(context.get("link_results", []))}
        <h2>Detected Forms</h2>{forms_table_html(context.get("forms", []))}
        <h2>Add-member Attempts</h2>{attempts_table_html(context.get("add_member_attempts", []))}
        </body></html>
        """
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    return REPORT_FILE

def links_table_html(link_results):
    rows = []
    rows.append("<table><thead><tr><th>Tag</th><th>URL</th><th>Status</th><th>Code</th><th>Reason</th></tr></thead><tbody>")
    for r in link_results:
        rows.append(f"<tr><td>{r.get('tag')}</td><td><a href=\"{r.get('url')}\" target=_blank>{r.get('url')}</a></td><td>{r.get('status')}</td><td>{r.get('code') or ''}</td><td>{r.get('reason') or ''}</td></tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)

def forms_table_html(forms):
    rows = []
    if not forms:
        return "<p>No forms detected.</p>"
    rows.append("<table><thead><tr><th>Action</th><th>Method</th><th>Inputs</th><th>Clue</th><th>Score</th></tr></thead><tbody>")
    for f in forms:
        inputs = ", ".join([i["name"] for i in f.get("inputs", [])])
        rows.append(f"<tr><td>{f.get('action')}</td><td>{f.get('method')}</td><td>{inputs}</td><td>{f.get('clue')}</td><td>{f.get('score')}</td></tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)

def attempts_table_html(attempts):
    if not attempts:
        return "<p>No attempts performed.</p>"
    rows = []
    rows.append("<table><thead><tr><th>Form Action</th><th>Method</th><th>Payload</th><th>Result</th><th>Response Code</th></tr></thead><tbody>")
    for a in attempts:
        rows.append("<tr>")
        rows.append(f"<td>{a.get('action')}</td>")
        rows.append(f"<td>{a.get('method')}</td>")
        rows.append(f"<td><pre>{json.dumps(a.get('payload', {}), indent=2)}</pre></td>")
        rows.append(f"<td>{a.get('result')}</td>")
        rows.append(f"<td>{a.get('code') or ''}</td>")
        rows.append("</tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)

# main scan logic -----------------------------------------------------------

def run_scan(target_url, max_link_checks=200, try_add_member=True, member_payload=None):
    summary = {"total_links": 0, "broken_links": 0, "forms_detected": 0, "add_member_attempts": 0}
    fetched_time = datetime.datetime.utcnow().isoformat() + "Z"
    ctx = {
        "target_url": target_url,
        "fetched_time": fetched_time,
        "link_results": [],
        "forms": [],
        "add_member_attempts": [],
        "summary": summary,
    }
    # fetch page
    r = fetch_url(target_url)
    if isinstance(r, Exception):
        ctx["summary"]["error"] = str(r)
        render_report(ctx)
        return ctx
    html = r.text
    # hostname
    try:
        hostname = urlparse(target_url).hostname or ""
        host_ip = socket.gethostbyname(hostname) if hostname else ""
    except Exception:
        host_ip = ""
    ctx["host_ip"] = host_ip
    # title
    soup = BeautifulSoup(html, "lxml")
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    ctx["fetched_title"] = title
    # extract links
    links = extract_links(target_url, html)
    ctx["summary"]["total_links"] = len(links)
    link_results = check_links(links, base_url=target_url, max_checks=max_link_checks)
    ctx["link_results"] = link_results
    ctx["summary"]["broken_links"] = sum(1 for L in link_results if L.get("status") not in ("ok", "skipped"))
    # find forms
    forms = find_possible_member_forms(target_url, html)
    ctx["forms"] = forms
    ctx["summary"]["forms_detected"] = len(forms)
    # try adding member
    attempts = []
    if try_add_member:
        # prepare default payload if not provided
        default_payload = {"name": "SecurityScanTest", "email": f"scanner+{uuid.uuid4().hex[:8]}@example.com"}
        payload = (member_payload or default_payload)
        # if forms found, attempt the first candidate (highest score)
        if forms:
            form = forms[0]
            action = urljoin(target_url, form.get("action") or "")
            method = form.get("method", "post").lower()
            # map inputs heuristically
            form_data = {}
            for inp in form.get("inputs", []):
                n = inp.get("name") or ""
                if not n:
                    continue
                ln = n.lower()
                if "email" in ln:
                    form_data[n] = payload.get("email")
                elif "name" in ln:
                    form_data[n] = payload.get("name")
                elif "first" in ln and "name" in ln:
                    form_data[n] = payload.get("name").split()[0]
                elif "last" in ln and "name" in ln:
                    form_data[n] = payload.get("name").split()[-1]
                else:
                    # generic
                    form_data[n] = payload.get(n) or payload.get("name") or payload.get("email") or "test"
            try:
                resp = requests.request(method.upper(), action, data=form_data, timeout=TIMEOUT, headers={"User-Agent": DEFAULT_USER_AGENT})
                attempts.append({"action": action, "method": method, "payload": form_data, "result": "ok" if resp.status_code < 400 else "error", "code": resp.status_code, "response_text": resp.text[:500]})
            except Exception as e:
                attempts.append({"action": action, "method": method, "payload": form_data, "result": "exception", "code": None, "error": str(e)})
        else:
            # attempt to look for common signup endpoints
            common_paths = ["/signup", "/register", "/members/add", "/subscribe", "/join"]
            for p in common_paths:
                url_try = urljoin(target_url, p)
                try:
                    resp = requests.post(url_try, data=(member_payload or default_payload), timeout=5, headers={"User-Agent": DEFAULT_USER_AGENT})
                    attempts.append({"action": url_try, "method": "post", "payload": (member_payload or default_payload), "result": "ok" if resp.status_code < 400 else "error", "code": resp.status_code})
                except Exception as e:
                    attempts.append({"action": url_try, "method": "post", "payload": (member_payload or default_payload), "result": "exception", "error": str(e)})
        ctx["add_member_attempts"] = attempts
        ctx["summary"]["add_member_attempts"] = len(attempts)
    # finalize and render report
    render_report(ctx)
    return ctx

# Flask endpoints (MCP-friendly minimal interface) -------------------------

@app.route("/mcp/scrape", methods=["POST"])
def mcp_scrape():
    """
    POST JSON:
      { "target": "https://example.com", "max_link_checks": 200, "try_add_member": true }
    Response JSON:
      { "status": "ok", "report": "/reports/report.html", "summary": {...} }
    """
    payload = request.get_json(force=True, silent=True) or {}
    target = payload.get("target")
    if not target:
        return jsonify({"status":"error","error":"missing 'target' in json body"}), 400
    max_checks = int(payload.get("max_link_checks", 200))
    try_add = bool(payload.get("try_add_member", True))
    member_payload = payload.get("member_payload")
    ctx = run_scan(target, max_link_checks=max_checks, try_add_member=try_add, member_payload=member_payload)
    return jsonify({"status":"ok", "report_path": REPORT_FILE, "summary": ctx.get("summary", {}), "report_host": request.host_url.rstrip("/") + "/" + REPORT_FILE}), 200
            # --- PATCH: Ensure consistent report name for tests ---
import shutil
try:
                shutil.copy(report_path, "reports/report.html")
                print("✅ Standard test report created: reports/report.html - mcp_site_scanner.py:331")
except Exception as e:
                print(f"⚠️ Failed to create standard test report: {e} - mcp_site_scanner.py:333")
            # --- END PATCH ---

@app.route("/mcp/add_member", methods=["POST"])
def mcp_add_member():
    """
    POST JSON:
      { "form_action": "https://example.com/form", "method": "post", "payload": { "name": "...", "email": "..." } }
    Response JSON:
      { "status":"ok", "result": { "code": 200, "text": "..." } }
    """
    payload = request.get_json(force=True, silent=True) or {}
    action = payload.get("form_action")
    method = payload.get("method", "post").lower()
    data = payload.get("payload", {})
    if not action:
        return jsonify({"status":"error","error":"missing form_action"}), 400
    try:
        resp = requests.request(method.upper(), action, data=data, timeout=TIMEOUT, headers={"User-Agent": DEFAULT_USER_AGENT})
        return jsonify({"status":"ok", "code": resp.status_code, "text_snippet": resp.text[:1000]}), 200
    except Exception as e:
        return jsonify({"status":"error", "error": str(e)}), 500

# serve reports directory so that MCP clients can fetch generated report easily
@app.route(f"/{OUT_DIR}/<path:filename>")
def serve_reports(filename):
    return send_from_directory(OUT_DIR, filename)

# CLI start ---------------------------------------------------------------
def load_config(path="scanner_config.yaml"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MCP Site Scanner - minimal tool server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8020, type=int)
    parser.add_argument("--target", help="If provided, run one-off scan and exit (prints summary).")
    parser.add_argument("--once", action="store_true", help="If used with --target, run scan once and exit.")
    args = parser.parse_args()
    # if target provided, run one-off scan and exit
    if args.target:
        print("Running oneoff scan of - mcp_site_scanner.py:378", args.target)
        ctx = run_scan(args.target)
        print("Summary: - mcp_site_scanner.py:380", json.dumps(ctx.get("summary", {}), indent=2))
        print("Report written to - mcp_site_scanner.py:381", REPORT_FILE)
        if args.once:
            exit(0)
    # otherwise run minimal HTTP tool server for MCP clients
    print("Starting MCP Site Scanner tool server on {}:{} - mcp_site_scanner.py:385".format(args.host, args.port))
    app.run(host=args.host, port=args.port)
