# IPS Tech Community ิว๖ Crowd Detection System

A Flask web application that counts people in images using YOLOv8 object detection and YuNet face detection. Annotated images are stored permanently on Cloudinary, and all records are persisted in MongoDB Atlas ิว๖ surviving across deployments.

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

- **Dual detection engine** ิว๖ YOLOv8m for full-body detection (any angle) + YuNet for face detection (catches people partially obscured)
- **Upload or capture** ิว๖ users can upload an image file or take a photo directly from their device camera
- **Annotated output** ิว๖ bounding boxes, confidence badges, and a people-count banner are drawn on every processed image
- **Cloud storage** ิว๖ annotated images uploaded to Cloudinary CDN; URLs stored permanently in MongoDB Atlas
- **Admin dashboard** ิว๖ analytics (totals, averages, per-event stats, daily chart), photo gallery with lightbox, place management, record editing
- **Place management** ิว๖ create, rename, and delete places/events from the admin panel
- **Persistent across deploys** ิว๖ MongoDB Atlas stores all records and events; Cloudinary stores all images

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
ิ๖้
ิ๖ฃิ๖วิ๖ว app.py                  # Flask routes and application logic
ิ๖ฃิ๖วิ๖ว detection.py            # YOLO + YuNet detection pipeline
ิ๖ฃิ๖วิ๖ว db.py                   # MongoDB Atlas access layer
ิ๖ฃิ๖วิ๖ว config.py               # App configuration and constants
ิ๖ฃิ๖วิ๖ว requirements.txt        # Python dependencies
ิ๖ฃิ๖วิ๖ว Dockerfile              # Container definition for Render
ิ๖้
ิ๖ฃิ๖วิ๖ว models/
ิ๖้   ิ๖ฃิ๖วิ๖ว yolov8m.pt                          # YOLOv8 medium model (body detection)
ิ๖้   ิ๖๖ิ๖วิ๖ว face_detection_yunet_2023mar.onnx   # YuNet model (face detection)
ิ๖้
ิ๖ฃิ๖วิ๖ว static/
ิ๖้   ิ๖ฃิ๖วิ๖ว css/style.css       # Application styles
ิ๖้   ิ๖๖ิ๖วิ๖ว js/
ิ๖้       ิ๖ฃิ๖วิ๖ว camera.js       # Camera capture logic
ิ๖้       ิ๖๖ิ๖วิ๖ว dialogs.js      # Upload form dialogs
ิ๖้
ิ๖ฃิ๖วิ๖ว templates/
ิ๖้   ิ๖ฃิ๖วิ๖ว base.html           # Base layout with navbar
ิ๖้   ิ๖ฃิ๖วิ๖ว upload.html         # Public upload page
ิ๖้   ิ๖๖ิ๖วิ๖ว admin/
ิ๖้       ิ๖ฃิ๖วิ๖ว login.html      # Admin login
ิ๖้       ิ๖ฃิ๖วิ๖ว dashboard.html  # Analytics dashboard
ิ๖้       ิ๖ฃิ๖วิ๖ว photos.html     # Photo gallery with lightbox
ิ๖้       ิ๖ฃิ๖วิ๖ว places.html     # Place management
ิ๖้       ิ๖๖ิ๖วิ๖ว edit_record.html
ิ๖้
ิ๖๖ิ๖วิ๖ว uploads/                # Temporary folder (files deleted after detection)
```

---

## How It Works

### Detection Pipeline

```
User uploads image
       ิ๖้
       ิ๛+
Saved temporarily to disk (uploads/)
       ิ๖้
       ิ๛+
YOLOv8m ิว๖ detects full bodies (conf ิ๋ั 0.25, imgsz=640)
       ิ๖้
       ิ๛+
YuNet ิว๖ detects faces (catches partially visible people)
       ิ๖้
       ิ๛+
Merge results ิว๖ face detections already covered by a body box are dropped
       ิ๖้
       ิ๛+
Draw bounding boxes + confidence badges + people count banner
       ิ๖้
       ิ๛+
Encode annotated image to JPEG bytes (in memory ิว๖ no disk write)
       ิ๖้
       ิ๛+
Delete original temp file from disk
       ิ๖้
       ิ๛+
Upload annotated bytes ิๅฦ Cloudinary (permanent CDN URL)
       ิ๖้
       ิ๛+
Save record (event, count, Cloudinary URL, timestamp) ิๅฦ MongoDB Atlas
```

### Model Caching

The YOLOv8 model is loaded **once** at application startup into a module-level singleton (`_yolo_model`). Subsequent requests reuse the cached model ิว๖ no disk I/O per request.

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

1. Go to [render.com](https://render.com) ิๅฦ **New ิๅฦ Web Service**
2. Connect your GitHub repository
3. Render auto-detects the `Dockerfile`

### 3. Add environment variables on Render

In your service ิๅฦ **Environment** tab, add all four variables from the table above.

### 4. Deploy

Render will build the Docker image and deploy automatically on every push to `main`.

The `Dockerfile` runs:
```
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

- `--workers 1` ิว๖ prevents two workers loading the 50MB PyTorch model simultaneously (RAM limit on free tier)
- `--timeout 120` ิว๖ allows 120 seconds for the first request (model loads once on first upload)

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

- The original uploaded image is **never stored permanently** ิว๖ it is deleted from disk immediately after detection runs
- Only the annotated image (with bounding boxes drawn) is stored, on Cloudinary
- MongoDB stores: event name, Cloudinary URL, Cloudinary public ID (for deletion), head count, and timestamp
- The `uploads/` folder is used only as a temporary scratch space during detection
