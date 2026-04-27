# TheAudioDB API — Developer Reference

Source: https://www.theaudiodb.com/free_music_api

---

## Why This API Matters for Moodwave

MusicBrainz returns track titles, artists, and duration — but no mood, no genre, no style.
TheAudioDB fills that gap: every track response includes `strMood`, `strGenre`, `strStyle`,
and `strTheme` — exactly the fields our scoring engine needs to match against a `MoodProfile`.

The two APIs are designed to work together. TheAudioDB includes `strMusicBrainzID` on every
artist, album, and track, so you can look up a song in MusicBrainz and enrich it via AudioDB
using the same MBID.

---

## Base URL (Free Tier)

```
https://www.theaudiodb.com/api/v1/json/2/
```

Free API key is `2`. Append it to the path, not a header.

> **Note on key `123`:** Older documentation refers to key `123`. Key `2` is the current
> working free key. Both are unauthenticated and rate-limited.

---

## Rate Limits

| Tier     | Limit          | 429 Behavior                |
|----------|----------------|-----------------------------|
| Free     | 30 req / min   | HTTP 429; retry after 1 min |
| Premium  | 100 req / min  | HTTP 429; retry after 1 min |
| Business | 120 req / min  | HTTP 429; retry after 1 min |

For Moodwave: **one lookup per track is fine** — we only call after retrieval, not in a loop.

---

## Endpoints We Care About

### 1. Search track by artist + track name

```
GET /searchtrack.php?s={artist}&t={track}
```

Best entry point for enriching a MusicBrainz result. Pass the artist and title you already have.

**Example:**
```
https://www.theaudiodb.com/api/v1/json/2/searchtrack.php?s=Coldplay&t=Yellow
```

**Returns:** Array under `track` key. Each object has the full track field set (see below).

---

### 2. Lookup track by MusicBrainz recording ID

```
GET /track-mb.php?i={mbid}
```

Use this when you already have the MBID from a MusicBrainz search — no text matching needed,
no ambiguity.

**Example:**
```
https://www.theaudiodb.com/api/v1/json/2/track-mb.php?i=729cf505-94eb-4fbe-bc76-cbae44cff091
```

**Returns:** Same track object as above.

---

### 3. Search artist

```
GET /search.php?s={artist}
```

Returns full artist profile including genre, mood, and style at the artist level.
Useful if you want genre/mood as a fallback when track-level data is missing.

**Example:**
```
https://www.theaudiodb.com/api/v1/json/2/search.php?s=Coldplay
```

---

### 4. Top 10 tracks for an artist

```
GET /track-top10.php?s={artist}
```

Returns the 10 most popular tracks with full metadata. Useful for seeding candidates
when MusicBrainz returns few results for a niche artist.

---

### 5. Most loved tracks (global)

```
GET /mostloved.php?format=track
```

Returns a curated global list of well-loved tracks with full metadata including mood.
Could be used as a fallback catalog when retrieval fails or returns nothing useful.

---

## Track Response Fields

Real response from `searchtrack.php` (Coldplay — Yellow):

```json
{
  "idTrack":              "32724184",
  "idAlbum":              "2109615",
  "idArtist":             "111239",
  "strTrack":             "Yellow",
  "strAlbum":             "Parachutes",
  "strArtist":            "Coldplay",
  "strArtistAlternate":   null,
  "intCD":                null,
  "intDuration":          "269240",

  "strGenre":             "Pop-Rock",
  "strMood":              "Relaxed",
  "strStyle":             "Rock/Pop",
  "strTheme":             "In Love",

  "strDescriptionEN":     "Yellow is a song by British alternative rock...",

  "strTrackThumb":        "https://r2.theaudiodb.com/images/media/track/thumb/...",
  "strMusicVid":          "https://www.youtube.com/watch?v=yKNxeF4KMsY",
  "strMusicVidDirector":  "James & Alex",

  "intMusicVidViews":     "409342773",
  "intMusicVidLikes":     "1585376",
  "intScore":             "9.30769",
  "intScoreVotes":        "13",
  "intTotalListeners":    "3383015",
  "intTotalPlays":        "36281471",

  "strMusicBrainzID":         "729cf505-94eb-4fbe-bc76-cbae44cff091",
  "strMusicBrainzAlbumID":    "1dc4c347-a1db-32aa-b14f-bc9cc507b843",
  "strMusicBrainzArtistID":   "cc197bad-dc9c-440d-a5b5-d52ba2e14234",

  "strLocked":            "Unlocked"
}
```

### Fields relevant to Moodwave scoring

| Field               | Type   | Notes                                                                    |
|---------------------|--------|--------------------------------------------------------------------------|
| `strMood`           | string | e.g. `"Relaxed"`, `"Happy"`, `"Melancholic"` — direct match to `MoodProfile.mood` |
| `strGenre`          | string | e.g. `"Pop-Rock"`, `"Alternative Rock"` — compare to `MoodProfile.genre` |
| `strStyle`          | string | e.g. `"Rock/Pop"` — secondary genre signal, useful when `strGenre` is missing |
| `strTheme`          | string | e.g. `"In Love"`, `"Loss"` — lyrical/emotional context                  |
| `intDuration`       | string | milliseconds as string — same unit as MusicBrainz                        |
| `intScore`          | string | Community rating 0–10; higher = more established track                   |
| `intTotalListeners` | string | Popularity proxy — avoids recommending obscure tracks                    |
| `strDescriptionEN`  | string | Full text description — could be passed to LLM explainer                 |
| `strMusicVid`       | string | YouTube URL — linkable in the UI if present                              |
| `strTrackThumb`     | string | Cover art image URL for UI display                                       |

### Fields NOT present (notable absences)

- **BPM / Tempo** — not in the API. Tempo is inferred from `strMood`/`strStyle` only.
- **Valence / Energy** — no numeric audio features (unlike Spotify). These must still come from the `MoodProfile`.
- **Lyrics** — `strTrackLyrics` exists in the schema but is empty in practice on the free tier.

---

## Artist Response Fields (relevant subset)

Returned by `search.php?s={artist}`:

| Field              | Example value         | Use in Moodwave                        |
|--------------------|-----------------------|----------------------------------------|
| `strGenre`         | `"Alternative Rock"`  | Fallback genre if track has none       |
| `strMood`          | `"Happy"`             | Fallback mood at artist level          |
| `strStyle`         | `"Rock/Pop"`          | Fallback style                         |
| `strCountry`       | `"London, England"`   | Could filter by region if needed       |
| `strMusicBrainzID` | `"cc197bad-..."`      | Bridge to MusicBrainz for cross-lookup |
| `strBiography`     | (long text)           | Could enrich LLM explainer context     |

---

## Integration Strategy for Moodwave

### Option A — Enrich after MusicBrainz retrieval (recommended)

```
MusicBrainz search → candidate list (title, artist, mbid, duration)
     |
     v
For each candidate: AudioDB track-mb.php?i={mbid}
     |
     v
Add strMood, strGenre, strStyle, strTheme, intScore to CandidateSong
     |
     v
Scorer now has richer fields → better ranking
```

**Tradeoff:** One extra HTTP request per candidate (up to 25). At free-tier rate limit
(30 req/min) this is fine for 25 candidates. Add a short delay if hitting 429s.

### Option B — Use AudioDB as primary search, skip MusicBrainz

```
AudioDB searchtrack.php?s={keyword}&t={keyword}
     |
     v
Returns title, artist, mood, genre, style, duration in one call
     |
     v
No enrichment step needed
```

**Tradeoff:** Keyword search is less flexible than MusicBrainz full-text. Results may be
narrower for niche genres. Best used as a complement to Option A, not a replacement.

### Option C — AudioDB mostloved as warm fallback

If MusicBrainz returns fewer than 5 candidates, pull from `mostloved.php?format=track`,
filter by matching mood, and pad the candidate list. No MBID lookup required.

---

## Data Type Quirk

All fields come back as **strings**, even numeric ones (`intDuration`, `intScore`, etc.).
Cast before arithmetic:

```python
duration_ms = int(track.get("intDuration") or 0)
score       = float(track.get("intScore") or 0)
```

Null fields return JSON `null`, which Python deserializes as `None`.
Always use `.get("field") or default` rather than bare key access.

---

## Image URLs

Thumbnails support size suffixes:

```
{base_url}           ->  720px original
{base_url}/medium    ->  500px
{base_url}/small     ->  250px
```

---

## Known Limitations

- Some tracks return `null` for `strMood` — always handle gracefully with a fallback.
- `strLocked: "Locked"` means the track has restricted metadata on the free tier; core fields
  (title, artist, MBID) still return but mood/genre may be null.
- No BPM, no valence, no energy — numeric audio features require Spotify or AcousticBrainz.
- Free tier search endpoints (searchtrack, search) rate-limit more aggressively than lookup
  endpoints (track-mb). Prefer MBID-based lookups after the initial MusicBrainz retrieval.
