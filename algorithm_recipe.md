# Algorithm Recipe: Music Recommender Scoring System

> Built from `feature_analysis.md` and `data/songs.csv`
> Last updated: redesigned scoring to explicit per-feature proximity math + revised categorical bonus weights.

---

## Core Idea in One Sentence

Given a **seed song** the user liked, score every other song by how close it is
in "vibe space" — rewarding proximity on each numeric feature — then add bonuses
for matching genre or mood.

---

## Why Two Rules? Scoring vs. Ranking

A recommendation system needs **both** a Scoring Rule and a Ranking Rule.
They solve different problems and neither can do the other's job.

```
SCORING RULE                          RANKING RULE
─────────────────────────────         ──────────────────────────────────
Sees: one candidate at a time         Sees: all scores at once
Asks: "how good is this song?"        Asks: "what do we actually show?"
Output: a single number (0–100)       Output: a final ordered short list
Knows about: seed + candidate         Knows about: every score, thresholds,
                                                    diversity, duplicates
```

### Why you need the Scoring Rule

Without a scoring rule you have no basis for comparison at all.
It is the math that turns raw song attributes into a preference signal.
Every candidate goes through it independently — it has no idea what
other songs scored, and it does not need to.

### Why the Scoring Rule alone is not enough

Imagine the scoring rule gives these results for a lofi seed song:

```
Library Rain        → 76
Spacewalk Thoughts  → 75
Focus Flow          → 73
Midnight Coding     → 71
...
```

If you just take the top 3, you get three nearly-identical quiet acoustic tracks.
Technically correct — all high scores — but poor UX. A real recommendation list
needs some breadth.

More critically, the scoring rule cannot answer questions like:
- "Is 40/100 good enough to even show to the user?"
- "If two songs tie at 71, which one goes first?"
- "Should we break up a cluster of same-genre results?"

Those are **list-level decisions**. That is the Ranking Rule's job.

### The analogy

> **Scoring Rule** = the interview rubric (evaluate each candidate individually)
> **Ranking Rule** = the hiring committee (given all the scores, who do we actually hire,
>                   and do we want two people from the same team?)

You need both. A great rubric with a bad committee still makes bad hires.

---

## The Scoring Budget

The total possible score is **100 points**, split into two tiers:

```
┌─────────────────────────────────────────────┐
│  NUMERIC TIER          0 – 80 pts           │
│  (how close the vibe is)                    │
│    energy component     up to 32 pts        │
│    valence component    up to 28 pts        │
│    acousticness comp.   up to 20 pts        │
├─────────────────────────────────────────────┤
│  CATEGORICAL TIER      0 – 20 pts           │
│  (does it belong to the same style?)        │
│    genre match          up to 12 pts        │
│    mood match           up to  8 pts        │
└─────────────────────────────────────────────┘
```

The split is intentional: **numeric vibe carries 80% of the weight**.
Categorical labels refine the ranking among numerically close songs —
they do not rescue a bad numeric match.

---

## Step 1: The Feature Vector

Each song is represented as three independent axes:

```
song_vector = [energy, valence, acousticness]
```

All values are already on a 0–1 scale in `songs.csv` — no normalization needed.

| Axis | Encodes | Low end | High end |
|---|---|---|---|
| `energy` | Intensity level | Spacewalk Thoughts (0.28) | Gym Hero (0.93) |
| `valence` | Emotional tone | Storm Runner (0.48) | Sunrise City (0.84) |
| `acousticness` | Production texture | Gym Hero (0.05) | Spacewalk Thoughts (0.92) |

---

## Step 2: Per-Feature Proximity Score

**The key principle:** we are not rewarding "high energy" or "low energy" —
we are rewarding *closeness to the seed song's energy*.

For each numeric feature, compute a **proximity score from 0.0 to 1.0**:

```
proximity(seed_val, candidate_val) = 1 - | seed_val - candidate_val |
```

### Why linear proximity?

| Scoring shape | Formula | Behavior |
|---|---|---|
| Linear (chosen) | `1 - \|Δ\|` | Every unit of difference costs the same — transparent and predictable |
| Squared | `1 - Δ²` | Forgives small gaps too much; 0.3 difference still scores 0.91 |
| Gaussian | `exp(-Δ²/2σ²)` | More realistic but adds a σ parameter with no obvious default value |

Linear is chosen because the dataset is small and the goal is a **readable, debuggable**
simulator. Every 0.10 difference in energy costs exactly 10% of the energy score.

### Worked proximity examples (energy axis only)

Seed: `Coffee Shop Stories` — energy = 0.37

| Candidate | Candidate Energy | \|Δ\| | Proximity |
|---|---|---|---|
| Library Rain | 0.35 | 0.02 | **0.98** — nearly identical |
| Focus Flow | 0.40 | 0.03 | **0.97** — almost the same |
| Midnight Coding | 0.42 | 0.05 | **0.95** — very close |
| Night Drive Loop | 0.75 | 0.38 | **0.62** — noticeably more intense |
| Gym Hero | 0.93 | 0.56 | **0.44** — completely different intensity |

This is the core insight: the score is *relative to the seed*, not an absolute rating.

---

## Step 3: Weighted Numeric Score (0–80 pts)

Each proximity score is multiplied by its feature weight and by 80
(the numeric tier budget):

```
energy_pts      = proximity(seed.energy,       candidate.energy)       × 0.40 × 80
valence_pts     = proximity(seed.valence,       candidate.valence)      × 0.35 × 80
acousticness_pts = proximity(seed.acousticness, candidate.acousticness) × 0.25 × 80

numeric_score   = energy_pts + valence_pts + acousticness_pts    ─── range: 0 → 80
```

Expanded so the max per feature is visible:

```
energy_pts       = (1 - |ΔE|) × 32        ← max 32 pts
valence_pts      = (1 - |ΔV|) × 28        ← max 28 pts
acousticness_pts = (1 - |ΔA|) × 20        ← max 20 pts
                              ─────────────────────────
                              numeric_score  max 80 pts
```

### Why these weights? (40 / 35 / 25)

| Feature | Weight | Reasoning |
|---|---|---|
| `energy` | 40% | Widest spread in the dataset (0.28–0.93). A wrong energy match is the most jarring — listeners notice immediately when a song is far more intense or calm than expected. |
| `valence` | 35% | Emotionally independent of energy. Storm Runner and Gym Hero both have ~0.92 energy but valence 0.48 vs 0.77 — very different feels. Second-most impactful on listener mood. |
| `acousticness` | 25% | Important but listeners tolerate more variance here. A slightly more electronic track is less jarring than a much more intense one. |

---

## Step 4: Categorical Bonuses (0–20 pts)

After the numeric score, add flat bonuses for matching categorical labels:

```
genre_bonus = 12 if candidate.genre == seed.genre else 0
mood_bonus  =  8 if candidate.mood  == seed.mood  else 0

final_score = round(numeric_score + genre_bonus + mood_bonus)    ─── cap at 100
```

### Why genre bonus (12) > mood bonus (8)?

This is the key design question. The answer comes from checking what information
each label adds **on top of** the numeric features.

**Mood is largely already in the numbers:**

| Mood | Typical energy | Typical valence | What the numerics already say |
|---|---|---|---|
| chill | 0.28–0.42 | 0.56–0.65 | Low energy + moderate valence = *already* chill |
| intense | 0.91–0.93 | 0.48–0.77 | High energy + low acousticness = *already* intense |
| happy | 0.76–0.82 | 0.81–0.84 | High energy + high valence = *already* happy |
| relaxed | 0.37 | 0.71 | Low energy + decent valence = *already* relaxed |

If you match on energy + valence, you have already captured most of what the mood
label says. Adding a mood bonus at +8 gives it a modest acknowledgement while
recognizing it is largely redundant.

**Genre carries information the numbers cannot:**

| Genre | What numerics capture | What numerics miss |
|---|---|---|
| jazz | High acousticness, low energy | Swing rhythm, improvisation, specific instrumentation (upright bass, brushed drums) |
| synthwave | Moderate energy, low acousticness | 80s aesthetic, analog synth textures, nostalgia signal |
| rock | High energy, low acousticness | Electric guitar power chords, specific structural patterns, cultural context |
| lofi | Low energy, high acousticness | Vinyl crackle, intentional degradation, study/focus cultural use |

Genre encodes **rhythm feel, instrumentation, cultural context, and era** — none of which
live in energy/valence/acousticness. A genre match is genuinely new information worth more.
That is why genre gets +12 and mood gets +8.

> **Previous version had this reversed (mood +5, genre +3).** That was wrong — it underweighted
> the information genre adds beyond the numeric features. Corrected here.

### Bonus impact in context

To see how much the bonuses actually matter, consider two candidates both scoring 71 numeric points against a seed:
- Candidate A: same genre, different mood → 71 + 12 = **83**
- Candidate B: different genre, same mood → 71 + 8  = **79**
- Candidate C: same genre AND mood        → 71 + 20 = **91**
- Candidate D: neither match             → 71 + 0  = **71**

The genre match pushes A above B. But candidate C wins because both signals fire.
And candidate D, despite an identical numeric score, ranks last — correct behavior.

---

---
---

# THE RANKING RULE
# (list-level decisions — applied after all songs are scored)

---

## Step 5: Exclude the Seed Song

The seed scores 100 against itself (all Δ = 0, both bonuses fire). Always exclude it:

```
if candidate.id == seed.id:
    skip
```

---

## Step 6: Apply the Minimum Score Threshold

Scores below the threshold are too dissimilar to be useful recommendations.
Drop them before ranking so they never appear in results — even if the catalog
is small and they would otherwise fill spots.

```
THRESHOLD = 40

eligible = [song for song in candidates if final_score(song) >= THRESHOLD]
```

### Why 40?

Looking at the worked example for Coffee Shop Stories:

| Score | Song | Would you recommend it? |
|---|---|---|
| 76 | Library Rain | Yes — nearly identical vibe |
| 41 | Storm Runner | No — loud rock against quiet jazz is a jarring mismatch |
| 44 | Gym Hero | No — same problem |
| 48 | Sunrise City | Borderline |

A threshold of 40 removes the worst mismatches while keeping borderline candidates
eligible. In a larger catalog, raising it to 50–55 would make sense.

---

## Step 7: Apply the Diversity Rule

Sort the eligible pool by score descending. Before locking in the final 3,
check whether the top results are too similar to each other.

**The rule:** if the top 2 results share **both** the same genre **and** the same mood
as each other (not just the seed), the 3rd slot must go to the highest-scoring song
that breaks at least one of those two matches.

```
top_sorted = sorted(eligible, key=final_score, reverse=True)

if top_sorted[0].genre == top_sorted[1].genre
   and top_sorted[0].mood == top_sorted[1].mood:

    # find the highest scorer that differs in genre OR mood from top_sorted[0]
    diversity_pick = next(
        s for s in top_sorted[2:]
        if s.genre != top_sorted[0].genre or s.mood != top_sorted[0].mood
    )
    results = [top_sorted[0], top_sorted[1], diversity_pick]
else:
    results = top_sorted[:3]
```

### Why this matters

Without a diversity rule, a lofi-heavy catalog would always return 3 lofi tracks
for any lofi seed — the user hears nothing new. The diversity rule ensures at least
one result reaches outside the tightest cluster.

This is a simplified version of what Spotify calls **serendipity injection** —
deliberately introducing a non-obvious pick to prevent the filter bubble that
pure proximity scoring creates.

### When the diversity rule does NOT fire

- Top 2 share genre but different moods → no problem, rule does not activate
- Top 2 share mood but different genres → no problem, rule does not activate  
- Only 1 or 2 eligible songs total → return what exists, no 3rd slot to diversify

---

## Step 8: Tie-Breaking Rule

When two songs have identical `final_score`, break the tie by preferring
**lower acousticness delta** — i.e., the song whose production texture
is closer to the seed. Ties on the lowest-weight feature are the least
meaningful, so using it as a tiebreaker avoids arbitrary ordering without
introducing a new concept.

```
# applied during sort as a secondary key
sorted(eligible,
       key=lambda s: (final_score(s), -abs(seed.acousticness - s.acousticness)),
       reverse=True)
```

---

## Step 9: Return the Final List

```
return results[:3]   # top 3 after exclusion, threshold, diversity, tie-breaking
```

Default is top 3. The README asks for "3 to 5 songs" — this can be made configurable
as `N` with a default of 3.

---

### Ranking Rule Summary

```
STEP 5  Exclude the seed song (id match)
STEP 6  Drop scores below threshold (< 40)
STEP 7  Sort descending; apply diversity rule if top 2 share genre AND mood
STEP 8  Break ties by smallest acousticness delta
STEP 9  Return top 3
```

---

## Full Worked Example (New Formula)

**Seed:** `Coffee Shop Stories` — jazz · relaxed · energy=0.37 · valence=0.71 · acousticness=0.89

```
energy_pts      = (1 - |0.37 - x|) × 32
valence_pts     = (1 - |0.71 - x|) × 28
acousticness_pts = (1 - |0.89 - x|) × 20
```

| Candidate | E pts | V pts | A pts | Numeric | Genre +12 | Mood +8 | **Final** |
|---|---|---|---|---|---|---|---|
| Sunrise City | (1-0.45)×32=17.6 | (1-0.13)×28=24.4 | (1-0.71)×20=5.8 | 47.8 | — | — | **48** |
| Midnight Coding | (1-0.05)×32=30.4 | (1-0.15)×28=23.8 | (1-0.18)×20=16.4 | 70.6 | — | — | **71** |
| Storm Runner | (1-0.54)×32=14.7 | (1-0.23)×28=21.6 | (1-0.79)×20=4.2 | 40.5 | — | — | **41** |
| Library Rain | (1-0.02)×32=31.4 | (1-0.11)×28=24.9 | (1-0.03)×20=19.4 | 75.7 | — | — | **76** |
| Gym Hero | (1-0.56)×32=14.1 | (1-0.06)×28=26.3 | (1-0.84)×20=3.2 | 43.6 | — | — | **44** |
| Spacewalk Thoughts | (1-0.09)×32=29.1 | (1-0.06)×28=26.3 | (1-0.03)×20=19.4 | 74.8 | — | — | **75** |
| Focus Flow | (1-0.03)×32=31.0 | (1-0.12)×28=24.6 | (1-0.11)×20=17.8 | 73.4 | — | — | **73** |
| Night Drive Loop | (1-0.38)×32=19.8 | (1-0.22)×28=21.6 | (1-0.67)×20=6.6 | 48.0 | — | — | **48** |
| Rooftop Lights | (1-0.39)×32=19.5 | (1-0.10)×28=25.2 | (1-0.54)×20=9.2 | 53.9 | — | — | **54** |

**No genre or mood matches fire** — Coffee Shop Stories is the only jazz/relaxed track in the set.

**Top 3:** Library Rain (76) → Spacewalk Thoughts (75) → Focus Flow (73)

All three are quiet, warm, acoustic tracks. The ordering reflects that Library Rain is
*numerically tightest* across all three axes, not just one.

---

## Decision Log

| Decision | Chosen | Rejected | Reason |
|---|---|---|---|
| Per-feature scoring | Linear proximity `1 - \|Δ\|` | Squared, Gaussian | Most transparent; every 0.10 difference = 10% penalty |
| Score structure | 80 numeric + 20 categorical | 100 numeric only | Categorical labels carry real information; need a seat at the table |
| Numeric weights | 40 / 35 / 25 | Equal weights | Energy shifts felt most by listeners; acousticness shifts most tolerated |
| Genre vs mood bonus | Genre = 12, Mood = 8 | Mood > Genre (prior version) | Mood is largely redundant with numerics; genre adds rhythm/instrument/cultural info |
| Distance metric | Weighted Euclidean → linear proximity | Cosine similarity | Magnitude matters — "much calmer" ≠ "slightly calmer" |
| `tempo_bpm` in vector | Excluded | Included | ~92% correlated with energy in this dataset — noise, not signal |

---

## Summary: The Complete Recipe

> **Note (Step 3 finalization):** This recipe uses a **user taste profile** as the reference point,
> not a seed song. Every `Δ` below means `|song_value - user_prefs_target|`.
> The user_prefs structure (from Step 2):
> `{ "genre", "mood", "target_energy", "target_valence", "likes_acoustic" }`

### Simple Starting Point (Step 3 baseline)

```
score = 0

+2.0   if song.genre == user_prefs["genre"]          # genre match
+1.0   if song.mood  == user_prefs["mood"]           # mood match
+0–3.0 energy_pts = (1 - |song.energy - user_prefs["target_energy"]|) × 3.0
```

This baseline is enough to correctly rank "intense rock" above "chill lofi"
for a rock/intense profile. The full weighted recipe below adds precision.

---

### Full Weighted Recipe

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THE SCORING RULE  (run once per candidate song)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  REPRESENT   song_vector = [energy, valence, acousticness]
              reference   = [target_energy, target_valence, likes_acoustic→0/1]

  SCORE       energy_pts       = (1 - |ΔE|) × 32
              valence_pts      = (1 - |ΔV|) × 28
              acousticness_pts = (1 - |ΔA|) × 20
              numeric_score    = sum of above            (0–80)

  ADJUST      + 12 if song.genre == user_prefs["genre"]
              +  8 if song.mood  == user_prefs["mood"]
              cap final_score at 100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THE RANKING RULE  (run once, after all songs are scored)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  THRESHOLD   drop any song scoring < 40
  SORT        descending by final_score
  DIVERSITY   if top 2 share genre AND mood →
                force 3rd slot to first song that breaks either
  TIE-BREAK   equal scores → prefer smaller |ΔA| (acousticness)
  RETURN      top 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
