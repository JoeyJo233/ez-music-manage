"""Cover search and management router."""

from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.cover_search import search_covers, download_cover
from services.metadata import get_cover_bytes, set_cover_only
from services.scanner import library

router = APIRouter(prefix="/api", tags=["cover"])


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _album_group_key(song) -> tuple[str, str]:
    album = _normalize(song.album)
    owner = _normalize(song.album_artist) or _normalize(song.artist)
    return album, owner


@router.get("/cover/search")
async def search_cover(artist: str = "", album: str = ""):
    from services.settings import load_settings
    settings = load_settings()
    cookie = settings.get("netease_cookie", "")
    covers = await search_covers(artist, album, cookie=cookie)
    return {"covers": covers}


class DownloadRequest(BaseModel):
    url: str
    source: str = ""


@router.post("/cover/download")
async def download_cover_api(req: DownloadRequest):
    data = await download_cover(req.url)
    if not data:
        raise HTTPException(status_code=502, detail="Failed to download cover")
    b64 = base64.b64encode(data).decode()
    return {"cover_data": f"data:image/jpeg;base64,{b64}"}


class ApplyAlbumCoverRequest(BaseModel):
    pass


@router.post("/songs/{song_id}/apply-album-cover")
async def apply_album_cover(song_id: str):
    song = library.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    cover_data = get_cover_bytes(song.file_path)
    if not cover_data:
        raise HTTPException(status_code=400, detail="Current song has no cover")

    album_name, album_owner = _album_group_key(song)
    if not album_name:
        raise HTTPException(status_code=400, detail="Current song has no album name")

    from services.settings import load_settings
    settings = load_settings()

    updated = []
    updated_ids = []
    for s in library.songs.values():
        if s.id == song_id:
            continue
        if _album_group_key(s) == (album_name, album_owner):
            try:
                set_cover_only(
                    s.file_path, cover_data,
                    max_cover_size=settings.get("cover_max_size", 1500),
                    cover_quality=settings.get("cover_quality", 90),
                )
                s.has_cover = True
                updated.append(s.filename)
                updated_ids.append(s.id)
            except Exception:
                continue

    return {"updated": updated, "updated_ids": updated_ids, "count": len(updated)}


@router.get("/cover/library")
async def list_covers_in_library():
    """List all songs with covers for the 'copy from library' feature."""
    results = []
    for s in library.songs.values():
        if s.has_cover:
            results.append({
                "id": s.id,
                "title": s.title,
                "artist": s.artist,
                "album": s.album,
                "filename": s.filename,
            })
    return {"songs": results}
