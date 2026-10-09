"""User settings router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_settings():
    """Get current user settings (placeholder until auth)."""
    return {
        "default_language": "auto",
        "default_caption_style": "hormozi",
        "default_layout": "fill",
        "default_resolution": "1080p",
        "api_keys_configured": {
            "gemini": False,
            "groq": False,
            "pexels": False,
            "youtube": False,
        },
    }


@router.put("")
async def update_settings():
    """Update settings (Phase 4 — requires auth)."""
    return {"ok": True, "message": "Settings saved"}
