import re
from typing import Optional


def validate_input(text: str) -> tuple[bool, Optional[str]]:
    """
    Validate user mood input before it hits the LLM.

    Returns:
        (True, None)             — input is acceptable
        (False, error_message)   — input rejected; show the message in UI
    """
    stripped = text.strip()

    if not stripped:
        return False, "Tell me how you're feeling first."

    if len(stripped) < 3:
        return False, "A little more please — try a few words at least."

    if re.fullmatch(r"[\d\s\.,]+", stripped):
        return False, "That looks like numbers. Describe your mood in words."

    alpha_ratio = sum(c.isalpha() for c in stripped) / len(stripped)
    if alpha_ratio < 0.4:
        return False, "I need a few real words to understand your mood."

    # Keyboard mashing — same character repeated 5+ times
    if re.search(r"(.)\1{5,}", stripped):
        return False, "Try describing your mood with a few words."

    # No-spaces single token too long — catches random strings without word breaks
    # Longest real single mood word ("unenthusiastic") is 14 chars
    if " " not in stripped and len(stripped) > 14:
        return False, "That doesn't look like a mood description. Try something like: 'I need something upbeat for my morning run.'"

    # Low vowel ratio — catches keyboard row mashing (asdfghjkl, zxcvbnm, etc.)
    # Real mood descriptions in English have at least 20% vowels
    if len(stripped) > 6:
        vowel_ratio = sum(c in "aeiouAEIOU" for c in stripped) / len(stripped)
        if vowel_ratio < 0.20:
            return False, "That doesn't look like a mood description. Try something like: 'I need something upbeat for my morning run.'"

    # Check A — Max length (prompt injection / paste protection)
    if len(stripped) > 300:
        return False, "That's a bit long — describe your mood in a sentence or two."

    # Check B — URL detection
    if re.search(r"https?://|www\.", stripped, re.IGNORECASE):
        return False, "That looks like a link. Describe how you're feeling instead."

    # Checks C & D share a token list
    tokens = stripped.split()

    # Check C — Single-character spaced tokens ("a b c d e f")
    if len(tokens) >= 4 and all(len(t) == 1 for t in tokens):
        return False, "That doesn't look like a mood description. Try something like: 'I need something upbeat for my morning run.'"

    # Check D — Repeated word spam ("happy happy happy happy")
    if len(tokens) >= 4:
        most_common_count = max(tokens.count(t.lower()) for t in tokens)
        if most_common_count / len(tokens) > 0.6:
            return False, "Try describing your mood with a few different words."

    return True, None
