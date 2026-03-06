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
