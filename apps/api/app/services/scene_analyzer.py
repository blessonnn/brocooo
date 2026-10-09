"""Scene analysis using PySceneDetect and MediaPipe Face Detection."""

import asyncio
import json
import os

import cv2
import mediapipe as mp
from scenedetect import ContentDetector, detect


class SceneError(Exception):
    pass


async def analyze_scenes(video_path: str, output_path: str) -> str:
    """
    Detect scenes (cuts) and track faces throughout the video.
    Returns path to the saved JSON analysis.
    """
    if os.path.exists(output_path):
        return output_path

    def _analyze():
        try:
            # 1. Scene detection
            scene_list = detect(video_path, ContentDetector(threshold=27.0))
            scenes = [
                {"start_time": s.get_seconds(), "end_time": e.get_seconds()}
                for s, e in scene_list
            ]
            if not scenes:
                # If no cuts detected, treat whole video as one scene
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                duration = frames / fps if fps > 0 else 0
                cap.release()
                scenes = [{"start_time": 0.0, "end_time": duration}]

            # 2. Face tracking (sampled at 1 fps for speed)
            face_tracking = []
            
            mp_face_detection = mp.solutions.face_detection
            with mp_face_detection.FaceDetection(
                model_selection=1, # 1 for full-range (far faces)
                min_detection_confidence=0.5
            ) as face_detection:
                
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = 0
                
                while cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        break
                        
                    # Process 1 frame per second
                    if frame_count % int(fps) == 0:
                        timestamp = frame_count / fps
                        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        results = face_detection.process(image_rgb)
                        
                        faces = []
                        if results.detections:
                            for detection in results.detections:
                                bbox = detection.location_data.relative_bounding_box
                                faces.append({
                                    "x": bbox.xmin,
                                    "y": bbox.ymin,
                                    "width": bbox.width,
                                    "height": bbox.height,
                                    "score": detection.score[0] if detection.score else 0.0
                                })
                        
                        face_tracking.append({
                            "time": timestamp,
                            "faces": faces
                        })
                        
                    frame_count += 1
                
                cap.release()

            analysis_data = {
                "scenes": scenes,
                "face_tracking": face_tracking
            }

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)

            return output_path

        except Exception as e:
            raise SceneError(f"Scene analysis failed: {e}")

    return await asyncio.to_thread(_analyze)
