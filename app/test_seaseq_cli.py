import os
import json
import tempfile
import pytest
from seaseq_cli import load_issues

# --- Fixtures ---
CSV_CONTENT = "id,description,severity\n1,SSL expired,High\n2,Weak password,Medium\n"
JSON_CONTENT = json.dumps([
    {"id": 1, "description": "SSL expired", "severity": "High"},
    {"id": 2, "description": "Weak password", "severity": "Medium"}
])

@pytest.fixture
def tmp_csv_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
        f.write(CSV_CONTENT)
        return f.name

@pytest.fixture
def tmp_json_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as f:
        f.write(JSON_CONTENT)
        return f.name

# --- Tests ---
def test_load_csv(tmp_csv_file):
    issues = load_issues(tmp_csv_file)
    assert len(issues) == 2
    assert issues[0]["description"] == "SSL expired"

def test_load_json(tmp_json_file):
    issues = load_issues(tmp_json_file)
    assert len(issues) == 2
    assert issues[1]["severity"] == "Medium"

def test_invalid_file():
    with pytest.raises(SystemExit):
        load_issues("nonexistent.csv")
