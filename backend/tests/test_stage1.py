import sqlite3

from fastapi.testclient import TestClient

from app.db import initialize
from app.main import app
from app.seed import seed


def test_schema_and_seed_survive_restart(tmp_path):
    path = tmp_path / "data" / "court.sqlite3"
    seed(path)
    seed(path)
    initialize(path)
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM facilities").fetchone()[0] == 3
        assert db.execute("SELECT count(*) FROM bookable_units").fetchone()[0] == 3
        assert db.execute("SELECT count(*) FROM bookable_units WHERE booking_model = 'EXCLUSIVE_SLOT' AND slot_minutes = 60 AND timezone = 'Asia/Jakarta'").fetchone()[0] == 3


def test_health_and_openapi(tmp_path, monkeypatch):
    monkeypatch.setenv("COURTSLOT_DB_PATH", str(tmp_path / "court.sqlite3"))
    with TestClient(app) as client:
        assert client.get("/api/health").json() == {"status": "ok"}
        assert client.get("/docs").status_code == 200
        spec = client.get("/openapi.json").json()
        assert "/api/health" in spec["paths"]
        assert "/api/public/facilities" not in spec["paths"]
