import time
import requests
from dataclasses import dataclass, field
from typing import Optional

from .interpreter import MoodProfile

_BASE_URL = "https://musicbrainz.org/ws/2"
_USER_AGENT = "Moodwave/1.0 (academic project; sultan.samidinov001@umb.edu)"

# Module-level timestamp for rate limiting (1 req/sec — MusicBrainz hard rule)
_last_request_at: float = 0.0


@dataclass
class CandidateSong:
    mbid: str
    title: str
    artist: str
    release: str
    duration_ms: Optional[int]
    tags: list[str] = field(default_factory=list)
    mb_score: int = 0       # MusicBrainz relevance score 0–100
    adb_mood: str | None = None
    adb_genre: str | None = None
    adb_style: str | None = None
    adb_theme: str | None = None
    adb_community_score: float | None = None
    adb_youtube_url: str | None = None
    adb_thumb_url: str | None = None


def _get(url: str, params: dict) -> dict:
    """Rate-limited GET — enforces 1 req/sec MusicBrainz limit."""
    global _last_request_at
    elapsed = time.time() - _last_request_at
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    response = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": _USER_AGENT,
            "Accept": "application/json",
        },
        timeout=15,
    )
    _last_request_at = time.time()
    response.raise_for_status()
    return response.json()


def _build_query(profile: MoodProfile) -> str:
    """
    Build a Lucene OR query from MoodProfile tags.

    OR casts a wide net — the scoring engine (Chapter 4) handles ranking.
    We take genre + mood + search_keywords, normalize to tag format,
    and deduplicate.
    """
    raw_tags = [profile.genre, profile.mood] + list(profile.search_keywords)
    seen: set[str] = set()
    unique: list[str] = []
    for t in raw_tags:
        normalized = t.lower().strip().replace(" ", "-")
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)

    return " OR ".join(f"tag:{t}" for t in unique[:6])


def _parse_recording(rec: dict) -> CandidateSong:
    """Extract a clean CandidateSong from a raw MusicBrainz recording dict."""
    # Artist: join all credited names
    artist_credits = rec.get("artist-credit", [])
    name_parts = []
    for ac in artist_credits:
        if isinstance(ac, dict):
            name_parts.append(ac.get("artist", {}).get("name", ""))
            join = ac.get("joinphrase", "")
            if join:
                name_parts.append(join)
        elif isinstance(ac, str):
            name_parts.append(ac)
    artist_name = "".join(name_parts).strip() or "Unknown Artist"

    # First release title
    releases = rec.get("releases", [])
    release_title = releases[0].get("title", "") if releases else ""

    # Tags (user-curated — best proxy for mood/genre)
    tags = [t.get("name", "") for t in rec.get("tags", []) if t.get("name")]

    return CandidateSong(
        mbid=rec.get("id", ""),
        title=rec.get("title", "Unknown"),
        artist=artist_name,
        release=release_title,
        duration_ms=rec.get("length"),
        tags=tags,
        mb_score=int(rec.get("score", 0)),
    )


def fetch_candidates(
    profile: MoodProfile,
    limit: int = 25,
) -> tuple[list[CandidateSong], Optional[str]]:
    """
    Query MusicBrainz for songs matching a MoodProfile.

    Returns:
        (candidates, None)         on success
        ([], error_string)         on failure or empty results
    """
    query = _build_query(profile)
    if not query:
        return [], "Could not build a search query from the mood profile."

    try:
        data = _get(
            f"{_BASE_URL}/recording",
            params={
                "query": query,
                "fmt": "json",
                "limit": limit,
                "inc": "tags",
            },
        )

        recordings = data.get("recordings", [])

        if not recordings:
            return [], f"MusicBrainz returned no songs for: {query}"

        candidates = [_parse_recording(r) for r in recordings]
        return candidates, None

    except requests.exceptions.Timeout:
        return [], "MusicBrainz request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status == 503:
            return [], "MusicBrainz is temporarily busy (503). Try again in a moment."
        return [], f"MusicBrainz HTTP {status}: {e}"
    except Exception as e:
        return [], f"Retrieval failed: {e}"
