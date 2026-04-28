from src.ai.guardrails import validate_input


def test_empty_string_rejected():
    ok, msg = validate_input("")
    assert ok is False
    assert msg is not None


def test_whitespace_only_rejected():
    ok, msg = validate_input("   ")
    assert ok is False
    assert msg is not None


def test_keyboard_mash_rejected():
    # (.)\1{5,} fires on 6+ consecutive identical chars
    ok, msg = validate_input("aaaaaaaaaa")
    assert ok is False
    assert msg is not None


def test_valid_sentence_accepted():
    ok, msg = validate_input("I feel calm and want something peaceful to wind down")
    assert ok is True
    assert msg is None


def test_pure_numbers_rejected():
    ok, msg = validate_input("12345")
    assert ok is False


def test_too_short_rejected():
    ok, msg = validate_input("hi")
    assert ok is False


def test_keyboard_row_mash_asdf_rejected():
    ok, msg = validate_input("asdfghjkl")
    assert ok is False
    assert msg is not None


def test_keyboard_row_mash_zxcv_rejected():
    ok, msg = validate_input("zxcvbnm")
    assert ok is False
    assert msg is not None


def test_too_long_rejected():
    ok, msg = validate_input("x" * 301)
    assert ok is False
    assert msg is not None


def test_url_rejected():
    ok, msg = validate_input("http://example.com/mood")
    assert ok is False
    assert msg is not None


def test_single_char_tokens_rejected():
    ok, msg = validate_input("a b c d e f g h")
    assert ok is False
    assert msg is not None


def test_repeated_word_spam_rejected():
    ok, msg = validate_input("happy happy happy happy happy")
    assert ok is False
    assert msg is not None
