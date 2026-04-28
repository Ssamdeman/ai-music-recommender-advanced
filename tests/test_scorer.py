from src.ai.scorer import score_candidate, _tag_matches, ScoredSong
from src.ai.interpreter import MoodProfile
from src.ai.retriever import CandidateSong


def _make_profile(**kwargs) -> MoodProfile:
    defaults = dict(
        genre="jazz", mood="melancholic", energy=0.4, valence=0.3,
        acoustic=True, tempo="slow", search_keywords=["late night", "jazz"],
    )
    defaults.update(kwargs)
    return MoodProfile(**defaults)


def _make_song(**kwargs) -> CandidateSong:
    defaults = dict(
        mbid="test-mbid", title="Test Song", artist="Test Artist",
        release="Test Album", duration_ms=240000, tags=[], mb_score=0,
        adb_mood=None, adb_genre=None, adb_style=None, adb_theme=None,
        adb_community_score=None, adb_youtube_url=None, adb_thumb_url=None,
    )
    defaults.update(kwargs)
    return CandidateSong(**defaults)


# ── _tag_matches ──────────────────────────────────────────────────────────────

def test_tag_matches_exact():
    assert _tag_matches(["melancholic"], "melancholic") is True


def test_tag_matches_hyphen_normalized():
    assert _tag_matches(["lo-fi"], "lo fi") is True


def test_tag_matches_bidirectional_substring():
    assert _tag_matches(["smooth jazz"], "smooth") is True
    assert _tag_matches(["smooth"], "smooth jazz") is True


def test_tag_matches_word_overlap_multi_word_target():
    # "late night" needs 2-word overlap; "late night jazz" provides both
    assert _tag_matches(["late night jazz"], "late night") is True


def test_tag_matches_no_match():
    assert _tag_matches(["pop", "dance"], "melancholic") is False


def test_tag_matches_empty_tags():
    assert _tag_matches([], "jazz") is False


# ── score_candidate ───────────────────────────────────────────────────────────

def test_mood_pts_exact_audiodb_match():
    # adb_mood exact match → mood tier fires for 20 pts
    profile = _make_profile(mood="melancholic", search_keywords=[])
    song = _make_song(adb_mood="melancholic", mb_score=0)
    result = score_candidate(profile, song)
    assert result.score >= 20.0


def test_mood_pts_no_match():
    # adb_mood present but wrong → 0 pts; mb_score=0 → total=0
    profile = _make_profile(mood="melancholic", search_keywords=[])
    song = _make_song(adb_mood="energetic", mb_score=0)
    result = score_candidate(profile, song)
    assert result.score == 0.0


def test_genre_pts_audiodb_match():
    # adb_genre exact match → genre tier fires for 25 pts
    profile = _make_profile(genre="rock", mood="xyz-nonexistent", search_keywords=[])
    song = _make_song(adb_genre="rock", mb_score=0)
    result = score_candidate(profile, song)
    assert result.score >= 25.0


def test_community_bonus_score_8():
    # (8.0 / 10.0) * 5.0 = 4.0 community pts; no other match → total=4.0
    profile = _make_profile(genre="xyz-nonexistent", mood="xyz-nonexistent", search_keywords=[])
    song = _make_song(adb_community_score=8.0, mb_score=0)
    result = score_candidate(profile, song)
    assert result.score == 4.0


def test_unenriched_song_does_not_crash():
    # All adb_* None + no tags → tag-matching falls back gracefully, returns ScoredSong
    profile = _make_profile()
    song = _make_song()
    result = score_candidate(profile, song)
    assert isinstance(result, ScoredSong)


def test_score_never_exceeds_100():
    # mb=100 (30) + genre (25) + mood (20) + 5 keywords (25) + community=10 (5) = 105 → capped at 100
    profile = _make_profile(
        genre="jazz", mood="melancholic",
        search_keywords=["jazz", "melancholic", "late night", "piano", "slow"],
    )
    song = _make_song(
        mb_score=100,
        adb_mood="melancholic",
        adb_genre="jazz",
        adb_community_score=10.0,
        tags=["jazz", "melancholic", "late night", "piano", "slow"],
    )
    result = score_candidate(profile, song)
    assert result.score <= 100.0
