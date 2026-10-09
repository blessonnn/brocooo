"""Brand template model."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BrandTemplate(SQLModel, table=True):
    """A saved brand template with caption style, colors, fonts, and assets."""

    __tablename__ = "brand_template"

    id: str = Field(default_factory=_uuid, primary_key=True)
    name: str
    user_id: str | None = None
    caption_style: dict = Field(default={}, sa_column=Column(JSON))
    colors: dict = Field(default={}, sa_column=Column(JSON))
    fonts: list = Field(default=[], sa_column=Column(JSON))
    logo_path: str | None = None
    intro_path: str | None = None
    outro_path: str | None = None
    vocabulary: list = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_now)
