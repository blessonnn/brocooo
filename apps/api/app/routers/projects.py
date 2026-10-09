"""Projects router — CRUD + create clipping job."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import Optional

from app.database import get_session
from app.models import Project, Clip, Job

router = APIRouter()


class CreateProjectRequest(BaseModel):
    """Create a new clipping project."""
    source_type: str = "link"  # "link" | "upload"
    source_url: Optional[str] = None
    source_file: Optional[str] = None  # file path from upload endpoint
    language: Optional[str] = None
    genre: Optional[str] = None
    num_clips: int = 5
    clip_length: str = "auto"
    prompt: Optional[str] = None
    caption_style: str = "hormozi"
    narration_style: Optional[str] = None
    narration_voice: Optional[str] = None
    layout: str = "fill"
    aspect_ratio: str = "9:16"
    resolution: str = "1080p"
    broll_enabled: bool = False
    filler_removal: bool = True
    filler_sensitivity: float = 0.5
    session_token: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project with clips and job status."""
    id: str
    title: Optional[str]
    source_type: str
    source_url: Optional[str]
    status: str
    num_clips: int
    clip_length: str
    caption_style: str
    layout: str
    aspect_ratio: str
    video_title: Optional[str]
    video_duration: Optional[float]
    created_at: datetime
    clips: list = []
    job: Optional[dict] = None


@router.post("", response_model=ProjectResponse)
async def create_project(req: CreateProjectRequest, session: Session = Depends(get_session)):
    """Create a project and queue a clipping job."""
    if req.source_type == "link" and not req.source_url:
        raise HTTPException(400, "source_url is required for link projects")
    if req.source_type == "upload" and not req.source_file:
        raise HTTPException(400, "source_file is required for upload projects")

    project = Project(**req.model_dump())
    session.add(project)

    # Create a job
    job = Job(project_id=project.id, stage="queued", message="Waiting in queue...")
    session.add(job)

    session.commit()
    session.refresh(project)

    return ProjectResponse(
        **project.model_dump(),
        clips=[],
        job={"id": job.id, "stage": job.stage, "progress": job.progress, "message": job.message},
    )


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    session_token: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """List projects for a session."""
    stmt = select(Project).order_by(Project.created_at.desc())  # type: ignore
    if session_token:
        stmt = stmt.where(Project.session_token == session_token)
    projects = session.exec(stmt.limit(50)).all()

    results = []
    for p in projects:
        clips = session.exec(select(Clip).where(Clip.project_id == p.id)).all()
        job = session.exec(
            select(Job).where(Job.project_id == p.id).order_by(Job.created_at.desc())  # type: ignore
        ).first()
        results.append(
            ProjectResponse(
                **p.model_dump(),
                clips=[c.model_dump() for c in clips],
                job=job.model_dump() if job else None,
            )
        )
    return results


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, session: Session = Depends(get_session)):
    """Get project details with clips and job status."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    clips = session.exec(
        select(Clip).where(Clip.project_id == project_id).order_by(Clip.score.desc())  # type: ignore
    ).all()
    job = session.exec(
        select(Job).where(Job.project_id == project_id).order_by(Job.created_at.desc())  # type: ignore
    ).first()

    return ProjectResponse(
        **project.model_dump(),
        clips=[c.model_dump() for c in clips],
        job=job.model_dump() if job else None,
    )


@router.delete("/{project_id}")
async def delete_project(project_id: str, session: Session = Depends(get_session)):
    """Delete a project and its clips."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # Delete clips
    clips = session.exec(select(Clip).where(Clip.project_id == project_id)).all()
    for clip in clips:
        session.delete(clip)

    # Delete jobs
    jobs = session.exec(select(Job).where(Job.project_id == project_id)).all()
    for job in jobs:
        session.delete(job)

    session.delete(project)
    session.commit()
    return {"ok": True}
