"""LRC lyrics read/write/search router."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.lyrics import search_lyrics
from services.scanner import library

router = APIRouter(prefix="/api", tags=["lrc"])


@router.get("/songs/{song_id}/lrc")
async def get_lrc(song_id: str):
    song = library.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    base = os.path.splitext(song.file_path)[0]
    synced = ""
    translated = ""

    lrc_path = base + ".lrc"
    if os.path.isfile(lrc_path):
        with open(lrc_path, "r", encoding="utf-8") as f:
            synced = f.read()

    trans_path = base + ".trans.lrc"
    if os.path.isfile(trans_path):
        with open(trans_path, "r", encoding="utf-8") as f:
            translated = f.read()

    return {
        "synced": synced,
        "translated": translated,
        "has_synced": bool(synced),
        "has_translated": bool(translated),
    }


class LrcSaveRequest(BaseModel):
    synced: str | None = None
    translated: str | None = None


@router.post("/songs/{song_id}/lrc")
async def save_lrc(song_id: str, req: LrcSaveRequest):
    song = library.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    base = os.path.splitext(song.file_path)[0]

    if req.synced is not None:
        with open(base + ".lrc", "w", encoding="utf-8") as f:
            f.write(req.synced)
        song.has_lrc = True

    if req.translated is not None:
        with open(base + ".trans.lrc", "w", encoding="utf-8") as f:
            f.write(req.translated)
        song.has_lrc_trans = True

    return {"status": "ok"}


class LrcDeleteRequest(BaseModel):
    type: str  # "synced" | "translated" | "all"


@router.delete("/songs/{song_id}/lrc")
async def delete_lrc(song_id: str, req: LrcDeleteRequest):
    song = library.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    base = os.path.splitext(song.file_path)[0]

    if req.type in ("synced", "all"):
        path = base + ".lrc"
        if os.path.isfile(path):
            os.remove(path)
        song.has_lrc = False

    if req.type in ("translated", "all"):
        path = base + ".trans.lrc"
        if os.path.isfile(path):
            os.remove(path)
        song.has_lrc_trans = False

    return {"status": "ok"}


@router.get("/lrc/search")
async def search_lrc(artist: str = "", title: str = "", album: str = ""):
    from services.settings import load_settings
    settings = load_settings()
    cookie = settings.get("netease_cookie", "")
    results = await search_lyrics(artist, title, album, cookie=cookie)
    return {"results": results}
