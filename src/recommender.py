from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to float/int."""
    import csv
    songs = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                'id': int(row['id']),
                'title': row['title'],
                'artist': row['artist'],
                'genre': row['genre'],
                'mood': row['mood'],
                'energy': float(row['energy']),
                'tempo_bpm': float(row['tempo_bpm']),
                'valence': float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness']),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song 0–100 using weighted proximity on energy/valence/acousticness plus genre (+12) and mood (+8) bonuses."""
    reasons: List[str] = []

    # --- Numeric tier ---
    # Energy: proximity × 64 pts (max) — EXPERIMENT: doubled from 32
    energy_diff = abs(song['energy'] - user_prefs['target_energy'])
    energy_pts = (1 - energy_diff) * 64
    reasons.append(f"energy proximity {song['energy']:.2f} vs {user_prefs['target_energy']:.2f} (+{energy_pts:.1f})")

    # Valence: proximity × 28 pts (max)
    valence_diff = abs(song['valence'] - user_prefs['target_valence'])
    valence_pts = (1 - valence_diff) * 28
    reasons.append(f"valence proximity {song['valence']:.2f} vs {user_prefs['target_valence']:.2f} (+{valence_pts:.1f})")

    # Acousticness: proximity × 20 pts (max)
    # likes_acoustic=True → target 1.0, False → target 0.0
    acoustic_target = 1.0 if user_prefs['likes_acoustic'] else 0.0
    acoustic_diff = abs(song['acousticness'] - acoustic_target)
    acoustic_pts = (1 - acoustic_diff) * 20
    reasons.append(f"acousticness proximity {song['acousticness']:.2f} vs {acoustic_target:.1f} (+{acoustic_pts:.1f})")

    numeric_score = energy_pts + valence_pts + acoustic_pts

    # --- Categorical tier ---
    genre_bonus = 0.0
    if song['genre'] == user_prefs['genre']:
        genre_bonus = 6.0  # EXPERIMENT: halved from 12
        reasons.append("genre match (+6.0)")

    mood_bonus = 0.0
    if song['mood'] == user_prefs['mood']:
        mood_bonus = 8.0
        reasons.append("mood match (+8.0)")

    final_score = min(100.0, numeric_score + genre_bonus + mood_bonus)
    return final_score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, filter below threshold, apply diversity rule, and return the top-k ranked recommendations."""
    THRESHOLD = 40
    acoustic_target = 1.0 if user_prefs['likes_acoustic'] else 0.0

    # Score every song and collect (song, score, reasons) triples
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]

    # Drop songs below the quality threshold
    eligible = [(song, score, reasons) for song, score, reasons in scored if score >= THRESHOLD]

    # Sort descending by score; tie-break by smallest acousticness delta
    eligible.sort(
        key=lambda t: (t[1], -abs(t[0]['acousticness'] - acoustic_target)),
        reverse=True
    )

    # Diversity rule: if top 2 share both genre AND mood, force a different 3rd pick
    if len(eligible) >= 3:
        top0, top1 = eligible[0][0], eligible[1][0]
        if top0['genre'] == top1['genre'] and top0['mood'] == top1['mood']:
            diversity_pick = next(
                (item for item in eligible[2:] if
                 item[0]['genre'] != top0['genre'] or item[0]['mood'] != top0['mood']),
                None
            )
            if diversity_pick:
                rest = [item for item in eligible[2:] if item is not diversity_pick]
                eligible = [eligible[0], eligible[1], diversity_pick] + rest

    # Build final output: (song_dict, score, explanation_string)
    return [
        (song, score, ", ".join(reasons))
        for song, score, reasons in eligible[:k]
    ]
