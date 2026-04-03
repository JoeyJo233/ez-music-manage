"""Batch operations router."""

from __future__ import annotations

import base64

from fastapi import APIRouter
from pydantic import BaseModel

from services.cover_search import search_covers, download_cover
from services.lyrics import search_lyrics
from services.metadata import get_cover_bytes, set_cover_only
from services.scanner import library

router = APIRouter(prefix="/api/batch", tags=["batch"])


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _album_group_key(song) -> tuple[str, str]:
    album = _normalize(song.album)
    owner = _normalize(song.album_artist) or _normalize(song.artist)
    return album, owner


class BatchCoverRequest(BaseModel):
    song_ids: list[str]
    overwrite: bool = False


@router.post("/covers")
async def batch_covers(req: BatchCoverRequest):
    from services.settings import load_settings
    settings = load_settings()
    cookie = settings.get("netease_cookie", "")

    success = 0
    skipped = 0
    failed = []

    for sid in req.song_ids:
        song = library.get_song(sid)
        if not song:
            failed.append({"id": sid, "reason": "not found"})
            continue

        if song.has_cover and not req.overwrite:
            skipped += 1
            continue

        try:
            covers = await search_covers(song.artist, song.album, cookie=cookie)
            if len(covers) == 1:
                data = await download_cover(covers[0]["url"])
                if data:
                    set_cover_only(
                        song.file_path, data,
                        max_cover_size=settings.get("cover_max_size", 1500),
                        cover_quality=settings.get("cover_quality", 90),
                    )
                    song.has_cover = True
                    success += 1
                else:
                    failed.append({"id": sid, "filename": song.filename, "reason": "download failed"})
            elif len(covers) == 0:
                failed.append({"id": sid, "filename": song.filename, "reason": "no results"})
            else:
                failed.append({"id": sid, "filename": song.filename, "reason": "multiple candidates"})
        except Exception as e:
            failed.append({"id": sid, "filename": song.filename, "reason": str(e)})

    return {"success": success, "skipped": skipped, "failed": failed}


class BatchLyricsRequest(BaseModel):
    song_ids: list[str]
    overwrite: bool = False


@router.post("/lyrics")
async def batch_lyrics(req: BatchLyricsRequest):
    import os
    from services.settings import load_settings
    settings = load_settings()
    cookie = settings.get("netease_cookie", "")

    success = 0
    skipped = 0
    failed = []

    for sid in req.song_ids:
        song = library.get_song(sid)
        if not song:
            failed.append({"id": sid, "reason": "not found"})
            continue

        if song.has_lrc and not req.overwrite:
            skipped += 1
            continue

        try:
            results = await search_lyrics(song.artist, song.title, song.album, cookie=cookie)
            if len(results) == 1:
                base = os.path.splitext(song.file_path)[0]
                lrc_content = results[0].get("synced") or results[0].get("plain", "")
                if lrc_content:
                    with open(base + ".lrc", "w", encoding="utf-8") as f:
                        f.write(lrc_content)
                    song.has_lrc = True

                    trans = results[0].get("translated")
                    if trans:
                        with open(base + ".trans.lrc", "w", encoding="utf-8") as f:
                            f.write(trans)
                        song.has_lrc_trans = True

                    success += 1
                else:
                    failed.append({"id": sid, "filename": song.filename, "reason": "empty lyrics"})
            elif len(results) == 0:
                failed.append({"id": sid, "filename": song.filename, "reason": "no results"})
            else:
                failed.append({"id": sid, "filename": song.filename, "reason": "multiple candidates"})
        except Exception as e:
            failed.append({"id": sid, "filename": song.filename, "reason": str(e)})

    return {"success": success, "skipped": skipped, "failed": failed}


class BatchSyncAlbumCoversRequest(BaseModel):
    song_ids: list[str]


@router.post("/sync-album-covers")
async def batch_sync_album_covers(req: BatchSyncAlbumCoversRequest):
    from services.settings import load_settings
    settings = load_settings()

    songs = [library.get_song(sid) for sid in req.song_ids if library.get_song(sid)]

    albums: dict[tuple[str, str], dict] = {}
    for s in songs:
        album, owner = _album_group_key(s)
        if album:
            key = (album, owner)
            if key not in albums:
                label = s.album.strip()
                if s.album_artist.strip():
                    label = f"{label} / {s.album_artist.strip()}"
                elif s.artist.strip():
                    label = f"{label} / {s.artist.strip()}"
                albums[key] = {"songs": [], "label": label}
            albums[key]["songs"].append(s)

    albums_processed = 0
    songs_updated = 0
    albums_skipped = []

    for album_data in albums.values():
        album_songs = album_data["songs"]
        source = None
        source_cover = None
        for s in album_songs:
            if s.has_cover:
                source_cover = get_cover_bytes(s.file_path)
                source = s
                break

        if not source_cover:
            albums_skipped.append(album_data["label"])
            continue

        albums_processed += 1
        for s in album_songs:
            if s.id == source.id:
                continue
            try:
                set_cover_only(
                    s.file_path, source_cover,
                    max_cover_size=settings.get("cover_max_size", 1500),
                    cover_quality=settings.get("cover_quality", 90),
                )
                s.has_cover = True
                songs_updated += 1
            except Exception:
                continue

    return {
        "albums_processed": albums_processed,
        "songs_updated": songs_updated,
        "albums_skipped": albums_skipped,
    }
