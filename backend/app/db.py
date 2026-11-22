import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import database_path


SCHEMA_VERSION = 1


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
