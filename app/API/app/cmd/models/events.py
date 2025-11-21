# ===============================
# Chapter 1: Imports and Models
# ===============================
# This chapter defines the core data models for SEA-SEC events and reporting.
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict
from datetime import datetime

# ===============================
# Chapter 2: Security Event Model
# ===============================
class SecurityEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    page_url: HttpUrl
    https: bool
    num_links: int
    num_forms: int
    has_login_form: bool
    headers: Dict[str, str] = {}
    note: Optional[str] = None
    risk: Optional[int] = None           # NEW field
    risk_reason: Optional[str] = None    # NEW field
    description: Optional[str] = None    # NEW field

# ===============================
# Chapter 3: ML Training Result Model
# ===============================
class TrainResult(BaseModel):
    trained_on: int
    model_path: str

# ===============================
# Chapter 4: Report Summary Model
# ===============================
class ReportSummary(BaseModel):
    total_events: int
    anomalies: int
    report_html_path: str
    report_csv_path: str
    report_json_path: str
    events: Optional[List[SecurityEvent]] = None   # NEW: embed detail
