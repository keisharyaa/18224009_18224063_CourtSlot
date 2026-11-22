import sqlite3
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.public import _calls
from app.seed import seed


@pytest.fixture
def client(tmp_path, monkeypatch):
    path = tmp_path / "partner.sqlite3"
    monkeypatch.setenv("COURTSLOT_DB_PATH", str(path))
    monkeypatch.setenv("COURTSLOT_AERIVA_API_KEY", "test-aeriva-only")
    monkeypatch.setenv("COURTSLOT_LOCALLOOP_API_KEY", "test-localloop-only")
    _calls.clear()
    seed(path)
    with TestClient(app) as api:
        yield api, path


def get(client, path, key="test-aeriva-only", **params):
    return client.get(path, params=params, headers={"X-API-Key": key})


def test_catalog_filters_pagination_and_detail(client):
    c, path = client
    first = get(c, "/api/public/facilities", limit=1).json()
    assert len(first["items"]) == 1 and first["next_cursor"]
    second = get(c, "/api/public/facilities", limit=1, cursor=first["next_cursor"]).json()
    assert second["items"][0]["id"] != first["items"][0]["id"]
    assert len(get(c, "/api/public/facilities", city="bandung").json()["items"]) == 3
    assert [x["type"] for x in get(c, "/api/public/facilities", type="park").json()["items"]] == ["park"]
    assert len(get(c, "/api/public/facilities", lat=-6.9175, lon=107.6191, radius_km=0.1).json()["items"]) == 1
    detail = get(c, "/api/public/facilities/fac-bandung-taman").json()
    assert detail == get(c, "/api/public/facilities", type="park").json()["items"][0]
    assert set(detail) == {"id", "name", "type", "address", "location", "status", "detail_url", "updated_at"}
    assert get(c, "/api/public/facilities/missing").json()["error"]["code"] == "NOT_FOUND"


def test_availability_time_boundary_zone_and_database(client):
    c, path = client
    route = "/api/public/facilities/fac-bandung-lapangan/availability"
    params = {"start": "2026-12-05T00:00:00Z", "end": "2026-12-05T01:00:00Z"}
    body = get(c, route, **params).json()
    assert body["slots"] == [{"unit_id": "unit-bandung-lapangan-1", "start": "2026-12-05T07:00:00+07:00", "end": "2026-12-05T08:00:00+07:00", "status": "available", "remaining_capacity": 1}]
    assert get(c, route, start="2026-12-05T08:00:00+07:00", end="2026-12-05T09:00:00+07:00").json()["slots"][0]["start"].endswith("08:00:00+07:00")
    with sqlite3.connect(path) as db:
        db.execute("UPDATE facilities SET status='closed' WHERE id='fac-bandung-lapangan'")
    assert get(c, route, **params).json()["slots"][0]["status"] == "closed"
    with sqlite3.connect(path) as db:
        db.execute("UPDATE bookable_units SET opens_at='09:00' WHERE id='unit-bandung-lapangan-1'")
    assert get(c, route, **params).json()["slots"] == []


def test_auth_errors_validation_and_rate_limit(client):
    c, _ = client
    route = "/api/public/facilities"
    assert c.get(route).status_code == 401
    assert get(c, route, key="wrong").json() == {"error": {"code": "INVALID_API_KEY", "message": "API key tidak valid."}}
    assert get(c, route, key="test-localloop-only").status_code == 200
    for params in ({"lat": 1}, {"radius_km": 0}, {"limit": 0}, {"limit": "abc"}, {"cursor": "%%%"}):
        response = get(c, route, **params)
        assert response.status_code == 400 and response.json()["error"]["code"] == "INVALID_REQUEST"
    a = get(c, "/api/public/facilities/fac-bandung-taman/availability", start="2026-12-05T07:00:00", end="2026-12-05T08:00:00+07:00")
    assert a.status_code == 400 and a.json()["error"]["code"] == "INVALID_REQUEST"
    _calls.clear()
    for _ in range(60):
        assert get(c, route).status_code == 200
    limited = get(c, route)
    assert limited.status_code == 429 and int(limited.headers["Retry-After"]) > 0
    assert limited.json()["error"]["code"] == "RATE_LIMITED"
    assert get(c, route, key="test-localloop-only").status_code == 200
