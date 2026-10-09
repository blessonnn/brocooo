"""SSE progress endpoint for live job updates."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.database import engine
from app.models import Job

router = APIRouter()


@router.get("/projects/{project_id}/progress")
async def project_progress(project_id: str):
    """Server-Sent Events stream for job progress."""

    async def event_stream():
        last_stage = None
        last_progress = -1.0

        while True:
            # Open a fresh session each poll
            with Session(engine) as session:
                job = session.exec(
                    select(Job)
                    .where(Job.project_id == project_id)
                    .order_by(Job.created_at.desc())  # type: ignore
                ).first()

                if not job:
                    yield f"data: {json.dumps({'error': 'No job found'})}\n\n"
                    return

                # Only send if something changed
                if job.stage != last_stage or job.progress != last_progress:
                    last_stage = job.stage
                    last_progress = job.progress

                    payload = {
                        "job_id": job.id,
                        "stage": job.stage,
                        "progress": job.progress,
                        "message": job.message,
                        "eta_seconds": job.eta_seconds,
                        "error": job.error,
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

                # Terminal states
                if job.stage in ("done", "failed"):
                    return

            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
