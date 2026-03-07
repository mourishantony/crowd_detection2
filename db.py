import os
from pymongo import MongoClient

_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        uri = os.environ.get("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI environment variable is not set")
        _client = MongoClient(uri)
        _db = _client["crowd_detection"]
    return _db


# ── Records ──────────────────────────────────────────────────────────────────

def load_records():
    db = _get_db()
    return list(db.records.find({}, {"_id": 0}).sort("id", 1))


def save_records(records):
    """Replace all records (drop + bulk insert)."""
    db = _get_db()
    db.records.drop()
    if records:
        db.records.insert_many([dict(r) for r in records])


# ── Events ───────────────────────────────────────────────────────────────────

_DEFAULT_EVENTS = []


def load_events():
    db = _get_db()
    doc = db.settings.find_one({"key": "events"})
    if doc:
        return doc["value"]
    return _DEFAULT_EVENTS


def save_events(events):
    db = _get_db()
    db.settings.replace_one(
        {"key": "events"},
        {"key": "events", "value": events},
        upsert=True
    )
