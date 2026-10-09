"""Job queue model — SQLite-backed job table."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


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
    message: str | None = None
    eta_seconds: int | None = None
    error: str | None = None

    # Worker claim
    worker_id: str | None = None
    claimed_at: datetime | None = None

    # Timestamps
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=_now)
