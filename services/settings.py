"""Settings persistence stored in the user's app data directory."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

APP_NAME = "EZ Music Manage"
LEGACY_SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.json"

DEFAULT_SETTINGS = {
    "netease_cookie": "",
    "default_scan_path": "",
    "cover_max_size": 1500,
    "cover_quality": 90,
    "lrc_source_priority": "netease",
    "list_display_mode": "detailed",
    "list_columns": {
        "cover_thumbnail": False,
        "artist": True,
        "album": False,
        "duration": False,
        "format_badge": True,
        "lrc_badge": True,
    },
    "itunes_countries": ["JP", "US"],
    "ui_language": "zh-CN",
    "theme_mode": "auto",
}


def get_settings_file() -> Path:
    if sys.platform == "darwin":
        settings_dir = Path.home() / "Library" / "Application Support" / APP_NAME
    elif sys.platform.startswith("win"):
        appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        settings_dir = appdata / APP_NAME
    else:
        settings_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ez-music-manage"
    return settings_dir / "settings.json"


def _migrate_legacy_settings(settings_file: Path) -> None:
    if settings_file.exists() or not LEGACY_SETTINGS_FILE.is_file():
        return
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LEGACY_SETTINGS_FILE, settings_file)


def load_settings() -> dict:
    settings_file = get_settings_file()
    _migrate_legacy_settings(settings_file)
    if settings_file.is_file():
        try:
            with settings_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            merged = {**DEFAULT_SETTINGS, **data}
            return merged
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(data: dict):
    settings_file = get_settings_file()
    _migrate_legacy_settings(settings_file)
    current = load_settings()
    current.update(data)
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    with settings_file.open("w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
