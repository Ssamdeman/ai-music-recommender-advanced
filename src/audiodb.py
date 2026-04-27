import time
import requests

_BASE_URL = "https://www.theaudiodb.com/api/v1/json/2"
_TIMEOUT = 10


def _normalize(raw: dict) -> dict:
    """
    Map a raw AudioDB track object to the normalized schema Moodwave uses.
    All seven keys are always present; values may be None.
    Locked tracks return the dict with every enrichment field as None.
    """
    if (raw.get("strLocked") or "").strip().lower() == "locked":
        return {
            "mood": None,
            "genre": None,
            "style": None,
            "theme": None,
            "community_score": None,
            "youtube_url": None,
            "thumb_url": None,
        }

    score_raw = raw.get("intScore")
    try:
        community_score = float(score_raw) if score_raw is not None else None
    except (ValueError, TypeError):
        community_score = None

    return {
        "mood":            raw.get("strMood") or None,
        "genre":           raw.get("strGenre") or None,
        "style":           raw.get("strStyle") or None,
        "theme":           raw.get("strTheme") or None,
        "community_score": community_score,
        "youtube_url":     raw.get("strMusicVid") or None,
        "thumb_url":       raw.get("strTrackThumb") or None,
    }


def _get(url: str, params: dict | None = None) -> dict | None:
    """
    GET with one 429 retry (2 s wait). Returns parsed JSON or None on any failure.
    Never raises — all errors are swallowed and return None.
    """
    for attempt in range(2):
        try:
            response = requests.get(url, params=params, timeout=_TIMEOUT)
            if response.status_code == 429:
                if attempt == 0:
                    time.sleep(2)
                    continue
                return None
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    return None


def lookup_by_mbid(mbid: str) -> dict | None:
    """
    Enrich a track using its MusicBrainz recording ID.

    Preferred over text search — MBID lookup is exact and unambiguous.
    Returns a normalized enrichment dict, or None if the lookup fails entirely.
    """
    if not mbid:
        return None

    data = _get(f"{_BASE_URL}/track-mb.php", params={"i": mbid})
    if not data:
        return None

    tracks = data.get("track") or []
    if not tracks:
        return None

    return _normalize(tracks[0])


def lookup_by_text(artist: str, title: str) -> dict | None:
    """
    Enrich a track by artist name + track title.

    Fallback for when no MBID is available. Returns the first result — AudioDB
    search is deterministic enough for well-known tracks but may misfire on
    ambiguous titles. Prefer lookup_by_mbid when a MBID exists.
    Returns a normalized enrichment dict, or None if the lookup fails entirely.
    """
    if not artist or not title:
        return None

    data = _get(f"{_BASE_URL}/searchtrack.php", params={"s": artist, "t": title})
    if not data:
        return None

    tracks = data.get("track") or []
    if not tracks:
        return None

    return _normalize(tracks[0])
