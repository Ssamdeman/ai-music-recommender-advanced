# Reflection: Profile Comparison Notes

## High-Energy Pop vs. Chill Lofi

These two profiles produced almost completely opposite results, which makes sense because they are testing opposite ends of the energy scale. The High-Energy Pop profile pulled in fast, loud, produced tracks (pop, EDM, hip-hop) while Chill Lofi surfaced slow, quiet, acoustic-heavy songs (lofi, classical, ambient). The genre bonus helped keep lofi songs at the top of the Chill list even when a classical track had a slightly better energy score. This comparison shows that the energy and acousticness dimensions are working correctly as anchors — they steer the output toward the right sonic territory even when genre labels differ.

---

## Chill Lofi vs. Deep Intense Rock

Both profiles are "mood-coherent" — the user's mood and energy preferences point in the same direction — and both returned results that felt intuitively right. Chill Lofi got quiet, introspective tracks; Deep Intense Rock got heavy, aggressive ones. The interesting difference is that the Rock profile's #1 result was a metal song (Iron and Ash), not a rock song, because the metal track's energy and valence were a closer numeric match. This shows the genre bonus (+12 pts) is sometimes not strong enough to beat a tight numeric fit from a different genre, especially when the genres are closely related in sound.

---

## High-Energy Pop vs. Conflicting Energy+Sad

This is the most revealing comparison. Both profiles have the same target energy (0.90), but the Sad profile sets valence to 0.15 instead of 0.88. The results shifted dramatically: the top song for the Sad profile was Iron and Ash (metal/angry) instead of Sunrise City (pop/happy). The same energy target pulled in a completely different genre because the low valence target aligned with a metal track rather than a pop one. This shows the system can be "tricked" — a user asking for sad pop gets metal because the scorer only checks if the numbers are close, not whether the combination of features actually makes sense together.

---

## Deep Intense Rock vs. Conflicting Energy+Sad

Both profiles want high energy and low valence, so their top results overlapped significantly (Iron and Ash and Storm Runner appeared in both). The key difference is the genre and mood preferences: Rock asked for "rock/angry" and got genre and mood bonuses on top; the Conflicting profile asked for "pop/sad" and got zero mood or genre matches in the top 5. This shows that when genre and mood bonuses are absent and numeric scores are close, the two profiles become almost indistinguishable to the scorer — they collapse into the same set of songs.

---

## All-Neutral vs. Acoustic but Intense

Both profiles failed to return results that matched the intended listener, but for different reasons. The All-Neutral profile had no strong preferences, so the output was almost arbitrary — whichever song happened to be closest to 0.5 on energy won. The Acoustic but Intense profile had very strong but contradictory preferences — high energy pulls toward electronic/loud tracks, while `likes_acoustic=True` pulls toward quiet guitar-based songs. The two forces canceled each other out and the top results were neither acoustic nor classical, just songs that scored mediocre on both dimensions. This comparison shows that the scorer cannot resolve contradictions; it just averages them out.
