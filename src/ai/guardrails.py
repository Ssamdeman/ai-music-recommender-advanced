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

    return True, None
