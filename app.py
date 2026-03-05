import os
import json
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import config
from detection import count_people

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Ensure folders exist
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
for event in config.load_events():
    os.makedirs(os.path.join(config.UPLOAD_FOLDER, event.replace(" ", "_").lower()), exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS


def load_data():
    if os.path.exists(config.DATA_FILE):
        with open(config.DATA_FILE, "r") as f:
            records = json.load(f)
        # Ensure all records have an 'id' field
        updated = False
        for i, record in enumerate(records):
            if "id" not in record:
                record["id"] = i + 1
                updated = True
        if updated:
            # Find max id and re-assign to avoid conflicts
            max_id = max((r.get("id", 0) for r in records), default=0)
            for i, record in enumerate(records):
                if record.get("id", 0) <= 0:
                    max_id += 1
                    record["id"] = max_id
            save_data(records)
        return records
    return []


def save_data(records):
    with open(config.DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)


# ────────────── Common User Routes ──────────────

@app.route("/")
def index():
    events = config.load_events()
    return render_template("upload.html", events=events)


@app.route("/upload", methods=["POST"])
def upload():
    events = config.load_events()
    place = request.form.get("place", "").strip()
    
    if not place:
        return jsonify({"success": False, "error": "Please enter a place name."}), 400
    
    # Add to events list if new place
    if place not in events:
        events.append(place)
        config.save_events(events)
    
    event = place

    file = request.files.get("image")
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No image selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file type. Use JPG, PNG, BMP, or WEBP."}), 400

    # Save uploaded image
    event_folder = event.replace(" ", "_").lower()
    upload_dir = os.path.join(config.UPLOAD_FOLDER, event_folder)
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{secure_filename(file.filename)}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Run detection
    try:
        head_count, annotated_filename = count_people(filepath)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    # Save record
    records = load_data()
    records.append({
        "id": len(records) + 1,
        "event": event,
        "filename": filename,
        "annotated_filename": annotated_filename,
        "filepath": filepath,
        "head_count": head_count,
        "timestamp": datetime.now().isoformat()
    })
    save_data(records)

    return jsonify({"success": True, "head_count": head_count, "event": event})


@app.route("/uploads/<event_folder>/<filename>")
def uploaded_file(event_folder, filename):
    return send_from_directory(os.path.join(config.UPLOAD_FOLDER, event_folder), filename)


# ────────────── Admin Routes ──────────────

def admin_required(f):
    """Decorator to protect admin routes."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials.", "error")

    return render_template("admin/login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    records = load_data()
    events = config.load_events()

    # Analytics
    total_uploads = len(records)
    total_people = sum(r["head_count"] for r in records)
    avg_count = round(total_people / total_uploads, 1) if total_uploads > 0 else 0
    max_count = max((r["head_count"] for r in records), default=0)
    min_count = min((r["head_count"] for r in records), default=0)

    # Per-event analytics
    event_stats = {}
    for event in events:
        event_records = [r for r in records if r["event"] == event]
        count = len(event_records)
        total = sum(r["head_count"] for r in event_records)
        event_stats[event] = {
            "uploads": count,
            "total_people": total,
            "avg_count": round(total / count, 1) if count > 0 else 0,
            "max_count": max((r["head_count"] for r in event_records), default=0),
        }

    # Recent uploads (last 10)
    recent = list(reversed(records[-10:]))

    # Daily upload counts (for chart)
    daily_counts = {}
    for r in records:
        day = r["timestamp"][:10]
        daily_counts[day] = daily_counts.get(day, 0) + 1

    return render_template("admin/dashboard.html",
                           records=records, events=events,
                           total_uploads=total_uploads,
                           total_people=total_people,
                           avg_count=avg_count,
                           max_count=max_count,
                           min_count=min_count,
                           event_stats=event_stats,
                           recent=recent,
                           daily_counts=daily_counts)


@app.route("/admin/photos")
@admin_required
def admin_photos():
    records = load_data()
    events = config.load_events()
    selected_event = request.args.get("event", "all")

    if selected_event != "all":
        filtered = [r for r in records if r["event"] == selected_event]
    else:
        filtered = records

    # Add image URL and annotated URL to each record
    for r in filtered:
        event_folder = r["event"].replace(" ", "_").lower()
        r["image_url"] = url_for("uploaded_file",
                                  event_folder=event_folder,
                                  filename=r["filename"])
        ann = r.get("annotated_filename")
        r["annotated_url"] = url_for("uploaded_file",
                                      event_folder=event_folder,
                                      filename=ann) if ann else r["image_url"]

    return render_template("admin/photos.html",
                           records=list(reversed(filtered)),
                           events=events,
                           selected_event=selected_event)


@app.route("/admin/places")
@admin_required
def admin_places():
    events = config.load_events()
    records = load_data()

    # Count uploads per place
    place_counts = {}
    for event in events:
        place_counts[event] = len([r for r in records if r["event"] == event])

    return render_template("admin/places.html",
                           events=events, place_counts=place_counts)


@app.route("/admin/places/add", methods=["POST"])
@admin_required
def admin_add_place():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Place name cannot be empty.", "error")
        return redirect(url_for("admin_places"))

    events = config.load_events()
    if name in events:
        flash("Place already exists.", "error")
        return redirect(url_for("admin_places"))

    events.append(name)
    config.save_events(events)
    os.makedirs(os.path.join(config.UPLOAD_FOLDER, name.replace(" ", "_").lower()), exist_ok=True)
    flash(f"Place '{name}' added successfully.", "success")
    return redirect(url_for("admin_places"))


@app.route("/admin/places/delete/<int:index>", methods=["POST"])
@admin_required
def admin_delete_place(index):
    events = config.load_events()
    if 0 <= index < len(events):
        removed = events.pop(index)
        config.save_events(events)
        flash(f"Place '{removed}' deleted.", "success")
    return redirect(url_for("admin_places"))


@app.route("/admin/places/rename", methods=["POST"])
@admin_required
def admin_rename_place():
    old_name = request.form.get("old_name", "").strip()
    new_name = request.form.get("new_name", "").strip()

    if not new_name:
        flash("New name cannot be empty.", "error")
        return redirect(url_for("admin_places"))

    events = config.load_events()
    if old_name in events:
        idx = events.index(old_name)
        events[idx] = new_name
        config.save_events(events)

        # Rename in data records too
        records = load_data()
        for r in records:
            if r["event"] == old_name:
                r["event"] = new_name
        save_data(records)

        flash(f"Renamed '{old_name}' to '{new_name}'.", "success")
    return redirect(url_for("admin_places"))


@app.route("/admin/records/edit/<int:record_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_record(record_id):
    records = load_data()
    events = config.load_events()
    record = None
    record_idx = None

    for i, r in enumerate(records):
        if r.get("id") == record_id:
            record = r
            record_idx = i
            break

    if record is None:
        flash("Record not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        new_event = request.form.get("event")
        new_count = request.form.get("head_count")

        if new_event and new_event in events:
            records[record_idx]["event"] = new_event
        if new_count and new_count.isdigit():
            records[record_idx]["head_count"] = int(new_count)

        save_data(records)
        flash("Record updated successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/edit_record.html",
                           record=record, events=events)


@app.route("/admin/records/delete/<int:record_id>", methods=["POST"])
@admin_required
def admin_delete_record(record_id):
    records = load_data()
    # Find and delete the image file
    for r in records:
        if r.get("id") == record_id:
            try:
                event_folder = r["event"].replace(" ", "_").lower()
                file_path = os.path.join(config.UPLOAD_FOLDER, event_folder, r["filename"])
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            break
    records = [r for r in records if r.get("id") != record_id]
    save_data(records)
    flash("Record deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/photos/delete/<int:record_id>", methods=["POST"])
@admin_required
def admin_delete_photo(record_id):
    records = load_data()
    # Find and delete the image file
    for r in records:
        if r.get("id") == record_id:
            try:
                event_folder = r["event"].replace(" ", "_").lower()
                file_path = os.path.join(config.UPLOAD_FOLDER, event_folder, r["filename"])
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            break
    records = [r for r in records if r.get("id") != record_id]
    save_data(records)
    flash("Photo deleted.", "success")
    return redirect(url_for("admin_photos"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
