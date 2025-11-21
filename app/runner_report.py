#!/usr/bin/env python3
"""
runner_report.py – Generate SEA-SEQ reports via Python reporting module.
Accepts input data in JSON, CSV, or Excel (.xls/.xlsx).
"""

import os
import sys
import csv
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import argparse

import pandas as pd  # for CSV/Excel parsing

# Import report generator
from app.services import report_service


def load_input(input_path: str) -> (List[Any], List[Dict[str, Any]]):
    """
    Load events/risks from JSON, CSV, or Excel file.
    Expected schema: must include at least "risk" field.
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    ext = input_file.suffix.lower()

    if ext == ".json":
        with open(input_file, "r", encoding="utf-8") as f:
            risks = json.load(f)
    elif ext == ".csv":
        risks = pd.read_csv(input_file).to_dict(orient="records")
    elif ext in (".xls", ".xlsx"):
        risks = pd.read_excel(input_file).to_dict(orient="records")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Convert into expected shape
    events = []
    for r in risks:
        if "risk" not in r:
            raise ValueError("Each record must include a 'risk' field")

        # Stub event object with attributes
        event_stub = type(
            "Evt",
            (),
            {
                "timestamp": r.get("timestamp", datetime.utcnow()),
                "page_url": r.get("page_url"),
                "https": r.get("https"),
                "num_links": r.get("num_links"),
                "num_forms": r.get("num_forms"),
                "has_login_form": r.get("has_login_form"),
            },
        )()
        r["event"] = event_stub

    return events, risks


def main():
    # CLI args
    parser = argparse.ArgumentParser(description="SEA-SEQ Report Generator")
    parser.add_argument(
        "--input", "-i", type=str, help="Path to input file (JSON, CSV, XLSX)"
    )
    parser.add_argument(
        "--output-dir", "-o", type=str, default="/app/reports",
        help="Directory where reports will be written (default: /app/reports)"
    )
    args = parser.parse_args()

    # Logging
    log_file = "/var/log/sea-seq/runner_report.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger("runner_report")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Starting SEA-SEQ report generation…")

        if args.input:
            logger.info(f"Loading input file: {args.input}")
            events, risks = load_input(args.input)
        else:
            logger.warning("No input file provided — using dummy data")
            events = []
            risks = [
                {"event": type("Evt", (), {"timestamp": datetime.utcnow(), "page_url": "https://demo.com"})(),
                 "risk": 8,
                 "pattern": "SQLi"}
            ]

        # Call generator
        result = report_service.generate(events, risks)

        # Move outputs to requested directory
        for key in ("report_html_path", "report_csv_path", "report_json_path"):
            src = Path(result[key])
            dst = output_dir / src.name
            if src != dst:
                src.replace(dst)
                result[key] = str(dst)

        logger.info("✅ Report generated successfully")
        logger.info("HTML: %s", result["report_html_path"])
        logger.info("CSV: %s", result["report_csv_path"])
        logger.info("JSON: %s", result["report_json_path"])

        print("Report generated: - runner_report.py:124")
        print(f"HTML → {result['report_html_path']} - runner_report.py:125")
        print(f"CSV  → {result['report_csv_path']} - runner_report.py:126")
        print(f"JSON → {result['report_json_path']} - runner_report.py:127")

    except Exception as e:
        logger.error("❌ Report generation failed: %s", e)
        logger.debug(traceback.format_exc())
        print(f"[ERROR] Report generation failed: {e} - runner_report.py:132", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
