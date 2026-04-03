"""Mutagen wrapper - unified read/write for FLAC and M4A."""

from __future__ import annotations

import base64
import io
from typing import Optional

from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image


def _compress_cover(data: bytes, max_size: int = 1500, quality: int = 90) -> bytes:
    img = Image.open(io.BytesIO(data))
    if img.mode == "RGBA":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    result = buf.getvalue()
    if len(result) > 500 * 1024:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        result = buf.getvalue()
    return result


def read_metadata(filepath: str) -> dict:
    if filepath.lower().endswith(".flac"):
        return _read_flac(filepath)
    return _read_m4a(filepath)


def _read_flac(filepath: str) -> dict:
    audio = FLAC(filepath)
    tags = audio.tags or {}

    def tag(key: str) -> str:
        vals = tags.get(key)
        return vals[0] if vals else ""

    cover_data = None
    if audio.pictures:
        pic = audio.pictures[0]
        cover_data = f"data:{pic.mime};base64,{base64.b64encode(pic.data).decode()}"

    return {
        "title": tag("TITLE"),
        "artist": tag("ARTIST"),
        "album": tag("ALBUM"),
        "album_artist": tag("ALBUMARTIST"),
        "year": tag("DATE"),
        "track_number": tag("TRACKNUMBER"),
        "disc_number": tag("DISCNUMBER"),
        "genre": tag("GENRE"),
        "composer": tag("COMPOSER"),
        "comment": tag("COMMENT"),
        "cover_data": cover_data,
        "format": "FLAC",
    }


def _read_m4a(filepath: str) -> dict:
    audio = MP4(filepath)
    tags = audio.tags or {}

    def tag(key: str) -> str:
        vals = tags.get(key)
        if not vals:
            return ""
        return str(vals[0])

    def tag_int_pair(key: str) -> str:
        vals = tags.get(key)
        if not vals:
            return ""
        pair = vals[0]
        if isinstance(pair, tuple) and len(pair) == 2:
            return f"{pair[0]}/{pair[1]}" if pair[1] else str(pair[0])
        return str(pair)

    cover_data = None
    covrs = tags.get("covr")
    if covrs:
        raw = bytes(covrs[0])
        mime = "image/jpeg" if covrs[0].imageformat == MP4Cover.FORMAT_JPEG else "image/png"
        cover_data = f"data:{mime};base64,{base64.b64encode(raw).decode()}"

    return {
        "title": tag("\xa9nam"),
        "artist": tag("\xa9ART"),
        "album": tag("\xa9alb"),
        "album_artist": tag("aART"),
        "year": tag("\xa9day"),
        "track_number": tag_int_pair("trkn"),
        "disc_number": tag_int_pair("disk"),
        "genre": tag("\xa9gen"),
        "composer": tag("\xa9wrt"),
        "comment": tag("\xa9cmt"),
        "cover_data": cover_data,
        "format": "AAC",
    }


def write_metadata(filepath: str, data: dict, cover_bytes: Optional[bytes] = None,
                    max_cover_size: int = 1500, cover_quality: int = 90):
    if filepath.lower().endswith(".flac"):
        _write_flac(filepath, data, cover_bytes, max_cover_size, cover_quality)
    else:
        _write_m4a(filepath, data, cover_bytes, max_cover_size, cover_quality)


def _write_flac(filepath: str, data: dict, cover_bytes: Optional[bytes],
                max_cover_size: int, cover_quality: int):
    audio = FLAC(filepath)

    field_map = {
        "title": "TITLE",
        "artist": "ARTIST",
        "album": "ALBUM",
        "album_artist": "ALBUMARTIST",
        "year": "DATE",
        "track_number": "TRACKNUMBER",
        "disc_number": "DISCNUMBER",
        "genre": "GENRE",
        "composer": "COMPOSER",
        "comment": "COMMENT",
    }
    for key, tag_name in field_map.items():
        if key in data:
            val = data[key]
            if val:
                audio[tag_name] = [val]
            elif tag_name in (audio.tags or {}):
                del audio.tags[tag_name]

    if cover_bytes is not None:
        compressed = _compress_cover(cover_bytes, max_cover_size, cover_quality)
        pic = Picture()
        pic.type = 3  # front cover
        pic.mime = "image/jpeg"
        pic.data = compressed
        img = Image.open(io.BytesIO(compressed))
        pic.width, pic.height = img.size
        audio.clear_pictures()
        audio.add_picture(pic)

    audio.save()


def _write_m4a(filepath: str, data: dict, cover_bytes: Optional[bytes],
               max_cover_size: int, cover_quality: int):
    audio = MP4(filepath)
    if audio.tags is None:
        audio.add_tags()

    field_map = {
        "title": "\xa9nam",
        "artist": "\xa9ART",
        "album": "\xa9alb",
        "album_artist": "aART",
        "year": "\xa9day",
        "genre": "\xa9gen",
        "composer": "\xa9wrt",
        "comment": "\xa9cmt",
    }
    for key, tag_name in field_map.items():
        if key in data:
            val = data[key]
            if val:
                audio.tags[tag_name] = [val]
            elif tag_name in audio.tags:
                del audio.tags[tag_name]

    if "track_number" in data and data["track_number"]:
        parts = data["track_number"].split("/")
        tn = int(parts[0]) if parts[0] else 0
        total = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        audio.tags["trkn"] = [(tn, total)]

    if "disc_number" in data and data["disc_number"]:
        parts = data["disc_number"].split("/")
        dn = int(parts[0]) if parts[0] else 0
        total = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        audio.tags["disk"] = [(dn, total)]

    if cover_bytes is not None:
        compressed = _compress_cover(cover_bytes, max_cover_size, cover_quality)
        audio.tags["covr"] = [MP4Cover(compressed, imageformat=MP4Cover.FORMAT_JPEG)]

    audio.save()


def get_cover_bytes(filepath: str) -> Optional[bytes]:
    if filepath.lower().endswith(".flac"):
        audio = FLAC(filepath)
        if audio.pictures:
            return audio.pictures[0].data
    else:
        audio = MP4(filepath)
        covrs = (audio.tags or {}).get("covr")
        if covrs:
            return bytes(covrs[0])
    return None


def set_cover_only(filepath: str, cover_bytes: bytes,
                   max_cover_size: int = 1500, cover_quality: int = 90):
    write_metadata(filepath, {}, cover_bytes, max_cover_size, cover_quality)
