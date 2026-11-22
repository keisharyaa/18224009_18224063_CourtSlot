"""MVP citizen API. Contract documented in docs/mobile-api-draft.md."""
import sqlite3
import uuid
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from .db import connection
from .public import PartnerError, facility
from .security import TOKEN_SECONDS, create_token, current_user, hash_password, verify_password

router = APIRouter(prefix="/api/v1", tags=["mobile"])
JAKARTA = ZoneInfo("Asia/Jakarta")


def now_local():
    return datetime.now(JAKARTA).isoformat(timespec="microseconds")


def reject(status, code, message):
    raise PartnerError(status, code, message)


def slot_start(unit, day):
    hour, minute = map(int, unit["opens_at"].split(":"))
    return datetime.combine(day, time(hour, minute), ZoneInfo(unit["timezone"]))


def slot_end(unit, day):
    hour, minute = map(int, unit["closes_at"].split(":"))
    return datetime.combine(day, time(hour, minute), ZoneInfo(unit["timezone"]))


def utc_text(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds")


class Register(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    email: str
    password: str


class Booking(BaseModel):
    unit_id: str
    start: datetime


@router.post("/auth/register", status_code=201)
def register(body: Register):
    email = body.email.strip().lower()
    if "@" not in email or not email.split("@")[-1].count("."):
        reject(400, "INVALID_REQUEST", "Email tidak valid.")
    user_id = "usr-" + uuid.uuid4().hex
    try:
        with connection() as db:
            db.execute("INSERT INTO users VALUES (?,?,?,?,?)", (user_id, body.name.strip(), email, hash_password(body.password), now_local()))
    except sqlite3.IntegrityError:
        reject(409, "EMAIL_IN_USE", "Email sudah terdaftar.")
    return {"id": user_id, "name": body.name.strip(), "email": email}


@router.post("/auth/login")
def login(body: Login):
    with connection() as db:
        row = db.execute("SELECT * FROM users WHERE email=?", (body.email.strip().lower(),)).fetchone()
    if row is None or not verify_password(body.password, row["password_hash"]):
        reject(401, "INVALID_CREDENTIALS", "Email atau password salah.")
    return {"access_token": create_token(row["id"]), "token_type": "bearer", "expires_in": TOKEN_SECONDS}


@router.get("/facilities")
def facilities():
    with connection() as db:
        rows = db.execute("SELECT * FROM facilities ORDER BY name").fetchall()
    return {"items": [facility(row) for row in rows]}


@router.get("/facilities/{facility_id}")
def detail(facility_id: str):
    with connection() as db:
        row = db.execute("SELECT * FROM facilities WHERE id=?", (facility_id,)).fetchone()
        units = db.execute("SELECT id,name,slot_minutes FROM bookable_units WHERE facility_id=? ORDER BY name", (facility_id,)).fetchall()
    if row is None:
        reject(404, "NOT_FOUND", "Fasilitas tidak ditemukan.")
    return {**facility(row), "units": [dict(unit) for unit in units]}


@router.get("/units/{unit_id}/slots")
def slots(unit_id: str, date: date):
    with connection() as db:
        unit = db.execute("SELECT u.*, f.status AS facility_status FROM bookable_units u JOIN facilities f ON f.id=u.facility_id WHERE u.id=?", (unit_id,)).fetchone()
        if unit is None:
            reject(404, "NOT_FOUND", "Unit tidak ditemukan.")
        booked = {r["start_utc"] for r in db.execute("SELECT start_utc FROM reservations WHERE unit_id=? AND status='CONFIRMED'", (unit_id,))}
    items = []
    point = slot_start(unit, date)
    while point + timedelta(minutes=unit["slot_minutes"]) <= slot_end(unit, date):
        end = point + timedelta(minutes=unit["slot_minutes"])
        status = "closed" if unit["facility_status"] == "closed" else "full" if utc_text(point) in booked else "available"
        items.append({"start": point.isoformat(timespec="seconds"), "end": end.isoformat(timespec="seconds"), "status": status})
        point = end
    return {"items": items}


def reservation_body(row):
    zone = ZoneInfo(row["timezone"])
    return {"id": row["id"], "unit_id": row["unit_id"], "facility_name": row["facility_name"],
            "start": datetime.fromisoformat(row["start_utc"]).astimezone(zone).isoformat(timespec="seconds"),
            "end": datetime.fromisoformat(row["end_utc"]).astimezone(zone).isoformat(timespec="seconds"),
            "status": row["status"]}


@router.post("/reservations", status_code=201)
def book(body: Booking, user_id: str = Depends(current_user)):
    if body.start.utcoffset() is None:
        reject(400, "INVALID_REQUEST", "Waktu harus menyertakan zona waktu.")
    if body.start <= datetime.now(timezone.utc):
        reject(400, "INVALID_REQUEST", "Slot harus berada di masa depan.")
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        unit = db.execute("SELECT u.*,f.status AS facility_status FROM bookable_units u JOIN facilities f ON f.id=u.facility_id WHERE u.id=?", (body.unit_id,)).fetchone()
        if unit is None:
            reject(404, "NOT_FOUND", "Unit tidak ditemukan.")
        if unit["facility_status"] != "open":
            reject(409, "SLOT_UNAVAILABLE", "Slot sudah tidak tersedia.")
        local = body.start.astimezone(ZoneInfo(unit["timezone"]))
        opening = slot_start(unit, local.date())
        closing = slot_end(unit, local.date())
        minutes = unit["slot_minutes"]
        if local < opening or local + timedelta(minutes=minutes) > closing or (local - opening).total_seconds() % (minutes * 60):
            reject(400, "INVALID_REQUEST", "Waktu di luar slot operasional.")
        end = local + timedelta(minutes=minutes)
        reservation_id = "res-" + uuid.uuid4().hex
        timestamp = now_local()
        try:
            db.execute("INSERT INTO reservations VALUES (?,?,?,?,?,?,?,?)", (reservation_id, user_id, unit["id"], utc_text(local), utc_text(end), "CONFIRMED", timestamp, timestamp))
        except sqlite3.IntegrityError:
            reject(409, "SLOT_UNAVAILABLE", "Slot sudah tidak tersedia.")
        db.execute("UPDATE facilities SET updated_at=? WHERE id=?", (timestamp, unit["facility_id"]))
    return {"id": reservation_id, "unit_id": unit["id"], "start": local.isoformat(timespec="seconds"), "end": end.isoformat(timespec="seconds"), "status": "CONFIRMED"}


@router.get("/reservations/me")
def mine(user_id: str = Depends(current_user)):
    with connection() as db:
        rows = db.execute("""SELECT r.*,u.timezone,f.name AS facility_name FROM reservations r
            JOIN bookable_units u ON u.id=r.unit_id JOIN facilities f ON f.id=u.facility_id
            WHERE r.user_id=? ORDER BY r.start_utc DESC""", (user_id,)).fetchall()
    return {"items": [reservation_body(row) for row in rows]}


@router.post("/reservations/{reservation_id}/cancel")
def cancel(reservation_id: str, user_id: str = Depends(current_user)):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("""SELECT r.*,u.facility_id FROM reservations r JOIN bookable_units u ON u.id=r.unit_id
            WHERE r.id=? AND r.user_id=?""", (reservation_id, user_id)).fetchone()
        if row is None:
            reject(404, "NOT_FOUND", "Reservasi tidak ditemukan.")
        if row["status"] != "CONFIRMED" or datetime.fromisoformat(row["start_utc"]) <= datetime.now(timezone.utc):
            reject(409, "CANNOT_CANCEL", "Reservasi tidak dapat dibatalkan.")
        timestamp = now_local()
        db.execute("UPDATE reservations SET status='CANCELLED_BY_USER',updated_at=? WHERE id=?", (timestamp, reservation_id))
        db.execute("UPDATE facilities SET updated_at=? WHERE id=?", (timestamp, row["facility_id"]))
    return {"id": reservation_id, "status": "CANCELLED_BY_USER"}
