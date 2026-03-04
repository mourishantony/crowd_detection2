import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "crowd-detection-secret-key-2026"

# Admin credentials
ADMIN_USERNAME = "kgadmin"
ADMIN_PASSWORD = "kgadmin@2026"

# Default events (used on first run)
DEFAULT_EVENTS = ["Place 1", "Place 2", "Place 3"]

# Paths
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MODELS_FOLDER = os.path.join(BASE_DIR, "models")
DATA_FILE = os.path.join(BASE_DIR, "data.json")
EVENTS_FILE = os.path.join(BASE_DIR, "events.json")

# Detection model paths
YOLO_MODEL = os.path.join(MODELS_FOLDER, "yolov8m.pt")
YUNET_MODEL = os.path.join(MODELS_FOLDER, "face_detection_yunet_2023mar.onnx")
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"

# Allowed image extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp", "tiff"}


def load_events():
    """Load events from JSON file, or create with defaults."""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    save_events(DEFAULT_EVENTS)
    return DEFAULT_EVENTS


def save_events(events):
    """Save events list to JSON file."""
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)
