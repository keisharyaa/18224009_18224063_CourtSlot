import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import database_path


SCHEMA_VERSION = 2


@contextmanager
def connection(path: Path | None = None):
    target = path or database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(target, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA busy_timeout = 10000")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def initialize(path: Path | None = None) -> None:
    with connection(path) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            raise RuntimeError(f"Database version {version} is newer than application version {SCHEMA_VERSION}")
        if version == 0:
            db.executescript("""
                CREATE TABLE facilities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    city TEXT NOT NULL,
                    address TEXT NOT NULL,
                    lat REAL,
                    lon REAL,
                    status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
                    updated_at TEXT NOT NULL,
                    CHECK ((lat IS NULL AND lon IS NULL) OR (lat BETWEEN -90 AND 90 AND lon BETWEEN -180 AND 180))
                );
                CREATE TABLE bookable_units (
                    id TEXT PRIMARY KEY,
                    facility_id TEXT NOT NULL REFERENCES facilities(id),
                    name TEXT NOT NULL,
                    booking_model TEXT NOT NULL CHECK (booking_model = 'EXCLUSIVE_SLOT'),
                    slot_minutes INTEGER NOT NULL CHECK (slot_minutes = 60),
                    capacity INTEGER NOT NULL CHECK (capacity = 1),
                    opens_at TEXT NOT NULL,
                    closes_at TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    CHECK (opens_at < closes_at)
                );
                CREATE INDEX idx_units_facility ON bookable_units(facility_id);
                PRAGMA user_version = 1;
            """)
            version = 1
        if version == 1:
            db.executescript("""
                BEGIN IMMEDIATE;
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE reservations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    unit_id TEXT NOT NULL REFERENCES bookable_units(id),
                    start_utc TEXT NOT NULL,
                    end_utc TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('CONFIRMED','CANCELLED_BY_USER')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX one_active_reservation_per_slot
                    ON reservations(unit_id, start_utc) WHERE status='CONFIRMED';
                CREATE INDEX reservations_owner ON reservations(user_id, start_utc);
                PRAGMA user_version = 2;
                COMMIT;
            """)
