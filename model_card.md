# Model Card: Music Recommender Simulation

## 1. Model Name

> VibeMatch 1.0

---

## 2. Goal / Task

VibeMatch tries to suggest the top 5 songs from a small catalog that best fit a listener's personal taste. It takes in a user's preferred genre, mood, energy, valence, and acoustic preference, scores every song, and spits out the best matches to show how rule-based scoring actually works in practice.

---

## 3. Algorithm Summary

The system scores every song out of 100 by comparing its features to the user's preferences.

- **Features considered:** It looks at energy, valence (mood), and acousticness. The closer a song's numbers are to the user's ideal, the higher the score.
- **Weighting:** Energy carries the most weight, followed by valence and acousticness.
- **Bonuses & rules:** It adds flat bonus points if the genre or mood matches exactly. Any song scoring under 40 is thrown out, and the system forces a little variety if the top two results are too similar.

---

## 4. Data Used

- **Catalog size:** There are 18 songs in the dataset.
- **Features tracked:** We track genre, mood, energy, valence, and acousticness. (Tempo and danceability are in the data but ignored).
- **Diversity:** The data is heavily unbalanced. Lofi has three tracks, but most genres only have one. Completely missing genres like reggae or Latin means fans of those styles won't get good matches.

---

## 5. Strengths

- **Consistent Profiles:** It works really well for users with clear, aligned tastes. A high-energy pop fan gets exactly that at the #1 spot because the scoring dimensions reinforce each other.
- **Transparency:** The system shows its math, explaining exactly which features contributed to a song's score.
- **Variety:** The built-in diversity rule successfully stops the top results from being a wall of the exact same genre and mood.

---

## 6. Observed Behavior / Biases

- **Energy Dominance:** Because energy makes up 40% of the score, the system will sometimes push completely mismatched genres (like heavy metal for a "sad pop" fan) just because the energy numbers line up.
- **Genre Skew & Strictness:** With only 18 songs, niche fans are out of luck. Also, genre matching is completely unforgiving—if you want "pop" and the song is "indie pop," you get zero bonus points.
- **Binary Choices:** The "likes acoustic" preference is a simple yes/no, which penalizes users who might just want a _little_ bit of acoustic sound.

---

## 7. Evaluation Process

I tested six different user profiles ranging from standard (Chill Lofi) to weird edge cases (Conflicting Energy+Sad).

- **Results:** Standard profiles worked as expected. The edge cases revealed big flaws—like recommending angry metal to a sad pop fan because the math technically matched.
- **Testing Weights:** I also tried doubling the energy weight and halving the genre bonus. This broke the system entirely, causing a bunch of songs to hit a 100-point tie, proving energy was already too dominant.

---

## 8. Intended Use and Non-Intended Use

- **Intended use:** A classroom simulation built to explore how scoring rules and weights affect recommendations. It's meant to be read, tweaked, and tested.
- **Not intended for:** It is _not_ a production app for real music discovery like Spotify. The 18-song catalog is too small, and the math is too simple to serve real-world taste diversity.

---

## 9. Ideas for Improvement

If I had more time, I would:

- **Fix the Acoustic Flag:** Change the simple yes/no acoustic preference into a sliding scale so users can express nuanced tastes.
- **Expand the Dataset:** Add at least 5 songs per genre to give niche listeners real options and reduce weird cross-genre results.
- **Dynamic Weights:** Scale the genre bonus proportionally to the numeric weights so it doesn't get overpowered when tweaking the math.

---

## 10. Personal Reflection

- **What surprised me:** Seeing a heavy metal track rank #1 for a sad pop fan was a wake-up call. The math was perfectly correct, but the result was completely wrong. It showed me how an algorithm can be logically sound but practically useless if you don't think about what the numbers actually represent.
- **AI Assistance:** AI tools were great for planning and spotting biases I missed (like the acoustic cliff), but I still had to cross-check everything against my actual Python code to ensure it was truthful.
- **Takeaway:** It’s wild how a simple weighted math equation can feel like the system "understands" your taste when it works right. It definitely changes how I view the "magic" behind real apps like Spotify.
