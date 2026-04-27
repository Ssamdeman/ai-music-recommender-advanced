# MusicBrainz API — Developer Reference

Source: https://musicbrainz.org/doc/MusicBrainz_API

---

## Base URL
```
https://musicbrainz.org/ws/2/
```

## Response Format
Default is XML. Always add `fmt=json` to get JSON back.

---

## The Three Request Types

### 1. Search (what we use — no MBID needed)
```
GET /ws/2/<entity>?query=<LUCENE_QUERY>&fmt=json&limit=25&offset=0
```
Entity types: `recording`, `artist`, `release`, `release-group`, `label`, `work`, `tag`, etc.

### 2. Lookup (requires a known MBID)
```
GET /ws/2/<entity>/<mbid>?inc=<INC>&fmt=json
```

### 3. Browse (requires a linked MBID)
```
GET /ws/2/<result_entity>?<linked_entity>=<mbid>&fmt=json
```

---

## Recording Search — Fields We Use

| Field       | Description                              | Example                      |
|-------------|------------------------------------------|------------------------------|
| `tag`       | User-assigned tags (genre, mood, vibe)   | `tag:jazz`                   |
| `recording` | Song title                               | `recording:"blue in green"`  |
| `artist`    | Artist name                              | `artist:miles davis`         |
| `arid`      | Artist MBID                              | `arid:561d854a-...`           |
| `dur`       | Duration in milliseconds                 | `dur:240000`                 |
| `date`      | Release date                             | `date:1970`                  |
| `status`    | Release status                           | `status:official`            |

**No native mood/energy/valence fields.** Tags are the closest proxy.
Use `tag:melancholic`, `tag:late-night`, `tag:lo-fi`, etc.

---

## Lucene Query Syntax

```
# Simple tag search
tag:jazz

# AND — both must match
tag:jazz AND tag:melancholic

# OR — either matches (broader results)
tag:jazz OR tag:blues

# Phrase in title
recording:"we will rock you"

# Combine title + tag
recording:rain AND tag:ambient

# Boost a term (relevance scoring)
tag:jazz^2 OR tag:blues
```

---

## Key Request Parameters

| Parameter | Description                                  | Notes                          |
|-----------|----------------------------------------------|--------------------------------|
| `query`   | Lucene query string                          | Required for search            |
| `fmt`     | Response format: `json` or `xml`             | Always use `json`              |
| `limit`   | Results per page (default 25, max 100)       |                                |
| `offset`  | Pagination offset                            | For page 2: offset=25          |
| `inc`     | Include extra data (e.g. `tags`, `releases`) | Separate multiple with `+`     |

---

## Required Headers

```
User-Agent: YourApp/1.0 (contact@email.com)
Accept: application/json
```

**The User-Agent is mandatory.** Missing or generic User-Agent risks IP ban.

---

## Rate Limiting

- **Max 1 request per second** — this is a hard rule, not a guideline
- Exceeding this risks a temporary or permanent IP block
- Use `time.sleep(1)` between requests or track elapsed time

---

## Recording Response Shape (JSON)

```json
{
  "count": 1234,
  "offset": 0,
  "recordings": [
    {
      "id": "mbid-string",
      "title": "Song Title",
      "score": 87,
      "length": 245000,
      "artist-credit": [
        {
          "artist": { "id": "...", "name": "Artist Name" },
          "joinphrase": ""
        }
      ],
      "releases": [
        { "id": "...", "title": "Album Name", "date": "2001", "status": "Official" }
      ],
      "tags": [
        { "count": 5, "name": "jazz" },
        { "count": 3, "name": "melancholic" }
      ]
    }
  ]
}
```

- `score` → MusicBrainz relevance score (0–100). Higher = better match.
- `length` → duration in milliseconds. Divide by 1000 for seconds.
- `tags` → user-curated tags. These are our primary mood/genre signals.

---

## Our Query Strategy

Given a `MoodProfile` from the LLM interpreter:

```python
# Build tags from: genre + mood + search_keywords
tags = [profile.genre, profile.mood] + profile.search_keywords
query = " OR ".join(f"tag:{t.lower().replace(' ', '-')}" for t in tags[:5])
# Example: "tag:jazz OR tag:melancholic OR tag:late-night OR tag:rainy"
```

OR queries cast a wide net and let our scoring engine (Chapter 4) do the ranking.
AND queries are stricter but return fewer results — use for refinement.

---

## Pagination Pattern

```python
# Page 1
params = {"query": q, "fmt": "json", "limit": 25, "offset": 0}
# Page 2
params = {"query": q, "fmt": "json", "limit": 25, "offset": 25}
```

---

## Error Codes to Handle

| Code | Meaning                            | Action                    |
|------|------------------------------------|---------------------------|
| 400  | Bad query syntax                   | Log and return empty list |
| 503  | Server busy / rate limited         | Retry after 2s            |
| 404  | Entity not found                   | Return empty list         |
| 5xx  | Server error                       | Retry once, then fail     |

---

## Useful Links
- Full search fields: https://musicbrainz.org/doc/MusicBrainz_API/Search
- Lucene syntax: https://lucene.apache.org/core/4_3_0/queryparser/org/apache/lucene/queryparser/classic/package-summary.html
- Rate limit policy: https://musicbrainz.org/doc/MusicBrainz_API#Rate_Limiting
