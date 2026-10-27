from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def now_utc():
    return datetime.now(UTC)


class ScanRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    final_url: str
    status_code: int
    title: str
    content_type: str
    summary_json: str = "{}"
    created_at: datetime = Field(default_factory=now_utc, index=True)


class TechnologyRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scanrow.id", index=True)
    name: str
    category: str
    score: int
    confidence: str


class EvidenceRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    technology_id: int = Field(foreign_key="technologyrow.id", index=True)
    source: str
    matched: str
    kind: str
    weight: int


class AIReportRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scanrow.id", index=True)
    model: str
    content: str
    created_at: datetime = Field(default_factory=now_utc, index=True)
