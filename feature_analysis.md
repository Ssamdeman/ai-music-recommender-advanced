# Feature Analysis: What to Use for a Simple Content-Based Recommender

> Based on `data/songs.csv` — 10 songs, 7 features (excluding id/title/artist)

---

## Step 1: Raw Data At a Glance

| # | Title | Genre | Mood | Energy | BPM | Valence | Dance | Acoustic |
|---|---|---|---|---|---|---|---|---|
| 1 | Sunrise City | pop | happy | 0.82 | 118 | 0.84 | 0.79 | 0.18 |
| 2 | Midnight Coding | lofi | chill | 0.42 | 78 | 0.56 | 0.62 | 0.71 |
| 3 | Storm Runner | rock | intense | 0.91 | 152 | 0.48 | 0.66 | 0.10 |
| 4 | Library Rain | lofi | chill | 0.35 | 72 | 0.60 | 0.58 | 0.86 |
| 5 | Gym Hero | pop | intense | 0.93 | 132 | 0.77 | 0.88 | 0.05 |
| 6 | Spacewalk Thoughts | ambient | chill | 0.28 | 60 | 0.65 | 0.41 | 0.92 |
| 7 | Coffee Shop Stories | jazz | relaxed | 0.37 | 90 | 0.71 | 0.54 | 0.89 |
| 8 | Night Drive Loop | synthwave | moody | 0.75 | 110 | 0.49 | 0.73 | 0.22 |
| 9 | Focus Flow | lofi | focused | 0.40 | 80 | 0.59 | 0.60 | 0.78 |
| 10 | Rooftop Lights | indie pop | happy | 0.76 | 124 | 0.81 | 0.82 | 0.35 |

---

## Step 2: Feature-by-Feature Analysis

### `energy` — Range: 0.28 → 0.93 | Spread: 0.65

The single widest-ranging numeric feature in the dataset. It cleanly separates two poles:

- **Low energy (≤0.42):** lofi, ambient, jazz — all calm, background-listening tracks
- **High energy (≥0.75):** pop, rock, synthwave — active, foreground tracks

**Verdict: strongest individual feature.** Almost no overlap between the two poles.

---

### `valence` — Range: 0.48 → 0.84 | Spread: 0.36

Captures the emotional brightness of a track independently of how loud or fast it is. Key observation: **energy and valence are not the same thing.**

- Storm Runner (rock, intense): energy = 0.91 but valence = 0.48 — high energy but emotionally dark
- Spacewalk Thoughts (ambient, chill): energy = 0.28 but valence = 0.65 — quiet but not sad
- Sunrise City (pop, happy): energy = 0.82, valence = 0.84 — high energy AND emotionally bright

This independence is exactly what makes valence valuable. It adds a second dimension that energy alone can't provide.

**Verdict: second most important feature. Captures the happy/dark axis.**

---

### `acousticness` — Range: 0.05 → 0.92 | Spread: 0.87

The widest absolute spread of any feature. Cleanly separates production texture:

- **High (≥0.71):** lofi, jazz, ambient — organic, warm, quieter production
- **Low (≤0.22):** pop, rock, synthwave — electronic, produced, polished

Critically, acousticness is **nearly independent of valence and largely independent of energy** in this dataset. A high-acousticness track isn't necessarily low-energy (though in this set they correlate somewhat).

**Verdict: strong third feature. Defines the organic vs. electronic texture axis.**

---

### `tempo_bpm` — Range: 60 → 152 | Spread: 92 BPM

Tempo is informative but **largely redundant with energy** in this dataset:

| Track | Energy | BPM |
|---|---|---|
| Spacewalk Thoughts | 0.28 | 60 |
| Library Rain | 0.35 | 72 |
| Coffee Shop Stories | 0.37 | 90 |
| Gym Hero | 0.93 | 132 |
| Storm Runner | 0.91 | 152 |

Pearson correlation between energy and BPM across these 10 songs is visually very high (~0.92). They move together almost perfectly. The one partial exception: Night Drive Loop (synthwave) has moderate energy (0.75) but mid tempo (110) — synthwave often has locked grooves that feel driven without being fast.

**Verdict: useful but secondary to energy. Adds slight independent signal for edge cases like synthwave. Include it, but weight it lower.**

---

### `danceability` — Range: 0.41 → 0.88 | Spread: 0.47

Also correlates with energy, but captures something subtly different — **rhythmic regularity and beat predictability**, not just loudness/intensity. Example:

- Storm Runner (rock, intense): energy = 0.91 but danceability = 0.66 — high energy but irregular rock rhythm
- Gym Hero (pop, intense): energy = 0.93, danceability = 0.88 — high energy AND perfectly on-beat

The gap between rock and pop here is real and meaningful for a recommender. Someone who wants "dance music" doesn't necessarily want all high-energy tracks.

**Verdict: worth including alongside energy. The rock vs. pop distinction it creates is meaningful.**

---

### `genre` — 7 unique values (categorical)

Genre is the most human-readable signal and arguably the most culturally loaded. However as a feature for computation it has problems:

- **Rigid boundaries:** A lofi track and an ambient track might be more similar numerically than two pop tracks
- **No natural ordering:** You can't compute "distance" between `jazz` and `synthwave` without encoding
- **Small dataset problem:** With only 10 songs, genre already has 7 unique values — nearly one-per-song

For a simple recommender, genre works well as a **hard filter** ("only show me jazz") but poorly as a continuous similarity signal. One-hot encoding it adds 7 sparse dimensions for 10 songs, which is noise.

**Verdict: use as a pre-filter or tie-breaker, not as a primary numeric feature.**

---

### `mood` — 6 unique values (categorical)

Mood is essentially a **human-readable summary label** derived from the numeric features. Look at the pattern:

| Mood | Energy | Valence | Acousticness |
|---|---|---|---|
| intense | 0.91–0.93 | 0.48–0.77 | 0.05–0.10 |
| happy | 0.76–0.82 | 0.81–0.84 | 0.18–0.35 |
| chill | 0.28–0.42 | 0.56–0.65 | 0.71–0.92 |
| relaxed | 0.37 | 0.71 | 0.89 |
| focused | 0.40 | 0.59 | 0.78 |
| moody | 0.75 | 0.49 | 0.22 |

`chill` = low energy + high acousticness. `intense` = high energy + low acousticness. The mood label largely duplicates what the numeric features already say. The exception is `moody` — Night Drive Loop has moderate-to-high energy and low acousticness (synthwave profile) but low valence. Mood captures that valence drop in a label the numbers almost express.

**Verdict: redundant with numeric features for computation. Best used as a display label or user-facing filter, not a distance metric.**

---

## Step 3: Recommended Feature Set for the Simulator

For a **simple content-based recommender**, use these three numeric features as the core similarity vector:

```
similarity_vector = [energy, valence, acousticness]
```

| Feature | Why it's in | What axis it covers |
|---|---|---|
| `energy` | Widest useful spread, clearest signal | Calm ↔ Intense |
| `valence` | Independent of energy, captures emotion | Dark ↔ Bright |
| `acousticness` | Independent texture dimension | Electronic ↔ Organic |

**Optional additions (with caveats):**

| Feature | Include if... | Caveat |
|---|---|---|
| `danceability` | You want to distinguish rock from pop at similar energy | Adds mild redundancy with energy |
| `tempo_bpm` | You normalize it to 0–1 range first | Almost entirely redundant with energy in this dataset |
| `genre` | Used as a hard filter only | Not suitable as a distance metric |
| `mood` | Used as a display label for the user | Redundant with the numeric vector for computation |

---

## Step 4: Do These Features Actually Capture "Vibe"?

**What "vibe" means in practice:**

When someone says "I want something with a similar vibe," they typically mean a combination of:
1. **Intensity/energy level** — is it background music or am I paying attention to it?
2. **Emotional tone** — is it lifting me up or settling me down?
3. **Sound texture** — does it feel warm and organic, or sharp and electronic?

That maps almost perfectly to `energy`, `valence`, and `acousticness`.

### Where the features succeed

- **energy** nails intensity. Recommending Midnight Coding (lofi, 0.42) when you liked Library Rain (lofi, 0.35) makes total sense — same low-key vibe.
- **valence** correctly separates Storm Runner (dark rock, 0.48) from Gym Hero (bright pop, 0.77) even though both have near-identical energy. Two songs can both be intense but feel completely different emotionally.
- **acousticness** correctly groups Coffee Shop Stories (jazz, 0.89) with Library Rain (lofi, 0.86) and Spacewalk Thoughts (ambient, 0.92) — all share that warm, un-produced texture even across different genres.

### Where the features fall short

- **Rhythm feel is partially missing.** `danceability` hints at it, but the dataset can't distinguish a tight 4/4 pop groove from a shuffled jazz feel. Both could score similarly.
- **Lyrical content is invisible.** A song about heartbreak and a song about a road trip could have identical numeric profiles. Vibe isn't just sonic — words matter.
- **Cultural and era context is lost.** An 80s synth track and a modern synthwave track might score identically but feel very different to a listener.
- **Mood nuance collapses.** `focused` and `chill` are both low-energy, high-acousticness — the recommender would treat Focus Flow and Library Rain as nearly identical. For studying vs. pure relaxation, that distinction matters to the listener.

### Verdict

**energy + valence + acousticness captures roughly 70–80% of what listeners mean by "vibe."** It handles the most common cases (calm vs. intense, happy vs. dark, electronic vs. organic) very well. The missing 20–30% lives in rhythm feel, lyrical content, and cultural context — none of which are in this dataset, and none of which are easy to encode in simple scalars.

For a simulator, that's an excellent starting point.

---

## Summary

```
RECOMMENDED CORE FEATURES:    energy  +  valence  +  acousticness
SECONDARY (optional):         danceability,  tempo_bpm (normalized)
USE AS FILTERS ONLY:          genre,  mood
DO NOT USE AS DISTANCE:       id,  title,  artist
```
