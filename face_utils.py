"""
face_utils.py
-------------
Wraps DeepFace (FaceNet model) + MTCNN detector + OpenCV for:
  - detecting faces in a frame
  - generating embeddings
  - matching a captured face against the registered "known_faces" gallery

DeepFace internally downloads and caches the FaceNet weights on first run.
"""

import os
import cv2
import numpy as np
from deepface import DeepFace

KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), "known_faces")
MODEL_NAME = "Facenet"          # FaceNet embedding model
DETECTOR_BACKEND = "mtcnn"      # MTCNN face detector
DISTANCE_METRIC = "cosine"
# Empirically reasonable threshold for Facenet + cosine distance
RECOGNITION_THRESHOLD = 0.40


def ensure_dirs():
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)


def save_face_image(student_id, image_bgr):
    """Save a registered student's face image to disk; returns the path."""
    ensure_dirs()
    path = os.path.join(KNOWN_FACES_DIR, f"{student_id}.jpg")
    cv2.imwrite(path, image_bgr)
    return path


def detect_face(image_bgr):
    """
    Detect the largest face in a BGR image.
    Returns the cropped face (BGR) and bounding box (x, y, w, h), or (None, None).
    """
    try:
        faces = DeepFace.extract_faces(
            img_path=image_bgr,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            align=True,
        )
    except Exception:
        return None, None

    if not faces:
        return None, None

    # Pick the face with the largest area
    best = max(faces, key=lambda f: f["facial_area"]["w"] * f["facial_area"]["h"])
    area = best["facial_area"]
    x, y, w, h = area["x"], area["y"], area["w"], area["h"]
    cropped = image_bgr[max(0, y):y + h, max(0, x):x + w]
    return cropped, (x, y, w, h)


def recognize_face(image_bgr):
    """
    Compare the face in `image_bgr` against every image in KNOWN_FACES_DIR.
    Returns (student_id, distance) for the best match below threshold,
    or (None, None) if no good match is found.
    """
    ensure_dirs()
    gallery = [f for f in os.listdir(KNOWN_FACES_DIR) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    if not gallery:
        return None, None

    best_match = None
    best_distance = float("inf")

    for filename in gallery:
        candidate_path = os.path.join(KNOWN_FACES_DIR, filename)
        try:
            result = DeepFace.verify(
                img1_path=image_bgr,
                img2_path=candidate_path,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR_BACKEND,
                distance_metric=DISTANCE_METRIC,
                enforce_detection=True,
            )
        except Exception:
            continue

        distance = result["distance"]
        if distance < best_distance:
            best_distance = distance
            best_match = os.path.splitext(filename)[0]  # student_id

    if best_match is not None and best_distance <= RECOGNITION_THRESHOLD:
        return best_match, best_distance
    return None, best_distance


def draw_box(image_bgr, box, label=""):
    """Draw a bounding box + label on the image (for UI feedback)."""
    if box is None:
        return image_bgr
    x, y, w, h = box
    cv2.rectangle(image_bgr, (x, y), (x + w, y + h), (0, 200, 0), 2)
    if label:
        cv2.putText(image_bgr, label, (x, max(0, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
    return image_bgr


def bytes_to_bgr(image_bytes):
    """Convert raw image bytes (e.g. from Streamlit camera input) to OpenCV BGR array."""
    arr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def image_to_jpg_bytes(image_bgr):
    """Convert an OpenCV BGR image into JPG bytes (for saving to database)."""
    success, buf = cv2.imencode(".jpg", image_bgr)
    return buf.tobytes() if success else None
