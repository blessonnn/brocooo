"""ASS Subtitle Generator."""

import json
import os


def hex_to_ass_color(hex_color: str) -> str:
    """Convert #RRGGBB to ASS format &HBBGGRR&."""
    if hex_color == "transparent":
        return "&H00000000&" # Transparent
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        # RGB -> BGR
        bgr = hex_color[4:6] + hex_color[2:4] + hex_color[0:2]
        return f"&H00{bgr}&"
    elif len(hex_color) == 8:
        # ARGB -> ABGR (ASS uses AABBGGRR where 00 is opaque and FF is transparent)
        # Note: hex alpha is usually 00 transparent, FF opaque. ASS is flipped.
        # For simplicity, we just handle RGB.
        return "&H00FFFFFF&"
    return "&H00FFFFFF&"


def generate_ass(
    transcript_path: str,
    clip_start: float,
    clip_end: float,
    style_json_path: str,
    output_ass_path: str
) -> str:
    """
    Generate an ASS subtitle file for a specific clip timeframe.
    """
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)
        
    with open(style_json_path, "r", encoding="utf-8") as f:
        style = json.load(f)

    # Base ASS styling based on the JSON
    font_family = style.get("font", {}).get("family", "Arial")
    font_size = style.get("font", {}).get("size", 24)
    bold = -1 if style.get("font", {}).get("weight", 400) >= 700 else 0
    italic = -1 if style.get("font", {}).get("italic", False) else 0
    
    primary_color = hex_to_ass_color(style.get("colors", {}).get("fill", "#FFFFFF"))
    outline_color = hex_to_ass_color(style.get("colors", {}).get("stroke", "#000000"))
    outline_width = style.get("colors", {}).get("strokeWidth", 2)
    
    # Simple top/bottom mapping
    alignment = 2 # Bottom center (ASS: 1=BL, 2=BC, 3=BR, 4=ML, 5=MC, 6=MR, 7=TL, 8=TC, 9=TR)
    pos = style.get("position", {})
    if pos.get("vertical") == "center":
        alignment = 5
    elif pos.get("vertical") == "top":
        alignment = 8

    margin_v = pos.get("marginBottom", 100)

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_family},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,{bold},{italic},0,0,100,100,0,0,1,{outline_width},0,{alignment},10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def format_time(seconds: float) -> str:
        # Format: H:MM:SS.cs (centiseconds)
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    events = []
    
    # Filter words in this clip
    clip_words = []
    for seg in transcript.get("segments", []):
        for word in seg.get("words", []):
            if clip_start <= word["start"] and word["end"] <= clip_end:
                clip_words.append(word)

    # Group words into lines (e.g. 4 words per line)
    words_per_line = style.get("display", {}).get("wordsPerLine", 4)
    uppercase = style.get("font", {}).get("uppercase", False)
    
    current_line = []
    
    def emit_line(line_words):
        if not line_words: return
        start_t = format_time(line_words[0]["start"] - clip_start)
        end_t = format_time(line_words[-1]["end"] - clip_start)
        
        # Build text string (basic version - no karaoke tags yet for Phase 1)
        text_parts = []
        for w in line_words:
            t = w["word"].strip()
            if uppercase: t = t.upper()
            text_parts.append(t)
            
        text = " ".join(text_parts)
        events.append(f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{text}")

    for word in clip_words:
        current_line.append(word)
        if len(current_line) >= words_per_line:
            emit_line(current_line)
            current_line = []
            
    if current_line:
        emit_line(current_line)

    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))
        
    return output_ass_path
