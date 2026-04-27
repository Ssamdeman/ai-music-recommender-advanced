# Build Plan — Part 2: AudioDB Enrichment + Pipeline Upgrades

## Chapter 8: AudioDB Client
- [x] Task 1: Create `src/audiodb.py` — HTTP client with two functions: `lookup_by_mbid(mbid)` calling `track-mb.php` and `lookup_by_text(artist, title)` calling `searchtrack.php`
- [x] Task 2: Add null-safe field extraction — all AudioDB fields return as strings or None; cast `intScore` to float, `intDuration` to int, guard every `.get()` with a fallback
- [x] Task 3: Handle `strLocked == "Locked"` — flag the track as unenriched rather than crashing
- [x] Task 4: Add rate-limit handling — catch HTTP 429, wait 2s, retry once, then skip enrichment for that track

## Chapter 9: Enrichment Step (MusicBrainz + AudioDB Bridge)
- [x] Task 1: After MusicBrainz retrieval, loop over candidates and call `lookup_by_mbid` for each using the MBID already in the result
- [x] Task 2: If MBID lookup returns nothing, fall back to `lookup_by_text(artist, title)`
- [x] Task 3: Attach AudioDB fields to each `CandidateSong`: `mood`, `genre`, `style`, `theme`, `community_score`, `youtube_url`, `thumb_url`
- [x] Task 4: Log enrichment rate per run (e.g. "18/25 candidates enriched")

## Chapter 10: Scoring Engine Upgrade
- [ ] Task 1: Add mood match score — compare `CandidateSong.mood` (AudioDB `strMood`) to `MoodProfile.mood`; exact match = +20, fuzzy/synonym match = +10
- [ ] Task 2: Add genre match score — compare `strGenre` + `strStyle` to `MoodProfile.genre`; replace the old tag-overlap approximation
- [ ] Task 3: Add popularity weight — scale `intScore` (0–10) and `intTotalListeners` into a small bonus (0–10 pts) so obscure tracks don't tie with established ones
- [ ] Task 4: Update the score breakdown display in the UI to show which fields contributed (mood match, genre match, popularity, keyword overlap)

## Chapter 11: Rich Recommendation Cards
- [ ] Task 1: Show `strTrackThumb` as a small album art image on each recommendation card (fallback: placeholder if null)
- [ ] Task 2: Show `strMusicVid` as a "Watch on YouTube" link if present
- [ ] Task 3: Show `strTheme` as a small tag badge on the card (e.g. "Theme: In Love") if present

## Chapter 12: Fallback Chain + Reliability
- [ ] Task 1: If MusicBrainz + enrichment yields fewer than 5 scored candidates, call `mostloved.php?format=track`, filter results by mood match against `MoodProfile.mood`, and pad the candidate list
- [ ] Task 2: If track-level AudioDB enrichment fails (locked or missing), fall back to artist-level `search.php` to get `strGenre` and `strMood` at the artist level
- [ ] Task 3: Log which fallback path fired so failures are traceable

## Chapter 13: Theme-Aware LLM Explainer
- [ ] Task 1: Pass each song's `strTheme` into the explainer prompt alongside the existing ranked results
- [ ] Task 2: Update the explainer system prompt to instruct the LLM to reference emotional themes when present — connecting the song's theme to what the user described
