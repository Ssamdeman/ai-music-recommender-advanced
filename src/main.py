"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


# ── User Profiles ────────────────────────────────────────────────────────────

PROFILES = {
    # Phase 1–3 baseline profile
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "target_energy": 0.90,
        "target_tempo_bpm": 128,
        "target_valence": 0.88,
        "likes_acoustic": False,
    },

    # Calm, mellow listener
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "calm",
        "target_energy": 0.25,
        "target_tempo_bpm": 75,
        "target_valence": 0.45,
        "likes_acoustic": True,
    },

    # Heavy, intense rock fan
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "angry",
        "target_energy": 0.95,
        "target_tempo_bpm": 160,
        "target_valence": 0.20,
        "likes_acoustic": False,
    },

    # ── Adversarial / Edge-Case Profiles ─────────────────────────────────────

    # Conflicting: high energy but sad mood — tests whether numeric score
    # can overpower a mood mismatch and surfaces "wrong vibe" songs.
    "Conflicting Energy+Sad": {
        "genre": "pop",
        "mood": "sad",
        "target_energy": 0.90,
        "target_tempo_bpm": 130,
        "target_valence": 0.15,   # sad → low valence
        "likes_acoustic": False,
    },

    # Middle-of-the-road: every numeric target is 0.5 — no strong signal,
    # reveals whether the scorer degenerates to arbitrary ordering.
    "All-Neutral (0.5 everything)": {
        "genre": "jazz",          # niche genre unlikely to match many songs
        "mood": "neutral",
        "target_energy": 0.50,
        "target_tempo_bpm": 100,
        "target_valence": 0.50,
        "likes_acoustic": False,
    },

    # Extreme mismatch: requests acoustic classical but with very high energy —
    # probes whether acoustic bonus can rescue a song the energy score penalises.
    "Acoustic but Intense": {
        "genre": "classical",
        "mood": "epic",
        "target_energy": 0.95,
        "target_tempo_bpm": 170,
        "target_valence": 0.70,
        "likes_acoustic": True,   # acoustic bonus pulls opposite direction to energy
    },
}


def print_recommendations(profile_name: str, user_prefs: dict, recommendations: list) -> None:
    print("\n" + "=" * 60)
    print(f"  Profile : {profile_name}")
    print(f"  Genre   : {user_prefs['genre']}  |  Mood: {user_prefs['mood']}")
    print(f"  Energy  : {user_prefs['target_energy']}  |  Valence: {user_prefs['target_valence']}"
          f"  |  Acoustic: {user_prefs['likes_acoustic']}")
    print("=" * 60)

    if not recommendations:
        print("  (no songs met the score threshold)")
    else:
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"\n  #{rank}  {song['title']}  —  {song['artist']}")
            print(f"      Genre: {song['genre']}  |  Mood: {song['mood']}")
            print(f"      Score: {score:.1f} / 100")
            for reason in explanation.split(", "):
                print(f"        • {reason}")

    print("=" * 60)


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile_name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(profile_name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
