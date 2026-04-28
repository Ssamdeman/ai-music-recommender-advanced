# Model Card: Moodwave

## Model Name
Moodwave — AI Music Recommender

## Task
Convert a plain-English mood description into 5 ranked song recommendations with a natural-language explanation, using a two-call LLM pipeline, live music catalog retrieval, and deterministic scoring.

## System Components
- **LLM (OpenRouter):** Two calls — one for structured MoodProfile extraction, one for explanation generation
- **MusicBrainz:** Candidate retrieval (up to 25 tracks)
- **TheAudioDB:** Enrichment — mood, genre, style, theme, cover art, YouTube links per track
- **Scoring engine:** Deterministic, 0–100, weighted arithmetic — no LLM involvement

## Data Sources
No training data. At inference time: live MusicBrainz catalog (millions of recordings), TheAudioDB metadata (mood/genre per track), user's free-text input.

## Strengths
- Natural language input — no dropdowns or checkboxes
- Real catalog — every recommendation is an actual song that exists
- Transparent scoring — reasons shown in UI, reproducible across runs
- Graceful degradation — unenriched candidates still score via MusicBrainz tags; fallback pool prevents empty results

## Observed Biases and Limitations
- AudioDB coverage is uneven — Western, English-language, mainstream artists are well-represented; regional, independent, and non-English artists frequently return null mood/genre fields and score lower regardless of actual fit
- Fallback pool is seeded from 8 hand-picked artists, introducing implicit style bias when retrieval is thin
- Community score bonus favors established tracks over obscure ones that might fit better emotionally
- Mood vocabulary mismatch: LLM may extract "melancholy" while AudioDB stores "Sad" — fuzzy matching narrows but does not close this gap
- No BPM, valence, or energy from the catalog — these come from LLM extraction, not measured audio features

## Intended Use
Music discovery and mood-based recommendation. Personal, casual, demo-grade. Not intended for production or commercial deployment.

## Misuse Considerations
Low-stakes domain — no PII stored, no health or financial decisions. Main technical risk: user text flows directly into the LLM prompt, making prompt injection theoretically possible. Mitigations: input guardrails reject short/incoherent text before the LLM is called; structured JSON extraction format limits injection impact.

## Testing Results
- 25/25 unit tests pass (`pytest tests/`) covering scorer logic, input guardrails, and AudioDB field normalization — no network calls required
- Enrichment rate: 60–80% of candidates enriched per run; unenriched candidates score via sparse MusicBrainz tags
- Fallback triggered correctly when candidate pool drops below 5
- `mostloved.php` documented as free-tier but returned 404 in production — adapted to `track-top10.php` across genre-spanning seed artists

## AI Collaboration
This project was built in close collaboration with AI coding assistants throughout.

**Helpful:** When upgrading the scoring engine to use AudioDB mood data, the AI proposed passing `[song.adb_mood]` as a single-item list into the existing `_tag_matches` function — reusing a tested fuzzy matcher instead of writing new comparison logic.

**Flawed:** The AI implemented the `mostloved.php` fallback endpoint exactly as the API documentation described. The endpoint was actually paywalled on the free tier and returned 404 in production. Neither the AI nor the documentation flagged this ahead of time; it only surfaced during a live run.
