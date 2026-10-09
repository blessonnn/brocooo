"""Explore / Trending feed (YouTube Data API v3 proxy with caching)."""

import time

import httpx
from fastapi import APIRouter, Query

from app.config import settings

router = APIRouter()

# In-memory cache (hourly refresh)
_cache: dict = {"data": [], "region": "", "timestamp": 0}
CACHE_TTL = 3600  # 1 hour


@router.get("/explore")
async def explore(region: str = Query(default="US", max_length=2)):
    """Get trending YouTube videos for the Explore grid."""
    now = time.time()

    # Return cached data if fresh
    if (
        _cache["data"]
        and _cache["region"] == region
        and (now - _cache["timestamp"]) < CACHE_TTL
    ):
        return {"videos": _cache["data"], "region": region, "cached": True}

    if not settings.youtube_data_api_key:
        return {
            "videos": [],
            "region": region,
            "cached": False,
            "error": "YouTube Data API key not configured. Add YOUTUBE_DATA_API_KEY to .env to enable Explore.",
        }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,contentDetails,statistics",
                    "chart": "mostPopular",
                    "regionCode": region,
                    "maxResults": 24,
                    "key": settings.youtube_data_api_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

        videos = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            videos.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "duration": item.get("contentDetails", {}).get("duration", ""),
                "views": int(stats.get("viewCount", 0)),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
            })

        _cache["data"] = videos
        _cache["region"] = region
        _cache["timestamp"] = now

        return {"videos": videos, "region": region, "cached": False}

    except Exception as e:
        return {"videos": _cache.get("data", []), "region": region, "error": str(e)}
