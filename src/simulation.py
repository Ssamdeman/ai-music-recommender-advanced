"""
simulation.py

Full catalog of all 10 songs from data/songs.csv represented as Song objects,
plus example UserProfiles for testing the recommender.

Source: data/songs.csv
Features per song: id, title, artist, genre, mood,
                   energy, tempo_bpm, valence, danceability, acousticness
"""

from src.recommender import Song, UserProfile


# ---------------------------------------------------------------------------
# SONG CATALOG
# All 10 songs from data/songs.csv, loaded as Song dataclass instances.
# Feature ranges:
#   energy       0.0 – 1.0   (0.28 low -> 0.93 high in this catalog)
#   tempo_bpm    integer BPM (60 slow -> 152 fast in this catalog)
#   valence      0.0 – 1.0   (0.48 dark -> 0.84 bright in this catalog)
#   danceability 0.0 – 1.0   (0.41 low -> 0.88 high in this catalog)
#   acousticness 0.0 – 1.0   (0.05 electronic -> 0.92 organic in this catalog)
# ---------------------------------------------------------------------------

CATALOG: list[Song] = [

    # ── Pop ────────────────────────────────────────────────────────────────
    Song(
        id=1,
        title="Sunrise City",
        artist="Neon Echo",
        genre="pop",
        mood="happy",
        energy=0.82,
        tempo_bpm=118,
        valence=0.84,
        danceability=0.79,
        acousticness=0.18,
    ),

    # ── Lofi ───────────────────────────────────────────────────────────────
    Song(
        id=2,
        title="Midnight Coding",
        artist="LoRoom",
        genre="lofi",
        mood="chill",
        energy=0.42,
        tempo_bpm=78,
        valence=0.56,
        danceability=0.62,
        acousticness=0.71,
    ),

    # ── Rock ───────────────────────────────────────────────────────────────
    Song(
        id=3,
        title="Storm Runner",
        artist="Voltline",
        genre="rock",
        mood="intense",
        energy=0.91,
        tempo_bpm=152,
        valence=0.48,
        danceability=0.66,
        acousticness=0.10,
    ),

    # ── Lofi ───────────────────────────────────────────────────────────────
    Song(
        id=4,
        title="Library Rain",
        artist="Paper Lanterns",
        genre="lofi",
        mood="chill",
        energy=0.35,
        tempo_bpm=72,
        valence=0.60,
        danceability=0.58,
        acousticness=0.86,
    ),

    # ── Pop ────────────────────────────────────────────────────────────────
    Song(
        id=5,
        title="Gym Hero",
        artist="Max Pulse",
        genre="pop",
        mood="intense",
        energy=0.93,
        tempo_bpm=132,
        valence=0.77,
        danceability=0.88,
        acousticness=0.05,
    ),

    # ── Ambient ────────────────────────────────────────────────────────────
    Song(
        id=6,
        title="Spacewalk Thoughts",
        artist="Orbit Bloom",
        genre="ambient",
        mood="chill",
        energy=0.28,
        tempo_bpm=60,
        valence=0.65,
        danceability=0.41,
        acousticness=0.92,
    ),

    # ── Jazz ───────────────────────────────────────────────────────────────
    Song(
        id=7,
        title="Coffee Shop Stories",
        artist="Slow Stereo",
        genre="jazz",
        mood="relaxed",
        energy=0.37,
        tempo_bpm=90,
        valence=0.71,
        danceability=0.54,
        acousticness=0.89,
    ),

    # ── Synthwave ──────────────────────────────────────────────────────────
    Song(
        id=8,
        title="Night Drive Loop",
        artist="Neon Echo",
        genre="synthwave",
        mood="moody",
        energy=0.75,
        tempo_bpm=110,
        valence=0.49,
        danceability=0.73,
        acousticness=0.22,
    ),

    # ── Lofi ───────────────────────────────────────────────────────────────
    Song(
        id=9,
        title="Focus Flow",
        artist="LoRoom",
        genre="lofi",
        mood="focused",
        energy=0.40,
        tempo_bpm=80,
        valence=0.59,
        danceability=0.60,
        acousticness=0.78,
    ),

    # ── Indie Pop ──────────────────────────────────────────────────────────
    Song(
        id=10,
        title="Rooftop Lights",
        artist="Indigo Parade",
        genre="indie pop",
        mood="happy",
        energy=0.76,
        tempo_bpm=124,
        valence=0.81,
        danceability=0.82,
        acousticness=0.35,
    ),

    # ── Hip-Hop ────────────────────────────────────────────────────────────
    Song(
        id=11,
        title="Corner Store Flex",
        artist="Dray Minus",
        genre="hip-hop",
        mood="confident",
        energy=0.78,
        tempo_bpm=95,
        valence=0.72,
        danceability=0.85,
        acousticness=0.12,
    ),

    # ── R&B ────────────────────────────────────────────────────────────────
    Song(
        id=12,
        title="Golden Hour Drive",
        artist="Sable June",
        genre="r&b",
        mood="romantic",
        energy=0.55,
        tempo_bpm=88,
        valence=0.76,
        danceability=0.74,
        acousticness=0.28,
    ),

    # ── Classical ──────────────────────────────────────────────────────────
    Song(
        id=13,
        title="Raindrop Sonata",
        artist="Clara Voss",
        genre="classical",
        mood="melancholic",
        energy=0.22,
        tempo_bpm=52,
        valence=0.32,
        danceability=0.25,
        acousticness=0.97,
    ),

    # ── Country ────────────────────────────────────────────────────────────
    Song(
        id=14,
        title="Dirt Road Memory",
        artist="The Wayfields",
        genre="country",
        mood="nostalgic",
        energy=0.61,
        tempo_bpm=104,
        valence=0.68,
        danceability=0.65,
        acousticness=0.72,
    ),

    # ── EDM ────────────────────────────────────────────────────────────────
    Song(
        id=15,
        title="Overdrive Horizon",
        artist="Pulse Architect",
        genre="edm",
        mood="euphoric",
        energy=0.96,
        tempo_bpm=128,
        valence=0.88,
        danceability=0.95,
        acousticness=0.04,
    ),

    # ── Folk ───────────────────────────────────────────────────────────────
    Song(
        id=16,
        title="Empty Porch Song",
        artist="Hazel Wren",
        genre="folk",
        mood="sad",
        energy=0.31,
        tempo_bpm=68,
        valence=0.28,
        danceability=0.38,
        acousticness=0.91,
    ),

    # ── Metal ──────────────────────────────────────────────────────────────
    Song(
        id=17,
        title="Iron and Ash",
        artist="Gravemass",
        genre="metal",
        mood="angry",
        energy=0.97,
        tempo_bpm=168,
        valence=0.22,
        danceability=0.52,
        acousticness=0.06,
    ),

    # ── Soul ───────────────────────────────────────────────────────────────
    Song(
        id=18,
        title="Bring It On Home",
        artist="The Velvet Groove",
        genre="soul",
        mood="uplifting",
        energy=0.71,
        tempo_bpm=112,
        valence=0.89,
        danceability=0.83,
        acousticness=0.38,
    ),
]


# ---------------------------------------------------------------------------
# EXAMPLE USER PROFILES
# Three different listener types to test against the catalog.
# Each profile drives different recommendations.
# ---------------------------------------------------------------------------

# Listener who prefers calm, warm, background music
PROFILE_CHILL = UserProfile(
    favorite_genre="lofi",
    favorite_mood="chill",
    target_energy=0.38,
    likes_acoustic=True,
)

# Listener who wants high-energy workout music
PROFILE_HYPE = UserProfile(
    favorite_genre="pop",
    favorite_mood="intense",
    target_energy=0.92,
    likes_acoustic=False,
)

# Listener who likes moody electronic music
PROFILE_MOODY = UserProfile(
    favorite_genre="synthwave",
    favorite_mood="moody",
    target_energy=0.75,
    likes_acoustic=False,
)


# ---------------------------------------------------------------------------
# CATALOG SUMMARY (printed when this file is run directly)
# Shows all songs with their key scoring features at a glance.
# ---------------------------------------------------------------------------

def print_catalog() -> None:
    print("=" * 72)
    print(f"{'SONG CATALOG':^72}")
    print(f"{f'{len(CATALOG)} songs from data/songs.csv':^72}")
    print("=" * 72)
    print(f"{'#':<4} {'Title':<24} {'Genre':<12} {'Mood':<10} {'NRG':>5} {'VAL':>5} {'ACOU':>5}")
    print("-" * 72)
    for song in CATALOG:
        print(
            f"{song.id:<4} "
            f"{song.title:<24} "
            f"{song.genre:<12} "
            f"{song.mood:<10} "
            f"{song.energy:>5.2f} "
            f"{song.valence:>5.2f} "
            f"{song.acousticness:>5.2f}"
        )
    print("-" * 72)
    print(f"  NRG = energy  |  VAL = valence  |  ACOU = acousticness")
    print(f"  All values on a 0.0 – 1.0 scale")
    print()

    # Genre breakdown
    genres: dict[str, list[str]] = {}
    for song in CATALOG:
        genres.setdefault(song.genre, []).append(song.title)
    print("Genres in catalog:")
    for genre, titles in sorted(genres.items()):
        print(f"  {genre:<14} -> {', '.join(titles)}")
    print()

    # Mood breakdown
    moods: dict[str, list[str]] = {}
    for song in CATALOG:
        moods.setdefault(song.mood, []).append(song.title)
    print("Moods in catalog:")
    for mood, titles in sorted(moods.items()):
        print(f"  {mood:<14} -> {', '.join(titles)}")
    print()

    # Feature ranges
    energies     = [s.energy for s in CATALOG]
    valences     = [s.valence for s in CATALOG]
    acousticness = [s.acousticness for s in CATALOG]
    print("Feature ranges across catalog:")
    print(f"  energy       {min(energies):.2f} -> {max(energies):.2f}")
    print(f"  valence      {min(valences):.2f} -> {max(valences):.2f}")
    print(f"  acousticness {min(acousticness):.2f} -> {max(acousticness):.2f}")
    print("=" * 72)


if __name__ == "__main__":
    print_catalog()
