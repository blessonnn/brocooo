"""Job queue model — SQLite-backed job table."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Job(SQLModel, table=True):
    """A background processing job tied to a project."""

    id: str = Field(default_factory=_uuid, primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)

    # Pipeline stage
    stage: str = Field(default="queued")
    progress: float = Field(default=0.0)
    message: Optional[str] = None
    eta_seconds: Optional[int] = None
    error: Optional[str] = None

    # Worker claim
    worker_id: Optional[str] = None
    claimed_at: Optional[datetime] = None

    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=_now)
