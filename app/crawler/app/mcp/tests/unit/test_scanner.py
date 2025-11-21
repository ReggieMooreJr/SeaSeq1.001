import os
import subprocess

def test_report_generated(tmp_path):
    """Ensure report.html is produced when scanner runs once."""
    cmd = ["bash", "run-scan.sh", "once", "https://example.com"]
    subprocess.run(cmd, check=False)
    assert os.path.exists("reports/report.html"), "Expected report.html not found"
