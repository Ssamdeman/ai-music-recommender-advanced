import json
from dataclasses import dataclass, field
from typing import Optional

from .llm_client import call_llm


@dataclass
class MoodProfile:
    """
    Structured musical intent extracted from plain-English user input.

    Designed to be flexible — fields map loosely to the scoring engine
    (recommender.py) but also carry search_keywords for MusicBrainz queries
    in Chapter 3, whose schema we don't yet know.
    """
    genre: str                      # e.g. "jazz", "lo-fi", "rock"
    mood: str                       # e.g. "melancholic", "energetic", "calm"
    energy: float                   # 0.0 (very calm) → 1.0 (very intense)
    valence: float                  # 0.0 (dark/sad) → 1.0 (bright/happy)
    acoustic: bool                  # True = prefers acoustic feel
    tempo: str                      # "slow" | "medium" | "fast"
    search_keywords: list[str] = field(default_factory=list)  # for MusicBrainz


_SYSTEM_PROMPT = """\
You are a music taste interpreter.
Given a user's description of their mood or situation, extract their musical preferences.
Respond ONLY with valid JSON — no markdown fences, no explanation, nothing else.

Required schema:
{
  "genre": "<one of: pop, rock, jazz, classical, electronic, hip-hop, r&b, lo-fi, metal, country, indie, folk>",
  "mood": "<one of: happy, sad, angry, calm, melancholic, energetic, romantic, anxious, nostalgic, epic>",
  "energy": <float 0.0–1.0>,
  "valence": <float 0.0–1.0>,
  "acoustic": <true or false>,
  "tempo": "<slow|medium|fast>",
  "search_keywords": ["<tag1>", "<tag2>", "<tag3>"]
}

Rules:
- energy: 0.0 = completely quiet/passive, 1.0 = explosive/intense
- valence: 0.0 = dark, grief, tension  |  1.0 = joyful, warm, uplifting
- search_keywords: 2–4 short music tags describing the emotional vibe
  (e.g. "late night drive", "rainy window", "cinematic swell", "quiet focus")
- Output valid JSON only. Any other text will break the system.\
"""


def interpret_mood(user_text: str) -> tuple[Optional[MoodProfile], Optional[str]]:
    """
    Parse plain-English mood description into a structured MoodProfile.

    Returns:
        (MoodProfile, None)     on success
        (None, error_string)    on failure
    """
    if not user_text.strip():
        return None, "Empty input — nothing to interpret."

    try:
        raw = call_llm(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_text.strip()},
            ],
            temperature=0.2,
        )

        data = json.loads(raw.strip())

        profile = MoodProfile(
            genre=str(data.get("genre", "pop")).lower().strip(),
            mood=str(data.get("mood", "calm")).lower().strip(),
            energy=max(0.0, min(1.0, float(data.get("energy", 0.5)))),
            valence=max(0.0, min(1.0, float(data.get("valence", 0.5)))),
            acoustic=bool(data.get("acoustic", False)),
            tempo=str(data.get("tempo", "medium")).lower().strip(),
            search_keywords=[str(k) for k in data.get("search_keywords", [])],
        )
        return profile, None

    except json.JSONDecodeError as e:
        return None, f"AI returned malformed JSON: {e}"
    except (KeyError, ValueError, TypeError) as e:
        return None, f"Unexpected AI response shape: {e}"
    except EnvironmentError as e:
        return None, str(e)
    except Exception as e:
        return None, f"Interpretation failed: {e}"
