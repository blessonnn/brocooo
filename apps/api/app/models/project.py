"""Project and Clip data models."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Project(SQLModel, table=True):
    """A clipping project for one source video."""

    id: str = Field(default_factory=_uuid, primary_key=True)
    title: str | None = None
    source_type: str = Field(default="link")  # "link" | "upload"
    source_url: str | None = None
    source_file: str | None = None
    language: str | None = None
    genre: str | None = None

    # Clipping options
    num_clips: int = Field(default=5)
    clip_length: str = Field(default="auto")
    prompt: str | None = None
    caption_style: str = Field(default="hormozi")
    narration_style: str | None = None
    narration_voice: str | None = None
    layout: str = Field(default="fill")
    aspect_ratio: str = Field(default="9:16")
    resolution: str = Field(default="1080p")
    broll_enabled: bool = Field(default=False)
    filler_removal: bool = Field(default=True)
    filler_sensitivity: float = Field(default=0.5)

    # User / session
    user_id: str | None = None
    session_token: str | None = None

    # Status
    status: str = Field(default="pending")

    # Cached intermediate paths
    audio_path: str | None = None
    transcript_path: str | None = None
    scenes_path: str | None = None
    video_duration: float | None = None
    video_title: str | None = None

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class Clip(SQLModel, table=True):
    """A single short clip generated from a project."""

    id: str = Field(default_factory=_uuid, primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)

    # Timing — list of {start, end} segments (may be non-contiguous for stitched clips)
    segments: list = Field(default=[], sa_column=Column(JSON))
    duration: float = Field(default=0.0)

    # AI outputs
    title: str = Field(default="")
    description: str = Field(default="")
    hashtags: list = Field(default=[], sa_column=Column(JSON))
    hook_text: str = Field(default="")

    # Scoring
    score: int = Field(default=0)
    score_breakdown: dict = Field(default={}, sa_column=Column(JSON))
    grade: str = Field(default="C")
    why: str = Field(default="")

    # Render config
    caption_style: str = Field(default="hormozi")
    layout: str = Field(default="fill")
    narration_script: str | None = None
    narration_audio_path: str | None = None
    render_path: str | None = None
    thumbnail_path: str | None = None

    # Organization
    status: str = Field(default="candidate")
    is_favorite: bool = Field(default=False)
    label: str | None = None
    folder: str | None = None

    created_at: datetime = Field(default_factory=_now)
