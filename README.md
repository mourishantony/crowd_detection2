# Phoenix — Crowd Detection System

A Flask web application that counts people in images using YOLOv8 object detection and YuNet face detection. Annotated images are stored permanently on Cloudinary, and all records are persisted in MongoDB Atlas — surviving across deployments.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Deploying to Render](#deploying-to-render)
- [Admin Panel](#admin-panel)
- [API Reference](#api-reference)

---

## Features

- **Dual detection engine** — YOLOv8m for full-body detection (any angle) + YuNet for face detection (catches people partially obscured)
- **Upload or capture** — users can upload an image file or take a photo directly from their device camera
- **Annotated output** — bounding boxes, confidence badges, and a people-count banner are drawn on every processed image
- **Cloud storage** — annotated images uploaded to Cloudinary CDN; URLs stored permanently in MongoDB Atlas
- **Admin dashboard** — analytics (totals, averages, per-event stats, daily chart), photo gallery with lightbox, place management, record editing
- **Place management** — create, rename, and delete places/events from the admin panel
- **Persistent across deploys** — MongoDB Atlas stores all records and events; Cloudinary stores all images

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3.0 |
| Production server | Gunicorn 22 |
| Body detection | YOLOv8m (Ultralytics) |
| Face detection | YuNet (OpenCV) |
| Deep learning backend | PyTorch 2.2.2 |
| Image processing | OpenCV (headless), Pillow |
| Database | MongoDB Atlas (pymongo) |
| Image CDN | Cloudinary |
| Deployment | Render (Docker) |

---

## Project Structure

```
crowd_detection2/
│
├── app.py                  # Flask routes and application logic
├── detection.py            # YOLO + YuNet detection pipeline
├── db.py                   # MongoDB Atlas access layer
├── config.py               # App configuration and constants
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition for Render
│
├── models/
│   ├── yolov8m.pt                          # YOLOv8 medium model (body detection)
│   └── face_detection_yunet_2023mar.onnx   # YuNet model (face detection)
│
├── static/
│   ├── css/style.css       # Application styles
│   └── js/
│       ├── camera.js       # Camera capture logic
│       └── dialogs.js      # Upload form dialogs
│
├── templates/
│   ├── base.html           # Base layout with navbar
│   ├── upload.html         # Public upload page
│   └── admin/
│       ├── login.html      # Admin login
│       ├── dashboard.html  # Analytics dashboard
│       ├── photos.html     # Photo gallery with lightbox
│       ├── places.html     # Place management
│       └── edit_record.html
│
└── uploads/                # Temporary folder (files deleted after detection)
```

---

## How It Works

### Detection Pipeline

```
User uploads image
       │
       ▼
Saved temporarily to disk (uploads/)
       │
       ▼
YOLOv8m — detects full bodies (conf ≥ 0.25, imgsz=640)
       │
       ▼
YuNet — detects faces (catches partially visible people)
       │
       ▼
Merge results — face detections already covered by a body box are dropped
       │
       ▼
Draw bounding boxes + confidence badges + people count banner
       │
       ▼
Encode annotated image to JPEG bytes (in memory — no disk write)
       │
       ▼
Delete original temp file from disk
       │
       ▼
Upload annotated bytes → Cloudinary (permanent CDN URL)
       │
       ▼
Save record (event, count, Cloudinary URL, timestamp) → MongoDB Atlas
```

### Model Caching

The YOLOv8 model is loaded **once** at application startup into a module-level singleton (`_yolo_model`). Subsequent requests reuse the cached model — no disk I/O per request.

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- A [MongoDB Atlas](https://www.mongodb.com/atlas) free cluster
- A [Cloudinary](https://cloudinary.com) free account

### 1. Clone and create virtual environment

```bash
git clone https://github.com/mourishantony/crowd_detection2.git
cd crowd_detection2
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the project root (never commit this):

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Then load it before running:

```bash
# Windows PowerShell
$env:MONGODB_URI="mongodb+srv://..."
$env:CLOUDINARY_CLOUD_NAME="..."
$env:CLOUDINARY_API_KEY="..."
$env:CLOUDINARY_API_SECRET="..."
```

### 4. Run the app

```bash
python app.py
```

Visit `http://localhost:5000`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URI` | Yes | MongoDB Atlas connection string (SRV format) |
| `CLOUDINARY_CLOUD_NAME` | Yes | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Yes | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Yes | Cloudinary API secret |

---

## Deploying to Render

### 1. Push your code to GitHub

```bash
git add .
git commit -m "your message"
git push
```

### 2. Create a Render Web Service

1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repository
3. Render auto-detects the `Dockerfile`

### 3. Add environment variables on Render

In your service → **Environment** tab, add all four variables from the table above.

### 4. Deploy

Render will build the Docker image and deploy automatically on every push to `main`.

The `Dockerfile` runs:
```
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

- `--workers 1` — prevents two workers loading the 50MB PyTorch model simultaneously (RAM limit on free tier)
- `--timeout 120` — allows 120 seconds for the first request (model loads once on first upload)

---

## Admin Panel

Access at `/admin` with the credentials configured in `config.py`.

| Page | URL | Description |
|---|---|---|
| Login | `/admin` | Admin authentication |
| Dashboard | `/admin/dashboard` | Analytics, recent uploads, daily chart |
| Photos | `/admin/photos` | Gallery with lightbox, filter by place, delete |
| Places | `/admin/places` | Add, rename, delete places/events |

Default credentials (change in `config.py` before deploying):
```
Username: kgadmin
Password: kgadmin@2026
```

---

## API Reference

### `POST /upload`

Upload an image for crowd detection.

**Form fields:**

| Field | Type | Description |
|---|---|---|
| `place` | string | Event/place name (new places are created automatically) |
| `image` | file | Image file (JPG, PNG, BMP, WEBP, TIFF) |

**Success response:**
```json
{
  "success": true,
  "head_count": 42,
  "event": "Ground"
}
```

**Error response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Notes

- The original uploaded image is **never stored permanently** — it is deleted from disk immediately after detection runs
- Only the annotated image (with bounding boxes drawn) is stored, on Cloudinary
- MongoDB stores: event name, Cloudinary URL, Cloudinary public ID (for deletion), head count, and timestamp
- The `uploads/` folder is used only as a temporary scratch space during detection
