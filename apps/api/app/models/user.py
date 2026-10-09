"""User model — optional account."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """Optional user account (magic link or Google sign-in)."""

    id: str = Field(default_factory=_uuid, primary_key=True)
    email: str | None = Field(default=None, unique=True, index=True)
    name: str | None = None
    avatar_url: str | None = None
    provider: str | None = None  # "google" | "email"

    # Settings
    default_language: str = Field(default="auto")
    default_caption_style: str = Field(default="hormozi")
    default_layout: str = Field(default="fill")
    default_resolution: str = Field(default="1080p")

    created_at: datetime = Field(default_factory=_now)
