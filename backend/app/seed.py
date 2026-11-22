from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .db import connection, initialize


FACILITIES = (
    ("fac-bandung-lapangan", "Lapangan Basket Cempaka", "sports_field", "Bandung", "Jl. Cempaka No. 10, Bandung", -6.9175, 107.6191, "open"),
    ("fac-bandung-perpustakaan", "Perpustakaan Melati", "library", "Bandung", "Jl. Melati No. 5, Bandung", -6.9147, 107.6098, "open"),
    ("fac-bandung-taman", "Taman Kenanga", "park", "Bandung", "Jl. Kenanga No. 3, Bandung", -6.9231, 107.6342, "open"),
)

UNITS = (
    ("unit-bandung-lapangan-1", "fac-bandung-lapangan", "Lapangan basket 1", "07:00", "21:00"),
    ("unit-bandung-ruang-baca-1", "fac-bandung-perpustakaan", "Ruang baca 1", "08:00", "17:00"),
    ("unit-bandung-pavilion-1", "fac-bandung-taman", "Pavilion 1", "07:00", "18:00"),
)


def seed(path: Path | None = None) -> None:
    initialize(path)
    now = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat(timespec="seconds")
    with connection(path) as db:
        db.executemany(
            "INSERT OR IGNORE INTO facilities (id,name,type,city,address,lat,lon,status,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (facility + (now,) for facility in FACILITIES),
        )
        db.executemany(
            "INSERT OR IGNORE INTO bookable_units (id,facility_id,name,booking_model,slot_minutes,capacity,opens_at,closes_at,timezone) VALUES (?,?,?,'EXCLUSIVE_SLOT',60,1,?,?,'Asia/Jakarta')",
            UNITS,
        )


if __name__ == "__main__":
    seed()
