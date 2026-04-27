from audiodb import lookup_by_mbid, lookup_by_text, lookup_artist_mood
from .retriever import CandidateSong
from .logger import logger


def enrich_candidates(candidates: list[CandidateSong]) -> list[CandidateSong]:
    """
    Attempt AudioDB enrichment for every candidate in-place.

    Strategy: MBID lookup first (exact, unambiguous); fall back to text search
    if the MBID lookup returns nothing. Failures are swallowed — an unenriched
    candidate still moves forward to the scorer with adb_* fields as None.
    """
    enriched = 0
    for song in candidates:
        result = lookup_by_mbid(song.mbid) if song.mbid else None
        if result is None:
            result = lookup_by_text(song.artist, song.title)
        if result:
            song.adb_mood            = result["mood"]
            song.adb_genre           = result["genre"]
            song.adb_style           = result["style"]
            song.adb_theme           = result["theme"]
            song.adb_community_score = result["community_score"]
            song.adb_youtube_url     = result["youtube_url"]
            song.adb_thumb_url       = result["thumb_url"]
            enriched += 1
        if result is None:
            artist_data = lookup_artist_mood(song.artist)
            if artist_data:
                song.adb_genre = artist_data["genre"]
                song.adb_mood  = artist_data["mood"]
                song.adb_style = artist_data["style"]
                enriched += 1
    logger.info(f"AudioDB enrichment: {enriched}/{len(candidates)} candidates enriched")
    return candidates
