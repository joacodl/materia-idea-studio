from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


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
    database_path: Path
    auto_sync_on_startup: bool
    app_password: str
    tiendanube_access_token: str
    tiendanube_store_id: str
    tiendanube_user_agent: str
    instagram_access_token: str
    instagram_business_account_id: str
    openai_api_key: str
    openai_model: str
    anthropic_api_key: str
    anthropic_model: str

    @property
    def has_app_password(self) -> bool:
        return bool(self.app_password)

    @property
    def has_tiendanube_credentials(self) -> bool:
        return bool(self.tiendanube_access_token and self.tiendanube_store_id)

    @property
    def has_instagram_credentials(self) -> bool:
        return bool(self.instagram_access_token and self.instagram_business_account_id)

    @property
    def ai_provider(self) -> str:
        if self.openai_api_key:
            return "openai"
        if self.anthropic_api_key:
            return "anthropic"
        return "mock"


def get_settings() -> Settings:
    return Settings(
        database_path=Path(get_config_value("DATABASE_PATH", "data/materia_content_studio.db")),
        auto_sync_on_startup=get_config_value("AUTO_SYNC_ON_STARTUP", "false").lower() == "true",
        app_password=get_config_value("APP_PASSWORD", ""),
        tiendanube_access_token=get_config_value("TIENDANUBE_ACCESS_TOKEN", ""),
        tiendanube_store_id=get_config_value("TIENDANUBE_STORE_ID", ""),
        tiendanube_user_agent=get_config_value(
            "TIENDANUBE_USER_AGENT", "Materia Content Studio (admin@materia.local)"
        ),
        instagram_access_token=get_config_value("INSTAGRAM_ACCESS_TOKEN", ""),
        instagram_business_account_id=get_config_value("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""),
        openai_api_key=get_config_value("OPENAI_API_KEY", ""),
        openai_model=get_config_value("OPENAI_MODEL", "gpt-4.1-mini"),
        anthropic_api_key=get_config_value("ANTHROPIC_API_KEY", ""),
        anthropic_model=get_config_value("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
        database_path=Path(os.getenv("DATABASE_PATH", "data/materia_content_studio.db")),
        auto_sync_on_startup=os.getenv("AUTO_SYNC_ON_STARTUP", "false").lower() == "true",
        tiendanube_access_token=os.getenv("TIENDANUBE_ACCESS_TOKEN", ""),
        tiendanube_store_id=os.getenv("TIENDANUBE_STORE_ID", ""),
        tiendanube_user_agent=os.getenv(
            "TIENDANUBE_USER_AGENT", "Materia Content Studio (admin@materia.local)"
        ),
        instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        instagram_business_account_id=os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
    )
