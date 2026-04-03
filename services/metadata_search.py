"""Online metadata lookup via iTunes Search API (multi-country)."""
from __future__ import annotations

import asyncio
from difflib import SequenceMatcher

import httpx


def _album_similarity(query: str, candidate: str) -> float:
    """Return 0-1 similarity between two album name strings."""
    a = query.lower().strip()
    b = candidate.lower().strip()
    if not a or not b:
        return 0.0
    if a in b or b in a:
        return 0.9
    return SequenceMatcher(None, a, b).ratio()


async def _search_itunes_country(
    artist: str, title: str, limit: int, country: str
) -> list[dict]:
    term = f"{artist} {title}".strip()
    if not term:
        return []
    url = "https://itunes.apple.com/search"
    params = {"term": term, "entity": "musicTrack", "limit": limit, "country": country}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        results = []
        for item in data.get("results", []):
            release = item.get("releaseDate", "")
            year = release[:4] if release else ""
            track_num = item.get("trackNumber")
            disc_num = item.get("discNumber")
            collection_name = item.get("collectionName", "")
            artwork_url = item.get("artworkUrl100", "")
            artwork_url_hq = artwork_url.replace("100x100bb", "800x800bb") if artwork_url else ""
            results.append({
                "title": item.get("trackName", ""),
                "artist": item.get("artistName", ""),
                "album": collection_name,
                "album_artist": item.get("collectionArtistName", "") or item.get("artistName", ""),
                "year": year,
                "genre": item.get("primaryGenreName", ""),
                "track_number": str(track_num) if track_num else "",
                "disc_number": str(disc_num) if disc_num else "",
                "album_score": 0.0,
                "artwork_url": artwork_url,
                "artwork_url_hq": artwork_url_hq,
                "store": country,
                "source": f"itunes-{country}",
            })
        return results
    except Exception:
        return []


async def search_itunes_track(
    artist: str,
    title: str,
    limit: int = 10,
    album_query: str = "",
    countries: list[str] | None = None,
) -> list[dict]:
    if not countries:
        countries = ["US"]

    # Search all countries in parallel
    tasks = [_search_itunes_country(artist, title, limit, c) for c in countries]
    country_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Merge, deduplicating by (normalized_title, normalized_album)
    seen: set[tuple[str, str]] = set()
    merged: list[dict] = []
    for batch in country_results:
        if isinstance(batch, Exception):
            continue
        for r in batch:
            key = (r["title"].lower().strip(), r["album"].lower().strip())
            if key not in seen:
                seen.add(key)
                merged.append(r)

    # Score and sort by album similarity if album_query given
    if album_query:
        for r in merged:
            r["album_score"] = round(_album_similarity(album_query, r["album"]), 3)
        merged.sort(key=lambda x: x["album_score"], reverse=True)

    return merged
