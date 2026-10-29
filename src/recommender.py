"""Content-based music recommendation with explainable scoring and diversity controls."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional, Any

Number = Union[int, float]
NUMERIC_FIELDS = {
    "energy": float,
    "tempo_bpm": int,
    "valence": float,
    "danceability": float,
    "acousticness": float,
    "popularity": int,
    "release_decade": int,
    "instrumentalness": float,
    "lyrical_complexity": float,
}

@dataclass
class Song:
    """Represent a song and its audio, metadata, and descriptive attributes."""
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
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: str = ""
    instrumentalness: float = 0.0
    lyrical_complexity: float = 0.5

@dataclass
class UserProfile:
    """Represent a user's target musical preferences."""
    favorite_genre: str = "pop"
    favorite_mood: str = "happy"
    target_energy: float = 0.8
    likes_acoustic: bool = False
    target_danceability: Optional[float] = None
    target_valence: Optional[float] = None
    target_acousticness: Optional[float] = None
    preferred_decade: Optional[int] = None
    preferred_tags: Optional[List[str]] = None


def _number(value: Any, converter: type = float) -> Any:
    """Convert a CSV value to a number, rejecting invalid numeric data clearly."""
    try:
        return converter(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Expected a valid {converter.__name__}, received {value!r}") from exc


def load_songs(csv_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load song rows from CSV, converting numeric columns to numeric values."""
    path = Path(csv_path)
    if not path.exists():
        # Also support running the module from the repository root or another cwd.
        candidate = Path(__file__).resolve().parent.parent / path
        if candidate.exists():
            path = candidate
        else:
            raise FileNotFoundError(f"Song CSV not found: {csv_path}")
    songs: List[Dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"id", "title", "artist", "genre", "mood", "energy", "tempo_bpm", "valence", "danceability", "acousticness"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
        for row in reader:
            song: Dict[str, Any] = dict(row)
            song["id"] = _number(row["id"], int)
            for field, converter in NUMERIC_FIELDS.items():
                if field in row and row[field] not in (None, ""):
                    song[field] = _number(row[field], converter)
            song["mood_tags"] = [tag.strip().lower() for tag in row.get("mood_tags", "").split(";") if tag.strip()]
            songs.append(song)
    return songs


def _get(obj: Union[Dict[str, Any], Song], key: str, default: Any = None) -> Any:
    """Read a field from either a dictionary or Song dataclass."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _profile_value(prefs: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Return the first available preference alias."""
    for key in keys:
        if key in prefs and prefs[key] is not None:
            return prefs[key]
    return default


def _closeness(actual: Number, target: Number, max_gap: Number = 1.0) -> float:
    """Return a normalized 0-to-1 similarity score, where 1 is an exact match."""
    if max_gap <= 0:
        return 1.0 if actual == target else 0.0
    return max(0.0, 1.0 - abs(float(actual) - float(target)) / float(max_gap))


def score_song(user_prefs: Dict[str, Any], song: Union[Dict[str, Any], Song], mode: str = "genre-first") -> Tuple[float, List[str]]:
    """Score one song for a profile and return a numeric score plus human-readable reasons."""
    modes = {"genre-first", "mood-first", "energy-focused"}
    if mode not in modes:
        raise ValueError(f"Unknown scoring mode {mode!r}. Choose one of: {', '.join(sorted(modes))}")
    genre = str(_profile_value(user_prefs, "genre", "favorite_genre", default="")).strip().lower()
    mood = str(_profile_value(user_prefs, "mood", "favorite_mood", default="")).strip().lower()
    target_energy = _profile_value(user_prefs, "energy", "target_energy")
    target_dance = _profile_value(user_prefs, "danceability", "target_danceability")
    target_valence = _profile_value(user_prefs, "valence", "target_valence")
    target_acoustic = _profile_value(user_prefs, "acousticness", "target_acousticness")
    target_popularity = _profile_value(user_prefs, "popularity", "target_popularity")
    target_instrumentalness = _profile_value(user_prefs, "instrumentalness", "target_instrumentalness")
    target_lyrical_complexity = _profile_value(user_prefs, "lyrical_complexity", "target_lyrical_complexity")
    preferred_decade = _profile_value(user_prefs, "release_decade", "preferred_decade")
    preferred_tags = _profile_value(user_prefs, "mood_tags", "preferred_tags", default=[])
    if isinstance(preferred_tags, str):
        preferred_tags = [t.strip().lower() for t in preferred_tags.split(";") if t.strip()]
    else:
        preferred_tags = [str(t).lower() for t in (preferred_tags or [])]

    weights = {
        "genre-first": {"genre": 2.0, "mood": 1.0, "energy": 1.5, "danceability": 0.6, "valence": 0.5, "acousticness": 0.4, "popularity": 0.35, "instrumentalness": 0.25, "lyrical_complexity": 0.25, "decade": 0.25, "tags": 0.4},
        "mood-first": {"genre": 0.75, "mood": 2.0, "energy": 1.0, "danceability": 0.5, "valence": 0.8, "acousticness": 0.4, "popularity": 0.25, "instrumentalness": 0.2, "lyrical_complexity": 0.3, "decade": 0.2, "tags": 0.6},
        "energy-focused": {"genre": 0.75, "mood": 0.75, "energy": 2.5, "danceability": 0.8, "valence": 0.4, "acousticness": 0.25, "popularity": 0.2, "instrumentalness": 0.15, "lyrical_complexity": 0.15, "decade": 0.1, "tags": 0.25},
    }[mode]
    score = 0.0
    reasons: List[str] = []
    song_genre = str(_get(song, "genre", "")).lower()
    song_mood = str(_get(song, "mood", "")).lower()
    if genre and song_genre == genre:
        score += weights["genre"]
        reasons.append(f"genre match (+{weights['genre']:.2f})")
    if mood and song_mood == mood:
        score += weights["mood"]
        reasons.append(f"mood match (+{weights['mood']:.2f})")
    if target_energy is not None:
        similarity = _closeness(_get(song, "energy", 0.5), target_energy)
        points = similarity * weights["energy"]
        score += points
        reasons.append(f"energy similarity {similarity:.2f} (+{points:.2f})")
    for pref, field, weight_key, label in [
        (target_dance, "danceability", "danceability", "danceability"),
        (target_valence, "valence", "valence", "valence"),
        (target_acoustic, "acousticness", "acousticness", "acousticness"),
        (target_popularity, "popularity", "popularity", "popularity"),
        (target_instrumentalness, "instrumentalness", "instrumentalness", "instrumentalness"),
        (target_lyrical_complexity, "lyrical_complexity", "lyrical_complexity", "lyrical complexity"),
    ]:
        if pref is not None:
            max_gap = 100.0 if field == "popularity" else 1.0
            similarity = _closeness(_get(song, field, 50 if field == "popularity" else 0.5), pref, max_gap=max_gap)
            points = similarity * weights[weight_key]
            score += points
            reasons.append(f"{label} similarity {similarity:.2f} (+{points:.2f})")
    if preferred_decade is not None and _get(song, "release_decade") is not None:
        if int(_get(song, "release_decade")) == int(preferred_decade):
            score += weights["decade"]
            reasons.append(f"release decade match (+{weights['decade']:.2f})")
    song_tags = _get(song, "mood_tags", []) or []
    if isinstance(song_tags, str):
        song_tags = [t.strip().lower() for t in song_tags.split(";") if t.strip()]
    else:
        song_tags = [str(t).lower() for t in song_tags]
    matching_tags = sorted(set(preferred_tags) & set(song_tags))
    if matching_tags:
        points = weights["tags"] * len(matching_tags)
        score += points
        reasons.append(f"mood tag match ({', '.join(matching_tags)}) (+{points:.2f})")
    likes_acoustic = bool(_profile_value(user_prefs, "likes_acoustic", default=False))
    if likes_acoustic:
        acoustic = float(_get(song, "acousticness", 0.0))
        points = 0.5 * acoustic
        score += points
        reasons.append(f"acoustic preference (+{points:.2f})")
    if not reasons:
        reasons.append("no matching preferences; neutral baseline")
    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict[str, Any], songs: List[Dict[str, Any]], k: int = 5, mode: str = "genre-first", diversity_penalty: float = 0.0) -> List[Tuple[Dict[str, Any], float, str]]:
    """Rank songs by score, optionally penalizing repeated artists and genres."""
    if k < 0:
        raise ValueError("k must be non-negative")
    if diversity_penalty < 0:
        raise ValueError("diversity_penalty must be non-negative")
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        scored.append({"song": song, "base_score": score, "score": score, "reasons": reasons})
    # Greedy re-ranking makes diversity depend on what is already in the result list.
    results: List[Tuple[Dict[str, Any], float, str]] = []
    selected_artists: set = set()
    selected_genres: set = set()
    remaining = scored[:]
    while remaining and len(results) < k:
        for item in remaining:
            penalty = 0.0
            song = item["song"]
            duplicate_artist = _get(song, "artist", "") in selected_artists
            duplicate_genre = _get(song, "genre", "") in selected_genres
            if diversity_penalty:
                if duplicate_artist:
                    penalty += diversity_penalty
                if duplicate_genre:
                    penalty += diversity_penalty * 0.5
            item["score"] = item["base_score"] - penalty
            item["rank_reasons"] = item["reasons"][:]
            if duplicate_artist and diversity_penalty:
                item["rank_reasons"].append(f"repeat-artist diversity penalty (-{diversity_penalty:.2f})")
            if duplicate_genre and diversity_penalty:
                item["rank_reasons"].append(f"repeat-genre diversity penalty (-{diversity_penalty * 0.5:.2f})")
        best = max(remaining, key=lambda item: (item["score"], -int(_get(item["song"], "id", 0))))
        remaining.remove(best)
        song = best["song"]
        explanation = "; ".join(best["rank_reasons"])
        results.append((song, round(best["score"], 2), explanation))
        selected_artists.add(_get(song, "artist", ""))
        selected_genres.add(_get(song, "genre", ""))
    return results


class Recommender:
    """Object-oriented interface to the same explainable recommendation engine."""
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "genre-first", diversity_penalty: float = 0.0) -> List[Song]:
        prefs = {"genre": user.favorite_genre, "mood": user.favorite_mood, "energy": user.target_energy, "likes_acoustic": user.likes_acoustic, "danceability": user.target_danceability, "valence": user.target_valence, "acousticness": user.target_acousticness, "release_decade": user.preferred_decade, "mood_tags": user.preferred_tags}
        ranked = recommend_songs(prefs, [song.__dict__ for song in self.songs], k, mode, diversity_penalty)
        by_id = {song.id: song for song in self.songs}
        return [by_id[item[0]["id"]] for item in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain why a song matches the supplied user profile."""
        prefs = {"genre": user.favorite_genre, "mood": user.favorite_mood, "energy": user.target_energy, "likes_acoustic": user.likes_acoustic, "danceability": user.target_danceability, "valence": user.target_valence, "acousticness": user.target_acousticness, "release_decade": user.preferred_decade, "mood_tags": user.preferred_tags}
        score, reasons = score_song(prefs, song)
        return f"Score {score:.2f}: " + "; ".join(reasons)


def to_song(row: Dict[str, Any]) -> Song:
    """Convert a loaded CSV dictionary to a Song dataclass instance."""
    values = dict(row)
    tags = values.get("mood_tags", [])
    values["mood_tags"] = ";".join(tags) if isinstance(tags, list) else tags
    allowed = Song.__dataclass_fields__.keys()
    return Song(**{key: value for key, value in values.items() if key in allowed})
