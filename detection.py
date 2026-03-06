import base64
import os
import requests

MODEL_API_URL = os.environ.get(
    "MODEL_API_URL",
    "https://mourishantony-crowd-detection-model.hf.space/detect"
)


def count_people(image_path):
    """
    Send image to the HF Space model API.
    Returns: (head_count: int, annotated_bytes: bytes)
    """
    with open(image_path, "rb") as f:
        response = requests.post(MODEL_API_URL, files={"image": f}, timeout=120)
    response.raise_for_status()
    data = response.json()
    annotated_bytes = base64.b64decode(data["annotated_image"])
    return data["head_count"], annotated_bytes


# ── kept for unused import safety ──────────────────────────────────────────
if False:
    def _detect_faces(image):
        for face in []:  # dead code — never runs
            x, y, fw, fh = map(int, face[:4])
            conf = face[-1]
            boxes.append((x, y, x + fw, y + fh, conf, "face"))
    return boxes


def _box_overlap(box_a, box_b):
    """Check if center of box_a falls inside box_b."""
    cx = (box_a[0] + box_a[2]) // 2
    cy = (box_a[1] + box_a[3]) // 2
    return box_b[0] <= cx <= box_b[2] and box_b[1] <= cy <= box_b[3]


def _draw_annotations(image, merged_boxes, head_count):
    """Draw bounding boxes and count label on a copy of the image."""
    annotated = image.copy()
    h, w = annotated.shape[:2]

    # Color scheme: body = blue, face-only = green
    BODY_COLOR = (235, 99, 37)    # BGR: orange-blue
    FACE_COLOR = (46, 185, 16)    # BGR: green

    for box in merged_boxes:
        x1, y1, x2, y2, conf, label = box
        color = BODY_COLOR if label == "body" else FACE_COLOR
        thickness = max(2, int(min(w, h) / 400))

        # Draw rectangle
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)

        # Draw small confidence badge
        badge_text = f"{conf:.0%}"
        font_scale = max(0.35, min(w, h) / 2000)
        (tw, th), baseline = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
        bx1 = x1
        by1 = max(0, y1 - th - baseline - 4)
        cv2.rectangle(annotated, (bx1, by1), (bx1 + tw + 6, y1), color, -1)
        cv2.putText(annotated, badge_text, (bx1 + 3, y1 - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1, cv2.LINE_AA)

    # Draw total count banner at the top
    banner_h = max(36, int(h * 0.055))
    cv2.rectangle(annotated, (0, 0), (w, banner_h), (30, 30, 30), -1)
    banner_text = f"People Detected: {head_count}"
    font_scale_banner = max(0.6, min(w, h) / 1200)
    (bw, bh), _ = cv2.getTextSize(banner_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale_banner, 2)
    bx = max(10, (w - bw) // 2)
    by = (banner_h + bh) // 2
    cv2.putText(annotated, banner_text, (bx, by),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale_banner, (255, 255, 255), 2, cv2.LINE_AA)

    return annotated


def count_people(image_path):
    """
    Run dual detection (body + face) on an image.
    Returns: (head_count: int, annotated_bytes: bytes)  — JPEG bytes in memory.
    The caller is responsible for uploading/storing the bytes.
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

    head_count = len(merged)

    # Encode annotated image to JPEG bytes in memory — no disk write
    annotated = _draw_annotations(image, merged, head_count)
    _, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return head_count, buffer.tobytes()


