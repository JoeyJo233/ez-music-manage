"""Directory recursive scanner - maintains in-memory song index."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from mutagen.flac import FLAC
from mutagen.mp4 import MP4

SUPPORTED_EXTENSIONS = {".flac", ".m4a", ".aac"}


@dataclass
class SongInfo:
    id: str
    file_path: str
    filename: str
    title: str
    artist: str
    album: str
    album_artist: str
    year: str
    track_number: str
    disc_number: str
    genre: str
    composer: str
    comment: str
    duration: float
    format: str  # "FLAC" or "AAC"
    has_cover: bool
    has_lrc: bool
    has_lrc_trans: bool
    cover_thumbnail: Optional[bytes] = field(default=None, repr=False)


class LibraryScanner:
    def __init__(self):
        self.songs: dict[str, SongInfo] = {}

    def _make_id(self, filepath: str) -> str:
        return hashlib.md5(filepath.encode("utf-8")).hexdigest()

    def _read_flac(self, path: str) -> SongInfo:
        audio = FLAC(path)
        tags = audio.tags or {}

        def tag(key: str) -> str:
            vals = tags.get(key)
            return vals[0] if vals else ""

        has_cover = bool(audio.pictures)
        duration = audio.info.length if audio.info else 0.0

        return SongInfo(
            id=self._make_id(path),
            file_path=path,
            filename=os.path.basename(path),
            title=tag("TITLE") or Path(path).stem,
            artist=tag("ARTIST"),
            album=tag("ALBUM"),
            album_artist=tag("ALBUMARTIST"),
            year=tag("DATE"),
            track_number=tag("TRACKNUMBER"),
            disc_number=tag("DISCNUMBER"),
            genre=tag("GENRE"),
            composer=tag("COMPOSER"),
            comment=tag("COMMENT"),
            duration=duration,
            format="FLAC",
            has_cover=has_cover,
            has_lrc=False,
            has_lrc_trans=False,
        )

    def _read_m4a(self, path: str) -> SongInfo:
        audio = MP4(path)
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

        has_cover = bool(tags.get("covr"))
        duration = audio.info.length if audio.info else 0.0

        return SongInfo(
            id=self._make_id(path),
            file_path=path,
            filename=os.path.basename(path),
            title=tag("\xa9nam") or Path(path).stem,
            artist=tag("\xa9ART"),
            album=tag("\xa9alb"),
            album_artist=tag("aART"),
            year=tag("\xa9day"),
            track_number=tag_int_pair("trkn"),
            disc_number=tag_int_pair("disk"),
            genre=tag("\xa9gen"),
            composer=tag("\xa9wrt"),
            comment=tag("\xa9cmt"),
            duration=duration,
            format="AAC",
            has_cover=has_cover,
            has_lrc=False,
            has_lrc_trans=False,
        )

    def _check_lrc(self, song: SongInfo):
        base = os.path.splitext(song.file_path)[0]
        song.has_lrc = os.path.isfile(base + ".lrc")
        song.has_lrc_trans = os.path.isfile(base + ".trans.lrc")

    def scan(self, root_path: str) -> list[dict]:
        root = os.path.expanduser(root_path)
        if not os.path.isdir(root):
            raise FileNotFoundError(f"Directory not found: {root}")

        self.songs.clear()

        for dirpath, _dirs, files in os.walk(root):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue
                fpath = os.path.join(dirpath, fname)
                try:
                    if ext == ".flac":
                        song = self._read_flac(fpath)
                    else:
                        song = self._read_m4a(fpath)
                    self._check_lrc(song)
                    self.songs[song.id] = song
                except Exception:
                    continue

        return [self._song_summary(s) for s in self.songs.values()]

    def _song_summary(self, s: SongInfo) -> dict:
        return {
            "id": s.id,
            "title": s.title,
            "artist": s.artist,
            "album": s.album,
            "album_artist": s.album_artist,
            "duration": round(s.duration, 2),
            "format": s.format,
            "has_cover": s.has_cover,
            "has_lrc": s.has_lrc,
            "has_lrc_trans": s.has_lrc_trans,
            "filename": s.filename,
            "file_path": s.file_path,
        }

    def get_song(self, song_id: str) -> Optional[SongInfo]:
        return self.songs.get(song_id)

    def get_all_summaries(self) -> list[dict]:
        return [self._song_summary(s) for s in self.songs.values()]


# Global singleton
library = LibraryScanner()
