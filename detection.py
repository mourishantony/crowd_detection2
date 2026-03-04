import cv2
import os
import urllib.request
from ultralytics import YOLO
import config


def _ensure_yunet_model():
    """Download YuNet model if not present."""
    if not os.path.exists(config.YUNET_MODEL):
        os.makedirs(config.MODELS_FOLDER, exist_ok=True)
        print("Downloading YuNet face detection model...")
        urllib.request.urlretrieve(config.YUNET_URL, config.YUNET_MODEL)
        print("Download complete.")


def _detect_bodies(image):
    """Detect people using YOLOv8m (works from any angle)."""
    model = YOLO(config.YOLO_MODEL)
    results = model(image, conf=0.25, iou=0.5, classes=[0], verbose=False, imgsz=1280)
    boxes = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = box.conf[0].item()
        boxes.append((x1, y1, x2, y2, conf, "body"))
    return boxes


def _detect_faces(image):
    """Detect faces using YuNet (catches front-facing people body detection may miss)."""
    _ensure_yunet_model()
    h, w = image.shape[:2]
    detector = cv2.FaceDetectorYN.create(
        config.YUNET_MODEL, "", (w, h),
        score_threshold=0.5, nms_threshold=0.3, top_k=5000
    )
    _, faces = detector.detect(image)
    boxes = []
    if faces is not None:
        for face in faces:
            x, y, fw, fh = map(int, face[:4])
            conf = face[-1]
            boxes.append((x, y, x + fw, y + fh, conf, "face"))
    return boxes


def _box_overlap(box_a, box_b):
    """Check if center of box_a falls inside box_b."""
    cx = (box_a[0] + box_a[2]) // 2
    cy = (box_a[1] + box_a[3]) // 2
    return box_b[0] <= cx <= box_b[2] and box_b[1] <= cy <= box_b[3]


def count_people(image_path):
    """
    Run dual detection (body + face) on an image.
    Returns: head count (int)
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    # Run both detectors
    body_boxes = _detect_bodies(image)
    face_boxes = _detect_faces(image)

    # Merge: keep all body detections, add face-only detections
    merged = list(body_boxes)
    for fb in face_boxes:
        already_covered = any(_box_overlap(fb, bb) for bb in body_boxes)
        if not already_covered:
            merged.append(fb)

    return len(merged)
