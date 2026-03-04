import cv2
import os
import urllib.request
import numpy as np
import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO

# Open file explorer to select an image
tk.Tk().withdraw()
image_path = filedialog.askopenfilename(
    title="Select an image",
    filetypes=[
        ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff"),
        ("All files", "*.*")
    ]
)

if not image_path:
    print("No image selected. Exiting.")
    exit()

print(f"Selected: {image_path}")

image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError("Could not load image")

h, w = image.shape[:2]

# ---- METHOD 1: YOLOv8m person detection (front, back, side) ----
print("Running person body detection...")
model = YOLO("yolov8m.pt")  # medium model — much better for small/distant people
body_results = model(image, conf=0.25, iou=0.5, classes=[0], verbose=False,
                     imgsz=1280)  # higher resolution for distant people
body_boxes = []
for box in body_results[0].boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    conf = box.conf[0].item()
    body_boxes.append((x1, y1, x2, y2, conf, "body"))

# ---- METHOD 2: YuNet face detection (catches faces YOLOv8 might miss) ----
print("Running face detection...")
FACE_MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
FACE_MODEL_PATH = "face_detection_yunet_2023mar.onnx"

if not os.path.exists(FACE_MODEL_PATH):
    print("Downloading YuNet face detection model...")
    urllib.request.urlretrieve(FACE_MODEL_URL, FACE_MODEL_PATH)
    print("Download complete.")

face_detector = cv2.FaceDetectorYN.create(
    FACE_MODEL_PATH, "", (w, h),
    score_threshold=0.5, nms_threshold=0.3, top_k=5000
)
_, faces = face_detector.detect(image)

face_boxes = []
if faces is not None:
    for face in faces:
        x, y, fw, fh = map(int, face[:4])
        conf = face[-1]
        face_boxes.append((x, y, x + fw, y + fh, conf, "face"))


# ---- MERGE: combine both, remove duplicates ----
def box_overlap(box_a, box_b):
    """Check if center of box_a falls inside box_b"""
    cx = (box_a[0] + box_a[2]) // 2
    cy = (box_a[1] + box_a[3]) // 2
    return box_b[0] <= cx <= box_b[2] and box_b[1] <= cy <= box_b[3]


# Start with all body detections
merged = list(body_boxes)

# Add face detections that don't overlap with any body detection
for fb in face_boxes:
    already_covered = False
    for bb in body_boxes:
        if box_overlap(fb, bb):
            already_covered = True
            break
    if not already_covered:
        merged.append(fb)

total_count = len(merged)

print(f"\nBody detections: {len(body_boxes)}")
print(f"Face-only detections (not covered by body): {len(merged) - len(body_boxes)}")
print(f"Total humans detected: {total_count}")

for i, (x1, y1, x2, y2, conf, method) in enumerate(merged):
    color = (0, 255, 0) if method == "body" else (255, 165, 0)  # green=body, orange=face-only
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    cv2.putText(image, f"#{i+1} {conf:.2f}", (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Add total count on the image
cv2.putText(image, f"Total: {total_count}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

cv2.imwrite("output.jpg", image)
print("Result saved to output.jpg")