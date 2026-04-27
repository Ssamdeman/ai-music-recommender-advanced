from typing import Optional

from .interpreter import MoodProfile
from .scorer import ScoredSong
from .llm_client import call_llm


_SYSTEM_PROMPT = """\
You are a warm, perceptive music concierge — knowledgeable but never clinical.
Someone described their mood and you found songs that match. Explain why in flowing prose.

Rules:
- Mention every song by title and artist at least once
- Be specific — connect each song's feel to what the person actually said
- Sound like a thoughtful friend who knows music deeply, not a recommendation engine
- Write in continuous prose: no bullet points, no numbered lists, no headers
- Do not open with "Here are your songs" or similar preamble — start mid-thought
- Under 150 words total
- Warm, unhurried tone — the reader should feel understood, not processed
"""


def explain_recommendations(
    user_text: str,
    profile: MoodProfile,
    ranked: list[ScoredSong],
) -> tuple[Optional[str], Optional[str]]:
    """
    Ask the LLM to write a plain-English paragraph explaining why the ranked
    songs fit the user's mood.

    Returns:
        (explanation_text, None)    on success
        (None, error_string)        on failure
    """
    if not ranked:
        return None, "No songs to explain."

    song_list = "\n".join(
        f'{i}. "{s.candidate.title}" by {s.candidate.artist}'
        for i, s in enumerate(ranked, 1)
    )

    user_message = (
        f'The user said: "{user_text}"\n\n'
        f"Mood profile: {profile.mood}, {profile.genre}, "
        f"energy {profile.energy:.0%}, valence {profile.valence:.0%}, "
        f"tempo {profile.tempo}.\n\n"
        f"Songs found:\n{song_list}\n\n"
        "Write a warm, specific explanation of why these songs fit what they described."
    )

    try:
        text = call_llm(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.72,
        )
        return text.strip(), None
    except EnvironmentError as e:
        return None, str(e)
    except Exception as e:
        return None, f"Explanation failed: {e}"
