from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine


def create_sqlite_engine(path: Path) -> Engine:
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(URL.create("sqlite", database=str(path)), future=True)


def create_readonly_sqlite_engine(path: Path) -> Engine:
    quoted_path = quote(path.as_posix(), safe="/")
    return create_engine(
        f"sqlite:///file:{quoted_path}?mode=ro&uri=true",
        future=True,
    )
