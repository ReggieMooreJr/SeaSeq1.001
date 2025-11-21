# ===============================
# Chapter 1: Unit Tests for events.py
# ===============================
from app.models.events import SecurityEvent, TrainResult, ReportSummary
from datetime import datetime

def test_security_event_fields():
    event = SecurityEvent(page_url="http://test.com", https=True, num_links=1, num_forms=1, has_login_form=False, headers={})
    assert isinstance(event.timestamp, datetime)
    assert event.page_url == "http://test.com"
    assert event.https is True
    assert event.num_links == 1
    assert event.num_forms == 1
    assert event.has_login_form is False
    assert isinstance(event.headers, dict)

def test_train_result():
    result = TrainResult(trained_on=5, model_path="/tmp/model.pkl")
    assert result.trained_on == 5
    assert result.model_path == "/tmp/model.pkl"

def test_report_summary():
    summary = ReportSummary(total_events=10, anomalies=2, report_html_path="/tmp/report.html", report_csv_path="/tmp/report.csv", report_json_path="/tmp/report.json")
    assert summary.total_events == 10
    assert summary.anomalies == 2
    assert summary.report_html_path == "/tmp/report.html"
    assert summary.report_csv_path == "/tmp/report.csv"
    assert summary.report_json_path == "/tmp/report.json"
