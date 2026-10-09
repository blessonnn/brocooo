"""Brand template model."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BrandTemplate(SQLModel, table=True):
    """A saved brand template with caption style, colors, fonts, and assets."""

    __tablename__ = "brand_template"

    id: str = Field(default_factory=_uuid, primary_key=True)
    name: str
    user_id: Optional[str] = None
    caption_style: dict = Field(default={}, sa_column=Column(JSON))
    colors: dict = Field(default={}, sa_column=Column(JSON))
    fonts: list = Field(default=[], sa_column=Column(JSON))
    logo_path: Optional[str] = None
    intro_path: Optional[str] = None
    outro_path: Optional[str] = None
    vocabulary: list = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_now)
