from datetime import datetime

from pydantic import BaseModel, Field, SecretStr


class ScanRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    authorized: bool = False


class EvidenceOut(BaseModel):
    source: str
    matched: str
    kind: str
    weight: int


class TechnologyOut(BaseModel):
    name: str
    category: str
    score: int
    confidence: str
    evidence: list[EvidenceOut]


class AIReportOut(BaseModel):
    id: int
    model: str
    content: str
    created_at: datetime


class ScanOut(BaseModel):
    id: int
    url: str
    final_url: str
    status_code: int
    content_type: str
    title: str
    headers: dict[str, str]
    meta: list[dict[str, str]]
    scripts: list[str]
    styles: list[str]
    created_at: datetime
    technologies: list[TechnologyOut]
    ai_report_count: int = 0
    ai_reports: list[AIReportOut] = []


class CompareRequest(BaseModel):
    first_scan_id: int
    second_scan_id: int


class AIConfigIn(BaseModel):
    base_url: str = Field(min_length=1, max_length=2048)
    api_key: SecretStr = Field(min_length=8, max_length=4096)
    model: str = Field(min_length=1, max_length=200)


class AIConfigView(BaseModel):
    configured: bool
    base_url: str | None = None
    model: str | None = None


class AIAnalysisRequest(BaseModel):
    scan_id: int
    confirm_data_sent: bool


class AIAnalysisResult(BaseModel):
    model: str
    content: str
