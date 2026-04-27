import logging
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import MoodProfile
    from .scorer import ScoredSong

# ── Log file setup ────────────────────────────────────────────────────────────
# Navigate from src/ai/ → src/ → project root → logs/
_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "app.log"

_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))

logger = logging.getLogger("moodwave")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(_handler)


# ── Pipeline log helpers ──────────────────────────────────────────────────────

def log_run_start(user_input: str) -> None:
    logger.info("=" * 60)
    logger.info(f"RUN START | input={user_input!r}")


def log_validation_fail(user_input: str, reason: str) -> None:
    logger.warning(f"GUARDRAIL | input={user_input!r} | reason={reason}")


def log_profile(profile: "MoodProfile") -> None:
    logger.info(
        f"PROFILE   | genre={profile.genre} mood={profile.mood} "
        f"energy={profile.energy:.2f} valence={profile.valence:.2f} "
        f"acoustic={profile.acoustic} tempo={profile.tempo} "
        f"keywords={profile.search_keywords}"
    )


def log_retrieval(count: int, error: Optional[str]) -> None:
    if error:
        logger.error(f"RETRIEVAL | FAILED — {error}")
    else:
        logger.info(f"RETRIEVAL | {count} songs fetched from MusicBrainz")


def log_ranked(ranked: "list[ScoredSong]") -> None:
    entries = [
        f'"{s.candidate.title}" by {s.candidate.artist} ({s.score:.0f}/100)'
        for s in ranked
    ]
    logger.info(f"RANKED    | top {len(entries)}: {entries}")


def log_explanation(success: bool, error: Optional[str] = None) -> None:
    if success:
        logger.info("EXPLAIN   | LLM explanation generated")
    else:
        logger.error(f"EXPLAIN   | FAILED — {error}")


def log_error(stage: str, error: str) -> None:
    logger.error(f"ERROR     | stage={stage} — {error}")
