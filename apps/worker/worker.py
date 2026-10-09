"""Brocooo Worker — polls the job queue and runs the clipping pipeline."""

import os
import sys
import time
import platform
from datetime import datetime, timezone

# Add parent dir to path so we can import the API models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlmodel import Session, select, create_engine
from app.models import Job, Project
from app.config import settings

# Database setup (shared with API)
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)

WORKER_ID = f"worker-{platform.node()}-{os.getpid()}"
POLL_INTERVAL = 1.0  # seconds


def claim_job(session: Session) -> Job | None:
    """Atomically claim the oldest queued job."""
    job = session.exec(
        select(Job)
        .where(Job.stage == "queued")
        .where(Job.worker_id == None)  # noqa: E711
        .order_by(Job.created_at)  # type: ignore
    ).first()

    if job:
        job.worker_id = WORKER_ID
        job.claimed_at = datetime.now(timezone.utc)
        job.stage = "downloading"
        job.message = "Starting pipeline..."
        session.add(job)
        session.commit()
        session.refresh(job)

    return job


def update_job(session: Session, job: Job, stage: str, progress: float, message: str, eta: int | None = None):
    """Update job progress."""
    job.stage = stage
    job.progress = progress
    job.message = message
    job.eta_seconds = eta
    session.add(job)
    session.commit()


def run_pipeline(session: Session, job: Job, project: Project):
    """Execute the full clipping pipeline (Phase 1 will implement each stage)."""
    stages = [
        ("downloading", 0.05, "Downloading video..."),
        ("extracting_audio", 0.10, "Extracting audio track..."),
        ("transcribing", 0.25, "Transcribing audio (this may take a few minutes)..."),
        ("analyzing", 0.35, "Analyzing scenes and audio..."),
        ("selecting_clips", 0.50, "AI is selecting the best moments..."),
        ("scoring", 0.60, "Scoring and ranking clips..."),
        ("reframing", 0.70, "Planning crop and reframe..."),
        ("generating_captions", 0.80, "Generating captions..."),
        ("rendering", 0.90, "Rendering final clips..."),
        ("done", 1.0, "All clips ready!"),
    ]

    for stage, progress, message in stages:
        update_job(session, job, stage, progress, message)

        # TODO (Phase 1): Each stage will call its actual implementation
        # For now, simulate with a short delay
        if stage != "done":
            time.sleep(0.5)

    job.completed_at = datetime.now(timezone.utc)
    session.add(job)
    session.commit()


def main():
    """Main worker loop."""
    print(f"🥦 Brocooo Worker started [{WORKER_ID}]")
    print(f"   Database: {settings.database_url}")
    print(f"   Poll interval: {POLL_INTERVAL}s")

    while True:
        try:
            with Session(engine) as session:
                job = claim_job(session)
                if job:
                    project = session.get(Project, job.project_id)
                    if not project:
                        job.stage = "failed"
                        job.error = "Project not found"
                        session.add(job)
                        session.commit()
                        continue

                    print(f"   📋 Claimed job {job.id[:8]} for project {project.id[:8]}")
                    try:
                        run_pipeline(session, job, project)
                        print(f"   ✅ Job {job.id[:8]} completed")
                    except Exception as e:
                        job.stage = "failed"
                        job.error = str(e)
                        session.add(job)
                        session.commit()
                        print(f"   ❌ Job {job.id[:8]} failed: {e}")

        except KeyboardInterrupt:
            print("\n🛑 Worker shutting down...")
            break
        except Exception as e:
            print(f"   ⚠️  Worker error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
