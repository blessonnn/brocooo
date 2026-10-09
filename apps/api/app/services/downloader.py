"""Downloader service using yt-dlp."""

import asyncio
import os

import yt_dlp


class DownloadError(Exception):
    pass


async def download_video(url: str, output_dir: str) -> dict:
    """Download video from YouTube or other sites using yt-dlp."""
    os.makedirs(output_dir, exist_ok=True)
    
    # We download the best video+audio format that is mp4
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise DownloadError("Failed to extract info")
                
                filename = ydl.prepare_filename(info)
                return {
                    "file_path": filename,
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "id": info.get("id"),
                }
            except Exception as e:
                raise DownloadError(f"yt-dlp error: {e}")

    # Run blocking yt-dlp in a thread
    result = await asyncio.to_thread(_download)
    return result


async def extract_audio(video_path: str, output_path: str) -> str:
    """Extract 16kHz mono audio for transcription."""
    import ffmpeg
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    def _extract():
        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(quiet=True)
            )
        except ffmpeg.Error as e:
            raise DownloadError(f"Audio extraction failed: {e.stderr.decode() if e.stderr else str(e)}")

    await asyncio.to_thread(_extract)
    return output_path
