"""Partner-facing, aggregate facility data. No user or reservation records are exposed."""
import base64
import hmac
import math
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse

from .db import connection

router = APIRouter(prefix="/api/public", tags=["partner facilities"])
_calls: dict[str, list[float]] = {}
_lock = threading.Lock()


class PartnerError(Exception):
    def __init__(self, status: int, code: str, message: str, headers=None):
        self.status, self.code, self.message, self.headers = status, code, message, headers


def fail(code="INVALID_REQUEST", message="Parameter permintaan tidak valid."):
    raise PartnerError(400, code, message)


def error_response(error: PartnerError):
    return JSONResponse({"error": {"code": error.code, "message": error.message}}, status_code=error.status, headers=error.headers)


def partner_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    keys = [os.getenv("COURTSLOT_AERIVA_API_KEY"), os.getenv("COURTSLOT_LOCALLOOP_API_KEY")]
    if not all(keys) or keys[0] == keys[1]:
        raise PartnerError(503, "SOURCE_UNAVAILABLE", "Akses mitra belum dikonfigurasi.")
    if not x_api_key or not any(hmac.compare_digest(x_api_key, key) for key in keys):
        raise PartnerError(401, "INVALID_API_KEY", "API key tidak valid.")
    now = time.monotonic()
    with _lock:
        previous = [t for t in _calls.get(x_api_key, []) if now - t < 60]
        if len(previous) >= 60:
            retry = max(1, math.ceil(60 - (now - previous[0])))
            raise PartnerError(429, "RATE_LIMITED", "Batas permintaan terlampaui.", {"Retry-After": str(retry)})
        previous.append(now)
        _calls[x_api_key] = previous
    return x_api_key


def facility(row):
    return {"id": row["id"], "name": row["name"], "type": row["type"],
            "address": row["address"],
            "location": None if row["lat"] is None or row["lon"] is None else {"lat": row["lat"], "lon": row["lon"]},
            "status": row["status"], "detail_url": None, "updated_at": row["updated_at"]}


def parse_time(value: str | None):
    if value is None:
        fail()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() is None:
            fail()
        return parsed
    except (ValueError, OverflowError):
        fail()


def distance_km(a, b, c, d):
    r1, r2 = math.radians(a), math.radians(c)
    dr, dl = r2-r1, math.radians(d-b)
    h = math.sin(dr/2)**2 + math.cos(r1)*math.cos(r2)*math.sin(dl/2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(h)))


def decode_cursor(value):
    try:
        result = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)).decode("utf-8")
        if not result.startswith("fac-"):
            fail()
        return result
    except (ValueError, UnicodeError, base64.binascii.Error):
        fail()


@router.get("/facilities", dependencies=[Depends(partner_key)])
def facilities(lat: float | None = None, lon: float | None = None, radius_km: float | None = None,
               city: str | None = None, type: str | None = None, limit: int = 20, cursor: str | None = None):
    if (lat is None) != (lon is None) or (radius_km is not None and (lat is None or not math.isfinite(radius_km) or radius_km <= 0)):
        fail()
    if lat is not None and (not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180):
        fail()
    if not 1 <= limit <= 100 or (city is not None and not city.strip()) or (type is not None and not type.strip()):
        fail()
    after = decode_cursor(cursor) if cursor else None
    with connection() as db:
        rows = db.execute("SELECT * FROM facilities ORDER BY id").fetchall()
    rows = [r for r in rows if (after is None or r["id"] > after)
            and (city is None or r["city"].casefold() == city.strip().casefold())
            and (type is None or r["type"].casefold() == type.strip().casefold())
            and (lat is None or (r["lat"] is not None and r["lon"] is not None
                 and (radius_km is None or distance_km(lat, lon, r["lat"], r["lon"]) <= radius_km)))]
    page = rows[:limit]
    next_cursor = base64.urlsafe_b64encode(page[-1]["id"].encode()).decode().rstrip("=") if len(rows) > limit else None
    return {"items": [facility(r) for r in page], "next_cursor": next_cursor}


@router.get("/facilities/{facility_id}", dependencies=[Depends(partner_key)])
def facility_detail(facility_id: str):
    with connection() as db:
        row = db.execute("SELECT * FROM facilities WHERE id=?", (facility_id,)).fetchone()
    if row is None:
        raise PartnerError(404, "NOT_FOUND", "Fasilitas tidak ditemukan.")
    return facility(row)


@router.get("/facilities/{facility_id}/availability", dependencies=[Depends(partner_key)])
def availability(facility_id: str, start: str | None = None, end: str | None = None):
    first, last = parse_time(start), parse_time(end)
    if last.astimezone(timezone.utc) <= first.astimezone(timezone.utc) or last - first > timedelta(days=31):
        fail()
    with connection() as db:
        row = db.execute("SELECT * FROM facilities WHERE id=?", (facility_id,)).fetchone()
        if row is None:
            raise PartnerError(404, "NOT_FOUND", "Fasilitas tidak ditemukan.")
        units = db.execute("SELECT * FROM bookable_units WHERE facility_id=? ORDER BY id", (facility_id,)).fetchall()
        booked = {(r["unit_id"], r["start_utc"]) for r in db.execute(
            "SELECT r.unit_id,r.start_utc FROM reservations r JOIN bookable_units u ON u.id=r.unit_id WHERE u.facility_id=? AND r.status='CONFIRMED'",
            (facility_id,))}
    slots = []
    for unit in units:
        zone = ZoneInfo(unit["timezone"])
        date = first.astimezone(zone).date()
        end_date = last.astimezone(zone).date()
        while date <= end_date:
            hour, minute = map(int, unit["opens_at"].split(":"))
            close_h, close_m = map(int, unit["closes_at"].split(":"))
            opening = datetime(date.year, date.month, date.day, hour, minute, tzinfo=zone)
            closing = datetime(date.year, date.month, date.day, close_h, close_m, tzinfo=zone)
            point = opening
            while point + timedelta(minutes=unit["slot_minutes"]) <= closing:
                following = point + timedelta(minutes=unit["slot_minutes"])
                if point.astimezone(timezone.utc) >= first.astimezone(timezone.utc) and following.astimezone(timezone.utc) <= last.astimezone(timezone.utc):
                    closed = row["status"] == "closed"
                    full = (unit["id"], point.astimezone(timezone.utc).isoformat(timespec="seconds")) in booked
                    slots.append({"unit_id": unit["id"], "start": point.isoformat(timespec="seconds"),
                                  "end": following.isoformat(timespec="seconds"),
                                  "status": "closed" if closed else "full" if full else "available",
                                  "remaining_capacity": 0 if closed or full else unit["capacity"]})
                point = following
            date += timedelta(days=1)
    slots.sort(key=lambda s: (s["start"], s["unit_id"]))
    return {"facility_id": facility_id, "slots": slots, "updated_at": row["updated_at"]}
