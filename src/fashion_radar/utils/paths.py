from __future__ import annotations

from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_documents_dir

APP_NAME = "fashion-radar"


def default_config_dir() -> Path:
    return Path(user_config_dir(APP_NAME))


def default_data_dir() -> Path:
    return Path(user_data_dir(APP_NAME))


def default_reports_dir() -> Path:
    return Path(user_documents_dir()) / APP_NAME / "reports"
