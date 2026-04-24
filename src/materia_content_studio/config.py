from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


DEFAULT_DB_PATH = Path("data/materia_content_studio.db")
DEFAULT_UPLOADS_PATH = Path("data/uploads")
DEFAULT_BRAND_MANUAL_PATH = Path("data/brand_manual")


def _get_streamlit_secret(key: str) -> str:
    try:
        import streamlit as st

        value: Any = st.secrets.get(key)
        return str(value) if value is not None else ""
    except Exception:
        return ""


def get_config_value(key: str, default: str = "") -> str:
    return os.getenv(key) or _get_streamlit_secret(key) or default


@dataclass(slots=True)
class Settings:
    app_password: str
    store_base_url: str
    database_path: Path
    uploads_path: Path
    brand_manual_path: Path


def get_settings() -> Settings:
    return Settings(
        app_password=get_config_value("APP_PASSWORD", ""),
        store_base_url=get_config_value("STORE_BASE_URL", "https://www.materiainsumos.com.ar"),
        database_path=DEFAULT_DB_PATH,
        uploads_path=DEFAULT_UPLOADS_PATH,
        brand_manual_path=DEFAULT_BRAND_MANUAL_PATH,
    )
