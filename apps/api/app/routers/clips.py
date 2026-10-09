"""Clips router — details, download, update."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session
from typing import Optional
import os

from app.database import get_session
from app.models import Clip

router = APIRouter()


class UpdateClipRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[list[str]] = None
    caption_style: Optional[str] = None
    layout: Optional[str] = None
    is_favorite: Optional[bool] = None
    label: Optional[str] = None
    folder: Optional[str] = None


@router.get("/{clip_id}")
async def get_clip(clip_id: str, session: Session = Depends(get_session)):
    """Get clip details."""
    clip = session.get(Clip, clip_id)
    if not clip:
        raise HTTPException(404, "Clip not found")
    return clip.model_dump()


@router.patch("/{clip_id}")
async def update_clip(clip_id: str, req: UpdateClipRequest, session: Session = Depends(get_session)):
    """Update clip metadata."""
    clip = session.get(Clip, clip_id)
    if not clip:
        raise HTTPException(404, "Clip not found")

    for key, value in req.model_dump(exclude_none=True).items():
        setattr(clip, key, value)

    session.add(clip)
    session.commit()
    session.refresh(clip)
    return clip.model_dump()


@router.get("/{clip_id}/download")
async def download_clip(clip_id: str, session: Session = Depends(get_session)):
    """Download rendered clip as MP4."""
    clip = session.get(Clip, clip_id)
    if not clip:
        raise HTTPException(404, "Clip not found")
    if not clip.render_path or not os.path.exists(clip.render_path):
        raise HTTPException(404, "Clip not yet rendered")

    return FileResponse(
        clip.render_path,
        media_type="video/mp4",
        filename=f"brocooo-{clip.title or clip.id}.mp4",
    )
