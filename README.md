# VibeFinder: Music Recommender Simulation

## Project Summary

VibeFinder is a CLI-first, explainable content-based music recommender built in Python. It loads a small CSV catalog, compares each song with a user's taste profile, scores the matches, and prints the highest-ranked songs with human-readable reasons. The project includes three scoring modes, an optional diversity re-ranking penalty, six evaluation profiles, an expanded 20-song dataset, unit tests, and a model card. It is a classroom simulation, not a production recommendation service.

## How the System Works

Large music platforms can combine multiple signals, including listening history, likes, skips, playlist additions, searches, context, and song metadata. Collaborative filtering finds patterns across users or items—for example, people who enjoy one song also tend to enjoy another. Content-based filtering compares attributes of a song with attributes or preferences associated with a listener. Real platforms may use hybrid systems and machine-learning ranking models; their exact production systems are proprietary and change over time. VibeFinder deliberately uses a transparent content-based scoring rule so each result can be explained.

### Data objects and features

- **Song:** `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`, `popularity`, `release_decade`, `mood_tags`, `instrumentalness`, and `lyrical_complexity`.
- **User profile:** preferred genre and mood, target energy, optional target danceability/valence/acousticness, optional preferred release decade, optional mood tags, and whether acoustic music is preferred.
- **Score:** a weighted sum of categorical matches and normalized numerical similarities. Numerical similarity is `max(0, 1 - abs(song_value - target_value))` for 0–1 attributes, so values closer to the target earn more points; they do not automatically earn more points just for being high.
- **Ranking:** score every song, then select the top `k`. Optional diversity re-ranking subtracts a penalty for an artist already selected and half that penalty for a repeated genre.

### Algorithm recipe

Default `genre-first` mode:

- Exact genre match: **+2.0**.
- Exact mood match: **+1.0**.
- Energy similarity: **0–1 similarity × 1.5**.
- If requested by a profile, danceability similarity × 0.6, valence similarity × 0.5, and acousticness similarity × 0.4.
- Optional exact release-decade match: +0.25.
- Each matching preferred mood tag: +0.4.
- If `likes_acoustic` is true, add 0.5 × song acousticness.

The modes change the weights, not the features: `genre-first` prioritizes genre; `mood-first` prioritizes mood; `energy-focused` emphasizes energy and danceability. Popularity, instrumentalness, and lyrical complexity are also optional numeric targets: popularity uses a 0–100 scale, while instrumentalness and lyrical complexity use 0–1 scales. They add points only when a profile supplies a target.

### Data flow

```text
User preferences + data/songs.csv
               ↓
      load_songs() parses CSV
               ↓
 score_song(profile, each song, mode)
               ↓
 rank by score (optional diversity penalty)
               ↓
 top-k list + explanations in terminal
```

## Real-world systems: collaborative vs. content-based

| Approach | Main idea | Example signals | Benefit | Limitation |
|---|---|---|---|---|
| Collaborative filtering | Learns from patterns across users or items | Plays, likes, skips, playlist co-occurrence | Can surface an unexpected song without relying on manually matching attributes | Can struggle with new users/items and popularity imbalance |
| Content-based filtering | Matches item attributes to a profile | Genre, mood, tempo, acousticness, tags | Can explain why an item's attributes match a profile and can work without other users' behavior | Can repeat familiar attributes and create a filter bubble |
| Hybrid | Combines approaches and potentially other ranking signals | Behavioral, metadata, contextual, and model features | Can balance different kinds of evidence | More complex to evaluate and explain |

The table describes general recommender-system concepts, not a claim about the exact current internal architecture of any named platform.

## Getting Started

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

### Run profiles and modes

```bash
python -m src.main --profile happy-pop
python -m src.main --profile chill-lofi
python -m src.main --profile intense-rock
python -m src.main --profile conflicted
python -m src.main --profile happy-pop --mode mood-first
python -m src.main --profile happy-pop --mode energy-focused
python -m src.main --profile happy-pop --diversity 1.5
python -m src.main --profile instrumental-focus --k 3
```

Available profiles: `happy-pop`, `chill-lofi`, `intense-rock`, `gym-hero`, `conflicted`, and `instrumental-focus`. Available modes: `genre-first`, `mood-first`, and `energy-focused`.

### Running tests

```bash
python -m pytest -q
```

## Sample Recommendation Output

Verified by running `python -m src.main` against the included CSV. Explanations are shortened in this README for readability; the terminal wraps and prints the full explanation field.

```text
Loaded songs: 20

Profile: happy-pop | Scoring mode: genre-first
# | Song            | Artist        | Score
--+-----------------+---------------+------
1 | Sunrise City    | Neon Echo     | 6.34
2 | Gym Hero        | Max Pulse      | 4.34
3 | Rooftop Lights  | Indigo Parade | 3.92
4 | Golden Hour Run | Tempo Theory  | 2.78
5 | City on Repeat  | Metro Static  | 2.54
```

## Evaluation Profiles and Results

The profile outputs were generated locally using the supplied implementation and dataset. They demonstrate expected behavior, not human-subject testing or measured real-world accuracy.

- **Happy Pop:** `Sunrise City` ranks first because its pop genre, happy mood, high energy, high valence, danceability, and matching tags fit the profile.
- **Chill Lofi:** `Library Rain`, `Midnight Coding`, and `Focus Flow` rank highly because they share lofi/chill or have low energy and high acousticness.
- **Intense Rock:** `Storm Runner` ranks first because it matches rock and intense and has very high energy.
- **Conflicted:** the profile requests metal, peaceful, high energy, and high acousticness. `After the Fire` ranks first mainly because the metal genre match and energy similarity outweigh its mismatch with the acoustic preference. This is an example of a weighted score resolving conflicting preferences without understanding the conflict semantically.

### Scoring-mode experiment

For `happy-pop`, the `genre-first` mode ranks `Gym Hero` ahead of `Rooftop Lights` because the genre match is worth 2 points. In `mood-first`, `Rooftop Lights` moves above `Gym Hero` because the happy-mood match is worth 2 points while genre is worth 0.75. The order changes because the weights change, not because the dataset changed.

### Diversity experiment

Run `python -m src.main --profile happy-pop --diversity 1.5`. The top song remains `Sunrise City`, while repeated artist/genre penalties can change later selections. The penalty is a heuristic, not a guarantee of optimal diversity; it may push down a relevant song simply because it resembles an already-selected item.

### Feature experiment

Optional numerical profile fields let you target valence, danceability, and acousticness. For example, `happy-pop` includes valence and danceability targets, while `chill-lofi` targets acousticness. Removing a target from a profile removes that feature's contribution, providing a straightforward feature-ablation experiment. Advanced metadata (`popularity`, `release_decade`, `mood_tags`, `instrumentalness`, `lyrical_complexity`) is included in the dataset; all five can influence score when explicitly requested by the profile.

## Limitations and Risks

- The catalog has only 20 hand-authored rows and is not representative of the breadth of real music.
- No listening behavior, skips, saves, playlists, user feedback, or collaborative signals are collected.
- The numerical similarity function assumes a linear relationship between closeness and preference.
- Exact genre and mood labels are brittle: synonyms and mixed moods are not recognized unless represented in tags.
- Genre and mood weights can favor a narrow set of familiar songs and contribute to a filter bubble.
- The dataset's metadata is illustrative rather than derived from verified audio analysis; scores should not be interpreted as objective quality or personal truth.
- Popularity can encode historical exposure and can amplify already popular artists if added without care.
- The diversity penalty can reduce relevance, and the scoring modes are manually selected rather than learned from evaluation data.

## Reflection

This project illustrates how a few explicit rules can turn song metadata and preferences into an ordered recommendation list. The most important design distinction is that a **scoring rule** judges one song, while a **ranking rule** compares all song scores to choose the top results. The reasons list makes the ranking more interpretable, but a plausible explanation does not prove the recommendation is accurate.

AI coding assistance is useful for brainstorming weights, scaffolding functions, and proposing edge cases. Generated code and explanations still need verification: numeric CSV fields must be converted before arithmetic, tests should cover sorting and edge cases, and documentation must not claim experiments that were not run. A next step would be to collect explicit user feedback, add a carefully evaluated hybrid approach, and compare relevance and diversity metrics across a larger, better-sourced catalog.

## Stretch Goals Completed

1. **Advanced features:** added popularity, release decade, detailed mood tags, instrumentalness, and lyrical complexity to the dataset and data model; release decade and mood tags can affect ranking when requested.
2. **Multiple scoring modes:** added genre-first, mood-first, and energy-focused strategies.
3. **Diversity and fairness logic:** added configurable repeated-artist and repeated-genre penalties during greedy re-ranking.
4. **Visual summary table:** terminal table includes rank, title, artist, score, and explanation.

See [`ai_interactions.md`](ai_interactions.md) for prompt records and manual verification notes, and [`model_card.md`](model_card.md) for the model card.
