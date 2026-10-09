"""Brocooo Worker — polls the job queue and runs the clipping pipeline."""

import os
import sys
import time
import asyncio
import platform
from datetime import datetime, timezone

# Add parent dir to path so we can import the API models and services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlmodel import Session, select, create_engine
from app.models import Job, Project, Clip
from app.config import settings

# Import services
from app.services.downloader import download_video, extract_audio
from app.services.transcriber import transcribe_audio
from app.services.scene_analyzer import analyze_scenes
from app.services.clip_selector import select_clips
from app.services.reframer import calculate_crop_plan
from app.services.caption_generator import generate_ass
from app.services.renderer import render_clip

# Database setup
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)

WORKER_ID = f"worker-{platform.node()}-{os.getpid()}"
POLL_INTERVAL = 2.0


def claim_job(session: Session) -> Job | None:
    job = session.exec(
        select(Job).where(Job.stage == "queued").where(Job.worker_id == None).order_by(Job.created_at)
    ).first()
    if job:
        job.worker_id = WORKER_ID
        job.claimed_at = datetime.now(timezone.utc)
        job.stage = "downloading"
        job.message = "Initializing job..."
        session.add(job)
        session.commit()
        session.refresh(job)
    return job


def update_job(session: Session, job: Job, stage: str, progress: float, message: str):
    job.stage = stage
    job.progress = progress
    job.message = message
    session.add(job)
    session.commit()
    print(f"[{job.id[:8]}] {stage} ({progress*100:.0f}%): {message}")


async def run_pipeline(session: Session, job: Job, project: Project):
    try:
        project_dir = os.path.join(settings.storage_dir, project.id)
        os.makedirs(project_dir, exist_ok=True)
        
        # 1. Download
        update_job(session, job, "downloading", 0.05, "Downloading video...")
        if project.source_type == "link" and project.source_url:
            dl_info = await download_video(project.source_url, project_dir)
            project.source_file = dl_info["file_path"]
            project.video_title = dl_info["title"]
            project.video_duration = dl_info["duration"]
            session.add(project)
            session.commit()
            
        video_path = project.source_file
        if not video_path or not os.path.exists(video_path):
            raise Exception("Video file missing")

        # 2. Extract Audio
        update_job(session, job, "extracting_audio", 0.10, "Extracting audio track...")
        audio_path = os.path.join(project_dir, "audio.wav")
        await extract_audio(video_path, audio_path)
        project.audio_path = audio_path
        session.add(project)
        session.commit()

        # 3. Transcribe
        update_job(session, job, "transcribing", 0.25, "Transcribing audio (this may take a few minutes)...")
        transcript_path = os.path.join(project_dir, "transcript.json")
        await transcribe_audio(audio_path, transcript_path, project.language)
        project.transcript_path = transcript_path
        session.add(project)
        session.commit()

        # 4. Analyze Scenes
        update_job(session, job, "analyzing", 0.35, "Analyzing scenes and face tracking...")
        scenes_path = os.path.join(project_dir, "scenes.json")
        await analyze_scenes(video_path, scenes_path)
        project.scenes_path = scenes_path
        session.add(project)
        session.commit()

        # 5. Select Clips via LLM
        update_job(session, job, "selecting_clips", 0.50, "AI is selecting the best viral moments...")
        candidates = await select_clips(
            transcript_path, 
            num_clips=project.num_clips, 
            clip_length=project.clip_length,
            prompt=project.prompt,
            genre=project.genre
        )
        
        clips = []
        for cand in candidates:
            clip = Clip(
                project_id=project.id,
                segments=[{"start": cand["start_time"], "end": cand["end_time"]}],
                duration=cand["end_time"] - cand["start_time"],
                title=cand["title"],
                description=cand["description"],
                hook_text=cand["hook_text"],
                hashtags=cand["hashtags"],
                score=cand["score"],
                score_breakdown=cand["score_breakdown"],
                grade=cand["grade"],
                why=cand["why"],
                caption_style=project.caption_style,
                layout=project.layout
            )
            session.add(clip)
            clips.append(clip)
        session.commit()

        # 6. Reframing & Captioning & Rendering
        total_clips = len(clips)
        style_path = os.path.join(os.path.dirname(__file__), "..", "..", "packages", "caption-styles", "presets", f"{project.caption_style}.json")
        
        for i, clip in enumerate(clips):
            base_prog = 0.60 + (i / total_clips * 0.30)
            update_job(session, job, "rendering", base_prog, f"Rendering clip {i+1} of {total_clips}...")
            
            c_start = clip.segments[0]["start"]
            c_end = clip.segments[0]["end"]
            
            # Reframe
            crop_plan = calculate_crop_plan(scenes_path, c_start, c_end, clip.layout)
            
            # Caption
            ass_path = os.path.join(project_dir, f"{clip.id}.ass")
            generate_ass(transcript_path, c_start, c_end, style_path, ass_path)
            
            # Render
            render_path = os.path.join(project_dir, f"{clip.id}.mp4")
            await render_clip(video_path, c_start, c_end, crop_plan, ass_path, render_path)
            
            clip.render_path = render_path
            clip.status = "done"
            session.add(clip)
            session.commit()

        update_job(session, job, "done", 1.0, "All clips ready!")
        job.completed_at = datetime.now(timezone.utc)
        project.status = "done"
        session.add(job)
        session.add(project)
        session.commit()

    except Exception as e:
        job.stage = "failed"
        job.error = str(e)
        project.status = "failed"
        session.add(job)
        session.add(project)
        session.commit()
        raise e


def main():
    print(f"🥦 Brocooo Worker started [{WORKER_ID}]")
    while True:
        try:
            with Session(engine) as session:
                job = claim_job(session)
                if job:
                    project = session.get(Project, job.project_id)
                    if project:
                        asyncio.run(run_pipeline(session, job, project))
        except Exception as e:
            print(f"⚠️ Worker error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
