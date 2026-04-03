"""Settings read/write router."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["settings"])


class SettingsModel(BaseModel):
    netease_cookie: str = ""
    default_scan_path: str = ""
    cover_max_size: int = 1500
    cover_quality: int = 90
    lrc_source_priority: str = "netease"  # "netease" | "lrclib"
    list_display_mode: str = "detailed"  # "detailed" | "compact"
    list_columns: dict = {
        "cover_thumbnail": False,
        "artist": True,
        "album": False,
        "duration": False,
        "format_badge": True,
        "lrc_badge": True,
    }


@router.get("/settings")
async def get_settings():
    from services.settings import load_settings
    return load_settings()


@router.put("/settings")
async def save_settings(data: dict):
    from services.settings import save_settings
    save_settings(data)
    return {"status": "ok"}
