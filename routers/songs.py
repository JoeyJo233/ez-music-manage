"""Single song metadata read/write router."""

from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.metadata import read_metadata, write_metadata, get_cover_bytes
from services.metadata_search import search_itunes_track
from services.scanner import library

router = APIRouter(prefix="/api", tags=["songs"])


class SongUpdateRequest(BaseModel):
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    album_artist: str | None = None
    year: str | None = None
    track_number: str | None = None
    disc_number: str | None = None
    genre: str | None = None
    composer: str | None = None
    comment: str | None = None
    cover_data: str | None = None  # base64 data URI or None


def _get_song_or_404(song_id: str):
    song = library.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.get("/songs/{song_id}")
async def get_song(song_id: str):
    song = _get_song_or_404(song_id)
    meta = read_metadata(song.file_path)
    meta["id"] = song.id
    meta["filename"] = song.filename
    meta["file_path"] = song.file_path
    meta["duration"] = round(song.duration, 2)
    meta["has_lrc"] = song.has_lrc
    meta["has_lrc_trans"] = song.has_lrc_trans
    return meta


@router.put("/songs/{song_id}")
async def update_song(song_id: str, req: SongUpdateRequest):
    song = _get_song_or_404(song_id)
    data = req.model_dump(exclude_none=True)

    cover_bytes = None
    cover_data_str = data.pop("cover_data", None)
    if cover_data_str:
        try:
            if "," in cover_data_str:
                cover_data_str = cover_data_str.split(",", 1)[1]
            cover_bytes = base64.b64decode(cover_data_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cover data")

    try:
        from services.settings import load_settings
        settings = load_settings()
        write_metadata(
            song.file_path, data, cover_bytes,
            max_cover_size=settings.get("cover_max_size", 1500),
            cover_quality=settings.get("cover_quality", 90),
        )
        # Refresh song info in scanner index
        library.songs[song_id] = library._read_flac(song.file_path) if song.format == "FLAC" else library._read_m4a(song.file_path)
        library._check_lrc(library.songs[song_id])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/songs/{song_id}/auto-fill")
async def auto_fill_metadata(song_id: str):
    """Search iTunes for matching track and return suggested metadata."""
    song = _get_song_or_404(song_id)
    meta = read_metadata(song.file_path)
    artist = meta.get("artist") or ""
    title = meta.get("title") or song.filename
    album = meta.get("album") or ""
    from services.settings import load_settings
    settings = load_settings()
    countries = settings.get("itunes_countries") or ["US"]
    results = await search_itunes_track(artist, title, album_query=album, countries=countries)
    return {"results": results, "has_album": bool(album)}


@router.get("/songs/{song_id}/cover")
async def get_cover(song_id: str):
    song = _get_song_or_404(song_id)
    data = get_cover_bytes(song.file_path)
    if not data:
        raise HTTPException(status_code=404, detail="No cover found")
    from fastapi.responses import Response
    return Response(content=data, media_type="image/jpeg")
