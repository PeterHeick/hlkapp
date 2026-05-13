"""Indstillinger via pydantic-settings — læses fra data/config.json."""
from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_DATA_DIR = Path("data")
_CONFIG_PATH = _DATA_DIR / "config.json"


def _load_json() -> dict:  # type: ignore[type-arg]
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KLINIK_", extra="ignore")

    gecko_api_token: str = ""
    gecko_base_url: str = "https://app.geckobooking.dk/api/v1"
    site_url: str = ""
    max_depth: int = 5
    port: int = 8765
    db_path: Path = _DATA_DIR / "klinik.db"
    exports_dir: Path = _DATA_DIR / "exports"
    assets_dir: Path = Path("assets")
    max_pages: int = 1000
    deep_threshold: int = 4

    @classmethod
    def load(cls) -> "Settings":
        return cls(**_load_json())

    def save(self, *, site_url: str | None = None, max_depth: int | None = None) -> None:
        data = _load_json()
        if site_url is not None:
            data["site_url"] = site_url
        if max_depth is not None:
            data["max_depth"] = max_depth
        _CONFIG_PATH.parent.mkdir(exist_ok=True)
        _CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        if site_url is not None:
            self.site_url = site_url
        if max_depth is not None:
            self.max_depth = max_depth


settings = Settings.load()
