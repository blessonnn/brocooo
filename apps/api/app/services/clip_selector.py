"""Clip selection logic using LLM."""

import json

from app.services.llm_service import generate_json

CLIP_SELECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "clips": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start_time": {"type": "number", "description": "Start time in seconds"},
                    "end_time": {"type": "number", "description": "End time in seconds"},
                    "title": {"type": "string", "description": "Catchy title for the clip"},
                    "description": {"type": "string", "description": "Short description"},
                    "hook_text": {"type": "string", "description": "Text overlay for the first 3 seconds"},
                    "hashtags": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "score": {"type": "integer", "description": "0-100 virality score"},
                    "score_breakdown": {
                        "type": "object",
                        "properties": {
                            "hook": {"type": "integer"},
                            "flow": {"type": "integer"},
                            "emotion": {"type": "integer"},
                            "trend": {"type": "integer"},
                            "share": {"type": "integer"}
                        }
                    },
                    "grade": {"type": "string", "enum": ["A+", "A", "B", "C"]},
                    "why": {"type": "string", "description": "One-line explanation of why this clip was selected"}
                },
                "required": ["start_time", "end_time", "title", "description", "hook_text", "hashtags", "score", "score_breakdown", "grade", "why"]
            }
        }
    },
    "required": ["clips"]
}


async def select_clips(
    transcript_path: str,
    num_clips: int = 5,
    clip_length: str = "auto",
    prompt: str | None = None,
    genre: str | None = None
) -> list[dict]:
    """
    Select the best clips from a transcript using LLM.
    Returns a list of candidate clips.
    """
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)

    # Combine text from segments
    # For very long videos, we might need to chunk this or use RAG, 
    # but for MVP we pass the formatted transcript directly.
    # Format: [00:00.00] text ...
    formatted_transcript = ""
    for seg in transcript_data.get("segments", []):
        formatted_transcript += f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}\n"
        
    system_prompt = (
        "You are an expert short-form video producer and viral content strategist. "
        "Your goal is to extract the most engaging, viral, and standalone moments from the provided video transcript.\n\n"
        "Criteria for a viral clip:\n"
        "1. STRONG HOOK: The first 3 seconds must grab attention instantly.\n"
        "2. COHERENCE: The clip must make sense on its own without needing the full context of the video.\n"
        "3. HIGH ENERGY / EMOTION: Look for humor, controversy, deep insights, or strong reactions.\n"
        "4. VALUE: The viewer must learn something, feel something, or be entertained.\n\n"
        "Target Length: " + (clip_length if clip_length != "auto" else "30-60 seconds") + "\n"
        "Genre context: " + (genre or "General video content") + "\n"
    )
    
    if prompt:
        system_prompt += f"\nSpecific user instructions for clip selection: {prompt}\n"
        
    user_prompt = (
        f"Analyze the following transcript and extract exactly {num_clips} clips.\n\n"
        f"Transcript:\n{formatted_transcript}"
    )

    result = await generate_json(user_prompt, CLIP_SELECTION_SCHEMA, system_prompt)
    
    clips = result.get("clips", [])
    
    # Sort by score descending
    clips.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return clips[:num_clips]
