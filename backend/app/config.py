import os
from pathlib import Path


def database_path() -> Path:
    return Path(os.getenv("COURTSLOT_DB_PATH", "data/courtslot.sqlite3")).expanduser().resolve()
