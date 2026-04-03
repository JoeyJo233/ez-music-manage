"""Lyrics search - LRCLIB + NetEase (pyncm)."""

from __future__ import annotations

import asyncio
from typing import Optional

import httpx

MAX_LYRIC_SEARCH_RESULTS = 3


async def search_lrclib(artist: str, title: str, album: str = "") -> list[dict]:
    try:
        params = {"artist_name": artist, "track_name": title}
        if album:
            params["album_name"] = album
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://lrclib.net/api/search", params=params)
            resp.raise_for_status()
            data = resp.json()
        results = []
        for item in data[:MAX_LYRIC_SEARCH_RESULTS]:
            synced = item.get("syncedLyrics") or ""
            plain = item.get("plainLyrics") or ""
            if not synced and not plain:
                continue
            results.append({
                "source": "lrclib",
                "title": item.get("trackName", ""),
                "artist": item.get("artistName", ""),
                "album": item.get("albumName", ""),
                "synced": synced,
                "plain": plain,
                "translated": None,
                "has_synced": bool(synced),
                "has_translated": False,
            })
        return results
    except Exception:
        return []


async def search_netease(artist: str, title: str, cookie: str = "") -> list[dict]:
    try:
        return await asyncio.to_thread(_search_netease_sync, artist, title, cookie)
    except Exception:
        return []


def _search_netease_sync(artist: str, title: str, cookie: str) -> list[dict]:
    try:
        import pyncm
        if cookie:
            pyncm.SetCurrentSession(pyncm.LoadSessionFromString(cookie))
    except Exception:
        pass

    try:
        from pyncm.apis.cloudsearch import GetSearchResult
        from pyncm.apis.track import GetTrackLyrics

        keyword = f"{artist} {title}".strip()
        if not keyword:
            return []
        search_resp = GetSearchResult(keyword, search_type=1, limit=MAX_LYRIC_SEARCH_RESULTS)
        songs = search_resp.get("result", {}).get("songs", [])
        results = []
        for song in songs[:MAX_LYRIC_SEARCH_RESULTS]:
            song_id = song.get("id")
            if not song_id:
                continue
            try:
                lyric_resp = GetTrackLyrics(song_id)
            except Exception:
                continue
            lrc = lyric_resp.get("lrc", {}).get("lyric", "")
            tlrc = lyric_resp.get("tlyric", {}).get("lyric", "")
            if not lrc:
                continue
            artists = song.get("ar") or song.get("artists") or []
            artist_name = artists[0].get("name", "") if artists else ""
            album_info = song.get("al") or song.get("album") or {}
            results.append({
                "source": "netease",
                "title": song.get("name", ""),
                "artist": artist_name,
                "album": album_info.get("name", ""),
                "synced": lrc,
                "plain": "",
                "translated": tlrc or None,
                "has_synced": bool(lrc),
                "has_translated": bool(tlrc),
            })
        return results
    except Exception:
        return []


async def search_lyrics(artist: str, title: str, album: str = "", cookie: str = "") -> list[dict]:
    lrclib_task = search_lrclib(artist, title, album)
    netease_task = search_netease(artist, title, cookie=cookie)
    lrclib_results, netease_results = await asyncio.gather(lrclib_task, netease_task)
    all_results = lrclib_results + netease_results
    all_results.sort(key=lambda x: (not x["has_synced"], not x.get("has_translated", False)))
    return all_results[:MAX_LYRIC_SEARCH_RESULTS]
