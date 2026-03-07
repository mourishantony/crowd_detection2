import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "crowd-detection-secret-key-2026"

# Admin credentials
ADMIN_USERNAME = "kgadmin"
ADMIN_PASSWORD = "kgadmin@2026"

# Paths
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MODELS_FOLDER = os.path.join(BASE_DIR, "models")

# Detection model paths
YOLO_MODEL = os.path.join(MODELS_FOLDER, "yolov8n.pt")
YUNET_MODEL = os.path.join(MODELS_FOLDER, "face_detection_yunet_2023mar.onnx")
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"

# Allowed image extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp", "tiff", "heic", "heif"}


