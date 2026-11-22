import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.db import initialize
from app.main import app
from app.seed import seed

FACILITY = "fac-bandung-lapangan"
UNIT = "unit-bandung-lapangan-1"
PARTNER = {"X-API-Key": "test-aeriva"}


@pytest.fixture
def api(tmp_path, monkeypatch):
    path = tmp_path / "data.sqlite3"
    monkeypatch.setenv("COURTSLOT_DB_PATH", str(path))
    monkeypatch.setenv("COURTSLOT_AERIVA_API_KEY", "test-aeriva")
    monkeypatch.setenv("COURTSLOT_LOCALLOOP_API_KEY", "test-localloop")
    monkeypatch.setenv("COURTSLOT_TOKEN_SECRET", "test-secret-with-at-least-thirty-two-characters")
    seed(path)
    with TestClient(app) as client:
        yield client, path


def account(client, email):
    response = client.post("/api/v1/auth/register", json={"name": "Warga Demo", "email": email, "password": "password-demo-123"})
    assert response.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "password-demo-123"})
    assert login.status_code == 200
    return {"Authorization": "Bearer " + login.json()["access_token"]}


def future_start():
    return (datetime.now(ZoneInfo("Asia/Jakarta")).date() + timedelta(days=2)).isoformat() + "T07:00:00+07:00"


def partner_slot(client, start):
    end = (datetime.fromisoformat(start) + timedelta(hours=1)).isoformat()
    response = client.get(f"/api/public/facilities/{FACILITY}/availability", headers=PARTNER, params={"start": start, "end": end})
    assert response.status_code == 200
    return response.json()


def test_migrate_filled_v1_database(tmp_path):
    path = tmp_path / "old.sqlite3"
    seed(path)
    with sqlite3.connect(path) as db:
        db.execute("DROP INDEX reservations_owner")
        db.execute("DROP INDEX one_active_reservation_per_slot")
        db.execute("DROP TABLE reservations")
        db.execute("DROP TABLE users")
        db.execute("PRAGMA user_version = 1")
    initialize(path)
    initialize(path)
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM facilities").fetchone()[0] == 3
        assert db.execute("SELECT count(*) FROM bookable_units").fetchone()[0] == 3


def test_auth_owner_cancel_and_partner_snapshot(api):
    client, path = api
    owner = account(client, "owner@example.test")
    other = account(client, "other@example.test")
    assert client.post("/api/v1/auth/login", json={"email": "owner@example.test", "password": "wrong"}).status_code == 401
    assert client.get("/api/v1/reservations/me").status_code == 401
    assert len(client.get("/api/v1/facilities").json()["items"]) == 3
    assert client.get(f"/api/v1/facilities/{FACILITY}").json()["units"][0]["id"] == UNIT
    start = future_start()
    date = start[:10]
    assert client.get(f"/api/v1/units/{UNIT}/slots", params={"date": date}).json()["items"][0]["status"] == "available"
    before = partner_slot(client, start)
    booked = client.post("/api/v1/reservations", headers=owner, json={"unit_id": UNIT, "start": start})
    assert booked.status_code == 201
    rid = booked.json()["id"]
    assert partner_slot(client, start)["slots"][0]["status"] == "full"
    assert partner_slot(client, start)["slots"][0]["remaining_capacity"] == 0
    assert partner_slot(client, start)["updated_at"] != before["updated_at"]
    assert client.get(f"/api/v1/units/{UNIT}/slots", params={"date": date}).json()["items"][0]["status"] == "full"
    assert client.get("/api/v1/reservations/me", headers=other).json() == {"items": []}
    assert client.post(f"/api/v1/reservations/{rid}/cancel", headers=other).status_code == 404
    assert len(client.get("/api/v1/reservations/me", headers=owner).json()["items"]) == 1
    assert client.post(f"/api/v1/reservations/{rid}/cancel", headers=owner).json()["status"] == "CANCELLED_BY_USER"
    assert partner_slot(client, start)["slots"][0]["status"] == "available"
    assert partner_slot(client, start)["slots"][0]["remaining_capacity"] == 1
    assert client.post(f"/api/v1/reservations/{rid}/cancel", headers=owner).status_code == 409
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT password_hash FROM users WHERE email='owner@example.test'").fetchone()[0] != "password-demo-123"


def test_concurrent_booking_exactly_one_and_invalid_time(api):
    client, path = api
    user_a = account(client, "a@example.test")
    user_b = account(client, "b@example.test")
    start = future_start()
    assert client.post("/api/v1/reservations", headers=user_a, json={"unit_id": UNIT, "start": start[:10] + "T06:00:00+07:00"}).status_code == 400
    assert client.post("/api/v1/reservations", headers=user_a, json={"unit_id": UNIT, "start": start.replace("+07:00", "")}).status_code == 400
    def attempt(headers):
        result = client.post("/api/v1/reservations", headers=headers, json={"unit_id": UNIT, "start": start})
        return result.status_code, result.json()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, (user_a, user_b)))
    assert sorted(status for status, _ in results) == [201, 409]
    assert next(body for status, body in results if status == 409)["error"]["code"] == "SLOT_UNAVAILABLE"
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT count(*) FROM reservations WHERE status='CONFIRMED'").fetchone()[0] == 1
