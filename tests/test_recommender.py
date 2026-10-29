from pathlib import Path
import pytest
from src.recommender import load_songs, score_song, recommend_songs, Song, UserProfile, Recommender

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def songs():
    return load_songs(ROOT / "data" / "songs.csv")

def test_loads_expanded_dataset_and_numeric_types(songs):
    assert len(songs) == 20
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["tempo_bpm"], int)
    assert isinstance(songs[0]["popularity"], int)
    assert isinstance(songs[0]["mood_tags"], list)

def test_exact_genre_and_mood_add_reasons(songs):
    score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 0.82}, songs[0])
    assert score > 3
    assert any("genre match" in reason for reason in reasons)
    assert any("mood match" in reason for reason in reasons)

def test_energy_similarity_rewards_closeness(songs):
    close, _ = score_song({"energy": 0.82}, songs[0])
    far, _ = score_song({"energy": 0.82}, songs[16])
    assert close > far

def test_recommendations_are_sorted_and_top_k(songs):
    recs = recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=5)
    assert len(recs) == 5
    assert all(recs[i][1] >= recs[i + 1][1] for i in range(len(recs) - 1))
    assert recs[0][0]["title"] in {"Sunrise City", "Rooftop Lights"}

def test_scoring_modes_produce_valid_results(songs):
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    for mode in ("genre-first", "mood-first", "energy-focused"):
        assert len(recommend_songs(prefs, songs, 3, mode)) == 3
    with pytest.raises(ValueError):
        score_song(prefs, songs[0], "unknown")

def test_diversity_penalty_changes_explanations_or_order(songs):
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    baseline = recommend_songs(prefs, songs, 5)
    diverse = recommend_songs(prefs, songs, 5, diversity_penalty=1.5)
    assert len(diverse) == 5
    assert any("diversity penalty" in reason for _, _, reason in diverse)
    assert baseline[0][0]["title"] == diverse[0][0]["title"]

def test_invalid_k_and_penalty_rejected(songs):
    with pytest.raises(ValueError): recommend_songs({}, songs, -1)
    with pytest.raises(ValueError): recommend_songs({}, songs, 3, diversity_penalty=-1)

def test_oop_api_explains_recommendation(songs):
    model = Recommender([Song(**{**s, "mood_tags": ";".join(s["mood_tags"])}) for s in songs])
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8)
    assert len(model.recommend(user, 3)) == 3
    assert "Score" in model.explain_recommendation(user, model.songs[0])

def test_advanced_numeric_features_can_affect_scores(songs):
    target_profile = {"popularity": 82, "instrumentalness": 0.02, "lyrical_complexity": 0.45}
    score_match, reasons_match = score_song(target_profile, songs[0])
    score_mismatch, _ = score_song(target_profile, songs[16])
    assert score_match > score_mismatch
    assert any("popularity similarity" in reason for reason in reasons_match)
    assert any("instrumentalness similarity" in reason for reason in reasons_match)
    assert any("lyrical complexity similarity" in reason for reason in reasons_match)

def test_advanced_numeric_features_can_affect_scores(songs):
    target_profile = {"popularity": 82, "instrumentalness": 0.02, "lyrical_complexity": 0.45}
    score_match, reasons_match = score_song(target_profile, songs[0])
    score_mismatch, _ = score_song(target_profile, songs[16])
    assert score_match > score_mismatch
    assert any("popularity similarity" in reason for reason in reasons_match)
    assert any("instrumentalness similarity" in reason for reason in reasons_match)
    assert any("lyrical complexity similarity" in reason for reason in reasons_match)
