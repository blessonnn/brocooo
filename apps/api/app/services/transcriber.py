"""Transcription service using faster-whisper."""

import asyncio
import json
import os

from faster_whisper import WhisperModel

from app.config import settings

# Global model instance for reuse
_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        # For CPU-only, we use int8 quantization
        # Using a small or base model is recommended for CPU performance
        _whisper_model = WhisperModel(
            settings.whisper_model, 
            device="cpu", 
            compute_type="int8"
        )
    return _whisper_model


async def transcribe_audio(audio_path: str, output_path: str, language: str | None = None) -> str:
    """
    Transcribe audio file to JSON containing word-level timestamps.
    Returns path to the saved JSON transcript.
    """
    if os.path.exists(output_path):
        # Already transcribed
        return output_path

    def _transcribe():
        model = _get_model()
        
        # Word timestamps are essential for karaoke captions and reframing
        segments_gen, info = model.transcribe(
            audio_path, 
            word_timestamps=True,
            language=language if language and language != "auto" else None,
            vad_filter=True, # Use silero VAD to skip silence
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        segments = []
        for segment in segments_gen:
            words = []
            if segment.words:
                for word in segment.words:
                    words.append({
                        "word": word.word,
                        "start": word.start,
                        "end": word.end,
                        "probability": word.probability
                    })
            
            segments.append({
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "words": words
            })
            
        transcript_data = {
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": segments
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
        return output_path

    result = await asyncio.to_thread(_transcribe)
    return result
