"""Settings persistence - reads/writes settings.json."""

from __future__ import annotations

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")

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
}


def load_settings() -> dict:
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = {**DEFAULT_SETTINGS, **data}
            return merged
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(data: dict):
    current = load_settings()
    current.update(data)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
