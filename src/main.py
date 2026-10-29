"""CLI runner for the music recommender simulation and its evaluation profiles."""
from __future__ import annotations
import argparse
import textwrap
from typing import Dict, Any, List, Tuple
from src.recommender import load_songs, recommend_songs

PROFILES: Dict[str, Dict[str, Any]] = {
    "happy-pop": {"genre": "pop", "mood": "happy", "energy": 0.8, "valence": 0.8, "danceability": 0.8, "mood_tags": ["bright", "feel-good"]},
    "chill-lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "acousticness": 0.8, "mood_tags": ["soft", "reflective"]},
    "intense-rock": {"genre": "rock", "mood": "intense", "energy": 0.95, "danceability": 0.55, "mood_tags": ["aggressive", "driving"]},
    "gym-hero": {"genre": "pop", "mood": "intense", "energy": 0.95, "danceability": 0.9, "valence": 0.75},
    "conflicted": {"genre": "metal", "mood": "peaceful", "energy": 0.95, "acousticness": 0.95, "mood_tags": ["gentle"]},
    "instrumental-focus": {"genre": "ambient", "mood": "focused", "energy": 0.3, "acousticness": 0.9, "mood_tags": ["minimal", "calm"]},
}


def print_table(recommendations: List[Tuple[dict, float, str]], profile_name: str, mode: str) -> None:
    """Print a readable ASCII table, wrapping rather than dropping explanations."""
    print(f"\nProfile: {profile_name} | Scoring mode: {mode}")
    headers = ("#", "Song", "Artist", "Score", "Why it ranked")
    explanation_width = 66
    widths = (3, 22, 18, 7, explanation_width)
    def line(values):
        print(" | ".join(str(value).ljust(widths[i]) for i, value in enumerate(values)))
    line(headers)
    print("-+-".join("-" * width for width in widths))
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        wrapped = textwrap.wrap(explanation, width=explanation_width) or [""]
        for line_index, explanation_line in enumerate(wrapped):
            values = (
                str(i) if line_index == 0 else "",
                str(song["title"])[:widths[1]] if line_index == 0 else "",
                str(song["artist"])[:widths[2]] if line_index == 0 else "",
                f"{score:.2f}" if line_index == 0 else "",
                explanation_line,
            )
            line(values)


def main() -> None:
    parser = argparse.ArgumentParser(description="Explainable content-based music recommender")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="happy-pop")
    parser.add_argument("--mode", choices=["genre-first", "mood-first", "energy-focused"], default="genre-first")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--diversity", type=float, default=0.0, help="Penalty for repeated artist; genre repetition gets half this penalty")
    args = parser.parse_args()
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    recs = recommend_songs(PROFILES[args.profile], songs, args.k, args.mode, args.diversity)
    print_table(recs, args.profile, args.mode)

if __name__ == "__main__":
    main()
