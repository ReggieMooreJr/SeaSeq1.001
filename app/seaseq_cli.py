#!/usr/bin/env python3
"""
Sea-Seq Validation CLI
Author: Mojo Consultants

Usage:
  ./seaseq_cli.py --input demo/issues.csv --api-url https://seaseq.internal/api --api-key DEMO123
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

import requests
from rich.console import Console
from rich.table import Table

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# Setup logging
logging.basicConfig(
    filename="seaseq_cli.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

console = Console()


def load_issues(file_path):
    """Load issues from CSV, JSON, or PDF."""
    ext = Path(file_path).suffix.lower()

    try:
        if ext == ".csv":
            issues = []
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    issues.append(row)
            logging.info(f"Loaded {len(issues)} issues from CSV. - seaseq_cli.py:47")
            return issues

        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                issues = json.load(f)
            logging.info(f"Loaded {len(issues)} issues from JSON. - seaseq_cli.py:53")
            return issues

        elif ext == ".pdf":
            if not PdfReader:
                raise ImportError("PyPDF2 not installed. Run `pip install PyPDF2`.")
            reader = PdfReader(file_path)
            text = "\n".join(
                page.extract_text() for page in reader.pages if page.extract_text()
            )
            issues = []
            for line in text.splitlines():
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3 and parts[0].isdigit():
                    issues.append({"id": parts[0], "description": parts[1], "severity": parts[2]})
            logging.info(f"Loaded {len(issues)} issues from PDF. - seaseq_cli.py:68")
            return issues

        else:
            raise ValueError(f"Unsupported file format: {ext}")

    except Exception as e:
        logging.error(f"Error reading {file_path}: {e} - seaseq_cli.py:75")
        console.print(f"[bold red]Error:[/bold red] Failed to load file {file_path} → {e} - seaseq_cli.py:76")
        sys.exit(1)


def upload_issues(issues, api_url, api_key):
    """Upload issues to the Sea-Seq API."""
    try:
        resp = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"issues": issues},
            timeout=10,
        )
        resp.raise_for_status()
        logging.info("Issues uploaded successfully. - seaseq_cli.py:90")
        return resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Upload failed: {e} - seaseq_cli.py:93")
        console.print(f"[bold red]Upload failed:[/bold red] {e} - seaseq_cli.py:94")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Sea-Seq Validation CLI")
    parser.add_argument("--input", required=True, help="Path to issues file (.csv, .json, .pdf)")
    parser.add_argument("--api-url", required=True, help="Sea-Seq API URL")
    parser.add_argument("--api-key", required=True, help="API Key for authentication")
    parser.add_argument("--export", help="Optional path to export parsed issues as JSON")

    args = parser.parse_args()

    # Load issues
    issues = load_issues(args.input)

    # Export parsed issues (optional)
    if args.export:
        try:
            with open(args.export, "w", encoding="utf-8") as f:
                json.dump(issues, f, indent=2)
            console.print(f"[bold green]✔ Exported parsed issues to {args.export}[/bold green] - seaseq_cli.py:114")
            logging.info(f"Exported parsed issues to {args.export} - seaseq_cli.py:115")
        except Exception as e:
            logging.error(f"Failed to export issues: {e} - seaseq_cli.py:117")
            console.print(f"[bold red]Error exporting issues:[/bold red] {e} - seaseq_cli.py:118")
            sys.exit(1)

    # Display summary
    table = Table(title="Issues Summary")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Severity", style="red")

    for issue in issues:
        table.add_row(str(issue.get("id")), issue.get("description"), issue.get("severity"))

    console.print(table)

    # Upload to API
    result = upload_issues(issues, args.api_url, args.api_key)

    console.print(f"[bold green]✔ Upload complete![/bold green] Server response: - seaseq_cli.py:135")
    console.print(result)

def main():
    parser = argparse.ArgumentParser(description="Sea-Seq Validation CLI")
    parser.add_argument("--input", required=True, help="Path to issues file (.csv, .json, .pdf)")
    parser.add_argument("--api-url", required=True, help="Sea-Seq API URL")
    parser.add_argument("--api-key", required=True, help="API Key for authentication")

    args = parser.parse_args()

    # Load issues
    issues = load_issues(args.input)

    # Display summary
    table = Table(title="Issues Summary")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Severity", style="red")

    for issue in issues:
        table.add_row(str(issue.get("id")), issue.get("description"), issue.get("severity"))

    console.print(table)

    # Upload to API
    result = upload_issues(issues, args.api_url, args.api_key)

    console.print(f"[bold green]✔ Upload complete![/bold green] Server response: - seaseq_cli.py:163")
    console.print(result)


if __name__ == "__main__":
    main()
