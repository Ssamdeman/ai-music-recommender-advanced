from dataclasses import dataclass, field

from .interpreter import MoodProfile
from .retriever import CandidateSong


@dataclass
class ScoredSong:
    candidate: CandidateSong
    score: float                        # 0–100
    reasons: list[str] = field(default_factory=list)


# ── Scoring weights (sum to 100) ──────────────────────────────────────────────
_W_RELEVANCE  = 30.0     # MusicBrainz catalog relevance score
_W_GENRE      = 25.0     # Genre tag match
_W_MOOD       = 20.0     # Mood tag match
_W_KEYWORD    = 5.0      # Per search keyword match (max 5 keywords = 25 pts)
_W_COMMUNITY  = 5.0      # AudioDB community score bonus (max 5 pts)

# Stop-words excluded from word-level matching
_STOP = {"a", "the", "of", "in", "and", "for", "to"}


def _tag_matches(song_tags: list[str], target: str) -> bool:
    """
    Multi-strategy fuzzy tag match:
      1. Exact normalized phrase match   ("lo-fi" == "lo fi")
      2. Bidirectional substring         ("smooth" in "smooth jazz")
      3. Word-level overlap              ("late night" ∩ {"late", "night", "jazz"} → {"late","night"})

    MusicBrainz tags are genre-heavy (jazz, bebop, hard bop) and rarely
    carry mood words. Strategy 3 catches partial semantic matches like
    "smooth sax" → "smooth jazz", or "night" → "late night".
    """
    t_phrase = target.lower().replace("-", " ").strip()
    t_words = set(t_phrase.split()) - _STOP

    for tag in song_tags:
        tag_phrase = tag.lower().replace("-", " ").strip()
        tag_words = set(tag_phrase.split()) - _STOP

        # 1. Exact
        if t_phrase == tag_phrase:
            return True

        # 2. Substring
        if t_phrase in tag_phrase or tag_phrase in t_phrase:
            return True

        # 3. Word overlap — single-word target needs 1 match;
        #    multi-word target needs at least 2 words in common
        if t_words and tag_words:
            overlap = t_words & tag_words
            min_needed = 1 if len(t_words) == 1 else 2
            if len(overlap) >= min_needed:
                return True

    return False


def _artist_key(song: CandidateSong) -> str:
    return song.artist.lower().strip()


def score_candidate(profile: MoodProfile, song: CandidateSong) -> ScoredSong:
    """
    Score one CandidateSong against a MoodProfile.

    Tiers adapted from Module 3 recommender.py:
      - Catalog relevance : mb_score × 0.30  (0–30 pts)
      - Genre tag match   : +25 pts
      - Mood tag match    : +20 pts          (rarely fires — MusicBrainz tags are genre-heavy)
      - Keyword matches   : +5 pts each, max 25 pts

    Actual MusicBrainz tags for each song are appended to reasons so
    you can inspect what the catalog is actually returning.
    """
    reasons: list[str] = []

    # ── Debug: show raw tags ──────────────────────────────────────────────────
    if song.tags:
        reasons.append(f"[MB tags: {', '.join(song.tags[:10])}]")
    else:
        reasons.append("[MB tags: none returned]")

    # ── Tier 1: MusicBrainz relevance ────────────────────────────────────────
    relevance_pts = song.mb_score * (_W_RELEVANCE / 100.0)
    reasons.append(f"catalog relevance {song.mb_score}/100 (+{relevance_pts:.1f})")

    # ── Tier 2: Genre match ───────────────────────────────────────────────────
    genre_pts = 0.0
    adb_genre_fields = [f for f in [song.adb_genre, song.adb_style] if f]
    genre_source = adb_genre_fields if adb_genre_fields else song.tags
    if _tag_matches(genre_source, profile.genre):
        genre_pts = _W_GENRE
        src = "AudioDB" if adb_genre_fields else "MB tags"
        reasons.append(f"genre '{profile.genre}' matched ({src}) (+{genre_pts:.0f})")

    # ── Tier 3: Mood match ────────────────────────────────────────────────────
    mood_pts = 0.0
    adb_mood_field = [song.adb_mood] if song.adb_mood else []
    mood_source = adb_mood_field if adb_mood_field else song.tags
    if _tag_matches(mood_source, profile.mood):
        mood_pts = _W_MOOD
        src = "AudioDB" if adb_mood_field else "MB tags"
        reasons.append(f"mood '{profile.mood}' matched ({src}) (+{mood_pts:.0f})")
    else:
        src = "AudioDB" if adb_mood_field else "MB tags"
        reasons.append(f"mood '{profile.mood}' not matched ({src}) (+0)")

    # ── Tier 4: Keyword matches ───────────────────────────────────────────────
    kw_pts = 0.0
    matched_kws: list[str] = []
    unmatched_kws: list[str] = []
    for kw in profile.search_keywords:
        if kw_pts >= _W_KEYWORD * 5:
            break
        if _tag_matches(song.tags, kw):
            kw_pts = min(kw_pts + _W_KEYWORD, _W_KEYWORD * 5)
            matched_kws.append(kw)
        else:
            unmatched_kws.append(kw)

    if matched_kws:
        reasons.append(f"keywords matched: {matched_kws} (+{kw_pts:.0f})")
    if unmatched_kws:
        reasons.append(f"keywords not in MB data: {unmatched_kws} (+0)")

    community_pts = 0.0
    if song.adb_community_score is not None:
        community_pts = round((song.adb_community_score / 10.0) * _W_COMMUNITY, 1)
        reasons.append(f"community score {song.adb_community_score:.1f}/10 (+{community_pts})")

    total = min(100.0, relevance_pts + genre_pts + mood_pts + kw_pts + community_pts)
    return ScoredSong(candidate=song, score=round(total, 1), reasons=reasons)


def _dedupe_by_artist(ranked: list[ScoredSong], k: int) -> list[ScoredSong]:
    """
    Artist diversity pass — keep only the highest-scoring song per artist.
    Pulls from further down the ranked list to fill all k slots.
    This runs AFTER score sorting so we never promote a worse song;
    we just skip duplicates.
    """
    seen: set[str] = set()
    result: list[ScoredSong] = []
    for s in ranked:
        key = _artist_key(s.candidate)
        if key not in seen:
            seen.add(key)
            result.append(s)
        if len(result) >= k:
            break
    return result


def rank_candidates(
    profile: MoodProfile,
    candidates: list[CandidateSong],
    k: int = 5,
    threshold: float = 15.0,
) -> list[ScoredSong]:
    """
    Score all candidates, filter below threshold, apply diversity rules,
    return top-k — preserving the Module 3 recommender logic pattern.

    Diversity rules (applied in order):
      1. Genre+mood tag rule (from Module 3): if top 2 share both tags,
         force a different song to position 3.
      2. Artist deduplication: no two songs from the same artist in final k.
    """
    scored = [score_candidate(profile, c) for c in candidates]

    eligible = [s for s in scored if s.score >= threshold]
    if not eligible:
        eligible = sorted(scored, key=lambda s: s.score, reverse=True)
    else:
        eligible.sort(key=lambda s: s.score, reverse=True)

    # ── Diversity rule 1: genre+mood tag (Module 3 original) ─────────────────
    if len(eligible) >= 3:
        g = profile.genre.lower().replace(" ", "-")
        m = profile.mood.lower().replace(" ", "-")
        top0_tags = {t.lower().replace(" ", "-") for t in eligible[0].candidate.tags}
        top1_tags = {t.lower().replace(" ", "-") for t in eligible[1].candidate.tags}

        if g in top0_tags and g in top1_tags and m in top0_tags and m in top1_tags:
            diversity_pick = next(
                (s for s in eligible[2:]
                 if g not in {t.lower().replace(" ", "-") for t in s.candidate.tags}
                 or m not in {t.lower().replace(" ", "-") for t in s.candidate.tags}),
                None,
            )
            if diversity_pick:
                rest = [s for s in eligible[2:] if s is not diversity_pick]
                eligible = [eligible[0], eligible[1], diversity_pick] + rest

    # ── Diversity rule 2: artist deduplication ────────────────────────────────
    # Pass the full eligible list so we can pull replacements from further down
    return _dedupe_by_artist(eligible, k)
