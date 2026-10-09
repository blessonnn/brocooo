"""Reframing logic (calculating crops for 9:16)."""

import json


def calculate_crop_plan(scenes_path: str, clip_start: float, clip_end: float, layout: str) -> list[dict]:
    """
    Generate a pan/crop plan for a specific clip based on face tracking data.
    Returns a list of segments with target X center (0.0 to 1.0).
    """
    with open(scenes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    face_tracking = data.get("face_tracking", [])
    
    # Filter tracking points within our clip
    clip_tracking = [pt for pt in face_tracking if clip_start <= pt["time"] <= clip_end]
    
    plan = []
    
    if not clip_tracking:
        # Default center crop if no data
        plan.append({
            "start": clip_start,
            "end": clip_end,
            "x_center": 0.5
        })
        return plan

    # Simple EMA (Exponential Moving Average) smoothing for camera tracking
    # MVP: we just find the dominant face in each tracking point and smooth the x coordinate.
    
    smoothed_x = 0.5
    alpha = 0.2  # Smoothing factor
    
    for i, pt in enumerate(clip_tracking):
        time = pt["time"]
        faces = pt["faces"]
        
        target_x = 0.5
        if faces:
            # Pick the largest face (most likely the speaker)
            best_face = max(faces, key=lambda f: f["width"] * f["height"])
            target_x = best_face["x"] + (best_face["width"] / 2)
            
            # Bound the target so the 9:16 crop window doesn't go off-screen.
            # A 9:16 crop from 16:9 source takes up 9/16 = 0.5625 of the width.
            # So the center can only move between roughly 0.28 and 0.72.
            target_x = max(0.28, min(0.72, target_x))
            
        if i == 0:
            smoothed_x = target_x
        else:
            smoothed_x = (alpha * target_x) + ((1 - alpha) * smoothed_x)
            
        # Determine the end time for this plan segment
        end_time = clip_tracking[i+1]["time"] if i + 1 < len(clip_tracking) else clip_end
        
        plan.append({
            "start": time,
            "end": end_time,
            "x_center": round(smoothed_x, 3)
        })
        
    return plan
