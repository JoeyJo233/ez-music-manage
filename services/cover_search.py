"""Cover art search - iTunes + NetEase (pyncm)."""

from __future__ import annotations

import asyncio
from typing import Optional

import httpx


async def search_itunes(artist: str, album: str, limit: int = 5) -> list[dict]:
    term = f"{artist} {album}".strip()
    if not term:
        return []
    url = "https://itunes.apple.com/search"
    params = {"term": term, "entity": "album", "limit": limit}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        results = []
        for item in data.get("results", [])[:limit]:
            art_url = item.get("artworkUrl100", "")
            art_url_hq = art_url.replace("100x100bb", "800x800bb") if art_url else ""
            results.append({
                "url": art_url_hq,
                "thumbnail": art_url,
                "album": item.get("collectionName", ""),
                "artist": item.get("artistName", ""),
                "source": "itunes",
            })
        return results
    except Exception:
        return []


async def search_netease(artist: str, album: str, limit: int = 5, cookie: str = "") -> list[dict]:
    try:
        results = await asyncio.to_thread(_search_netease_sync, artist, album, limit, cookie)
        return results
    except Exception:
        return []


def _search_netease_sync(artist: str, album: str, limit: int, cookie: str) -> list[dict]:
    try:
        import pyncm
        if cookie:
            pyncm.SetCurrentSession(pyncm.LoadSessionFromString(cookie))
    except Exception:
        pass

    try:
        from pyncm.apis.cloudsearch import GetSearchResult
        keyword = f"{artist} {album}".strip()
        if not keyword:
            return []
        resp = GetSearchResult(keyword, search_type=10, limit=limit)
        results = []
        for alb in resp.get("result", {}).get("albums", [])[:limit]:
            pic_url = alb.get("picUrl", "") or alb.get("blurPicUrl", "")
            if pic_url:
                results.append({
                    "url": pic_url,
                    "thumbnail": pic_url + "?param=100y100" if pic_url else "",
                    "album": alb.get("name", ""),
                    "artist": (alb.get("artist", {}) or {}).get("name", ""),
                    "source": "netease",
                })
        return results
    except Exception:
        return []


async def search_covers(artist: str, album: str, cookie: str = "") -> list[dict]:
    itunes_task = search_itunes(artist, album)
    netease_task = search_netease(artist, album, cookie=cookie)
    itunes_results, netease_results = await asyncio.gather(itunes_task, netease_task)
    return itunes_results + netease_results


async def download_cover(url: str) -> Optional[bytes]:
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
    except Exception:
        return None
