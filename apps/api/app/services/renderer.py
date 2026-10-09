"""FFmpeg rendering pipeline."""

import asyncio
import os


class RenderError(Exception):
    pass

async def render_clip(
    video_path: str,
    clip_start: float,
    clip_end: float,
    crop_plan: list,
    ass_path: str,
    output_path: str
) -> str:
    """
    Render a 9:16 cropped clip with burned-in subtitles.
    """
    import ffmpeg
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Simple static crop for Phase 1 (use first center point)
    # x_center is 0.0 to 1.0 (relative to width)
    # We want 1080x1920 (9:16) output.
    
    # If source is e.g. 1920x1080, crop width is 1080*(1080/1920) = 607.5
    # Wait, ffmpeg crop syntax: crop=w:h:x:y
    # Let's crop to 9:16 ratio of the height. 
    # if height is ih, width is ih * 9 / 16.
    
    x_center = crop_plan[0]["x_center"] if crop_plan else 0.5
    
    # For a 1920x1080 video:
    # crop width = 1080 * 9/16 = 607.5. Let's say 608.
    # crop x = (1920 * x_center) - (608 / 2)
    
    # Filter string for ffmpeg
    # 'crop=ih*9/16:ih:(iw-ih*9/16)*X:0' where X is mapped x_center
    # Since x_center is center of the window, we calculate top left X:
    # x = (iw * x_center) - (ih * 9/16 / 2)
    # Scale to 1080x1920
    
    crop_expr = f"crop=ih*9/16:ih:iw*{x_center}-ih*9/32:0"
    scale_expr = "scale=1080:1920"
    
    # We must escape the ASS path for ffmpeg filter
    escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
    
    def _render():
        try:
            # -ss before -i for fast seeking
            (
                ffmpeg
                .input(video_path, ss=clip_start, t=clip_end-clip_start)
                .output(
                    output_path, 
                    vf=f"{crop_expr},{scale_expr},ass='{escaped_ass}'",
                    vcodec="libx264",
                    preset="veryfast",
                    crf=23,
                    acodec="aac",
                    audio_bitrate="128k"
                )
                .overwrite_output()
                .run(quiet=True)
            )
        except ffmpeg.Error as e:
            raise RenderError(f"FFmpeg render failed: {e.stderr.decode() if e.stderr else str(e)}")

    await asyncio.to_thread(_render)
    return output_path
