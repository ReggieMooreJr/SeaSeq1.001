# ===============================
# Chapter 3: Main Report Generation
# ===============================
from doctest import REPORT_UDIFF
from click import echo
from jinja2 import Template
from typing import Any, Dict, List
from pathlib import Path

# Define the directory where reports will be saved
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def _get_risk_reason(event, risk):
    """
    Returns a tuple of (reason, description) for a given event and risk score.
    """
    if risk >= 7:
        reason = "High risk detected"
        description = "This event has a high risk score, indicating a critical issue."
    elif risk >= 4:
        reason = "Medium risk detected"
        description = "This event has a moderate risk score, indicating a potential issue."
    else:
        reason = "Low risk detected"
        description = "This event has a low risk score, indicating minimal concern."
    return reason, description


def generate(events: List[Any], risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate SEA-SEQ Wave Report (HTML, CSV, JSON) with
    risk score, pattern, tier → business impact mapping.
    """
    enriched = []
    for r in risks:
        event = r["event"]
        risk = r["risk"]
        pattern = r.get("pattern", "N/A")

        # Determine reason + description
        reason, description = _get_risk_reason(event, risk)

        # Assign tier + business impact mapping
        if risk >= 7:
            risk_level = "High"
            business_impact = "Critical Business Impact"
        elif risk >= 4:
            risk_level = "Medium"
            business_impact = "Moderate Business Impact"
        else:
            risk_level = "Low"
            business_impact = "Minimal Business Impact"

        enriched.append({
            "timestamp": str(getattr(event, "timestamp", None)),
            "page_url": getattr(event, "page_url", None),
            "https": getattr(event, "https", None),
            "num_links": getattr(event, "num_links", None),
            "num_forms": getattr(event, "num_forms", None),
            "has_login_form": getattr(event, "has_login_form", None),
            "pattern": pattern,
            "risk": risk,
            "risk_level": risk_level,
            "business_impact": business_impact,
            "risk_reason": reason,
            "description": description,
        })

    # Write JSON
    json_path = REPORT_DIR / "report.json"
    with open(json_path, "w") as f:
        json.dump(enriched, f, indent=2)

    # Write CSV
    csv_path = REPORT_DIR / "report.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=enriched[0].keys())
        writer.writeheader()
        writer.writerows(enriched)

    # Write HTML
    html_template = """
    <html>
      <head>
        <title>SEA-SEQ Wave Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h1 { color: #004085; }
          img.logo { max-height: 80px; }
          .low { background-color: #d4edda; }
          .medium { background-color: #fff3cd; }
          .high { background-color: #f8d7da; }
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid #ddd; padding: 8px; }
          th { background-color: #f0f4f7; }
        </style>
      </head>
      <body>
        <img src="../Logo.png" alt="Mojo Consultants Logo" class="logo"/>
        <h1>SEA-SEQ Wave Report</h1>
        <table>
          <tr>
            {% for col in records[0].keys() %}
              <th>{{ col }}</th>
            {% endfor %}
          </tr>
          {% for row in records %}
            {% set risk = row['risk'] %}
            {% if risk >= 7 %}
              <tr class="high">
            {% elif risk >= 4 %}
              <tr class="medium">
            {% else %}
              <tr class="low">
            {% endif %}
              {% for col, val in row.items() %}
                <td>{{ val }}</td>
              {% endfor %}
            </tr>
          {% endfor %}
        </table>
      </body>
    </html>
    """
    html = Template(html_template).render(records=enriched)
    html_path = REPORT_DIR / "report.html"
    with open(html_path, "w") as f:
        f.write(html)

echo(f"Report generated: {html_path}, {csv_path}, {json_path}")
return {
    "total_events": len(events),
    "anomalies": sum(1 for r in enriched if r["risk"] >= 7),
    "report_html_path": str(html_path),
    "report_csv_path": str(csv_path),
    "report_json_path": str(json_path),
    "events": enriched
}
