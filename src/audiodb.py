import time
import requests

from ai.retriever import CandidateSong

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


def lookup_artist_mood(artist: str) -> dict | None:
    """
    Artist-level fallback when track-level enrichment fails.
    Returns genre/mood/style from the artist profile, or None on any failure.
    """
    if not artist:
        return None

    data = _get(f"{_BASE_URL}/search.php", params={"s": artist})
    if not data:
        return None

    artists = data.get("artists") or []
    if not artists:
        return None

    a = artists[0]
    return {
        "genre": a.get("strGenre") or None,
        "mood":  a.get("strMood") or None,
        "style": a.get("strStyle") or None,
    }



# Seed artists for the fallback pool — chosen to span common moods and genres.
# mostloved.php returns 404 on the free tier; track-top10.php is the working equivalent.
_FALLBACK_SEED_ARTISTS = [
    "Coldplay", "Adele", "Arctic Monkeys", "Billie Eilish",
    "Frank Ocean", "The Weeknd", "Radiohead", "Lana Del Rey",
]


def fetch_mostloved() -> list[CandidateSong]:
    """
    Build a fallback pool of pre-enriched CandidateSongs from track-top10 calls.

    Note: mostloved.php returns 404 on the free tier. track-top10.php is the
    working equivalent — same schema, same response fields. We seed from a
    curated artist list to get genre and mood diversity across the pool.
    Returns [] on any failure — never raises.
    """
    candidates: list[CandidateSong] = []
    for artist in _FALLBACK_SEED_ARTISTS:
        try:
            data = _get(f"{_BASE_URL}/track-top10.php", params={"s": artist})
            if not data:
                continue
            items = data.get("track") or []
            for item in items:
                try:
                    enriched = _normalize(item)
                    duration_raw = int(item.get("intDuration") or 0)
                    candidates.append(CandidateSong(
                        title=item.get("strTrack") or "",
                        artist=item.get("strArtist") or "",
                        mbid=item.get("strMusicBrainzID") or "",
                        release=item.get("strAlbum") or "",
                        duration_ms=duration_raw if duration_raw else None,
                        tags=[],
                        mb_score=0,
                        adb_mood=enriched["mood"],
                        adb_genre=enriched["genre"],
                        adb_style=enriched["style"],
                        adb_theme=enriched["theme"],
                        adb_community_score=enriched["community_score"],
                        adb_youtube_url=enriched["youtube_url"],
                        adb_thumb_url=enriched["thumb_url"],
                    ))
                except Exception:
                    continue
        except Exception:
            continue
    return candidates


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
