from audiodb import _normalize  # audiodb.py lives in src/; conftest.py puts src/ on sys.path


def _full_raw() -> dict:
    return {
        "strMood":       "Melancholic",
        "strGenre":      "Rock",
        "strStyle":      "Alternative",
        "strTheme":      "Night",
        "intScore":      "8",
        "strMusicVid":   "https://youtube.com/watch?v=abc",
        "strTrackThumb": "https://cdn.audiodb.com/thumb.jpg",
        "strLocked":     "",
    }


def test_all_fields_present_with_correct_types():
    result = _normalize(_full_raw())
    expected_keys = {"mood", "genre", "style", "theme", "community_score", "youtube_url", "thumb_url"}
    assert set(result.keys()) == expected_keys
    assert result["mood"] == "Melancholic"
    assert result["genre"] == "Rock"
    assert result["style"] == "Alternative"
    assert result["theme"] == "Night"
    assert isinstance(result["community_score"], float)
    assert result["youtube_url"] == "https://youtube.com/watch?v=abc"
    assert result["thumb_url"] == "https://cdn.audiodb.com/thumb.jpg"


def test_null_mood_field_returns_none():
    raw = _full_raw()
    raw["strMood"] = None
    result = _normalize(raw)
    assert result["mood"] is None


def test_locked_track_returns_all_none():
    raw = _full_raw()
    raw["strLocked"] = "Locked"
    result = _normalize(raw)
    assert set(result.keys()) == {"mood", "genre", "style", "theme", "community_score", "youtube_url", "thumb_url"}
    for val in result.values():
        assert val is None


def test_empty_string_fields_normalized_to_none():
    raw = _full_raw()
    raw["strMood"] = ""
    raw["strGenre"] = ""
    result = _normalize(raw)
    assert result["mood"] is None
    assert result["genre"] is None


def test_seven_keys_always_present_on_empty_input():
    result = _normalize({})
    assert len(result) == 7
    assert set(result.keys()) == {"mood", "genre", "style", "theme", "community_score", "youtube_url", "thumb_url"}
