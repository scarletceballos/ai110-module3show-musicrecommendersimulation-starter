# Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0** — an explainable, content-based music recommender simulation.

## 2. Intended Use

VibeFinder is designed for classroom exploration of how user preferences and song metadata can be converted into ranked recommendations. It is intended for demonstration and experimentation, not for commercial deployment, mental-health inference, copyright decisions, or claims about what a person will definitely enjoy. It assumes that a user's stated genre, mood, and numerical targets are meaningful approximations of their taste.

## 3. How the Model Works

The program compares a user profile with each song. Exact genre and mood matches earn weighted points. Numerical preferences such as energy, danceability, valence, and acousticness earn more points when a song's value is closer to the user's target. Optional mood tags and release decade can add points when the profile specifies them. Popularity (0–100), instrumentalness (0–1), and lyrical complexity (0–1) also use closeness-to-target scores when explicitly requested. Popularity (0–100), instrumentalness (0–1), and lyrical complexity (0–1) also use closeness-to-target scores when explicitly requested. The program then ranks songs by score and can apply a diversity penalty to repeated artists and genres. The three modes—genre-first, mood-first, and energy-focused—use different weights. Each result includes reasons describing its score contributions.

## 4. Data

The CSV contains **20 illustrative song records**. The first 10 preserve the starter catalog; 10 additional rows broaden the range of genres and moods. Fields include genre, mood, energy, tempo, valence, danceability, acousticness, popularity, release decade, mood tags, instrumentalness, and lyrical complexity. The data is hand-authored for this exercise, not verified from audio or a licensed streaming catalog. It does not include real listening histories, skips, likes, playlists, demographics, or contextual information. Popularity, instrumentalness, and lyrical complexity can contribute when the user profile explicitly supplies target values; their scales are 0–100, 0–1, and 0–1 respectively.

## 5. Strengths

- The rules are simple to inspect and modify.
- Numerical similarity rewards closeness to a target rather than always rewarding a high or low value.
- The program returns human-readable reasons for each recommendation.
- Multiple scoring modes make the impact of weight choices visible.
- Optional diversity penalties help demonstrate the trade-off between relevance and variety.
- Unit tests check loading, numeric conversion, scoring, ranking, modes, diversity, and the object-oriented interface.

## 6. Limitations and Bias

The small dataset is not representative, and its genre distribution influences which kinds of songs can be recommended. Genre-first scoring can over-prioritize an exact genre match, while mood-first can over-prioritize mood. Users whose tastes do not fit the available labels may receive poor recommendations. The linear energy similarity formula does not model nuanced relationships between tempo, loudness, emotion, or listening context. A content-based system can create a filter bubble by repeatedly showing items that resemble stated preferences. The diversity penalty is only a heuristic: it can demote a relevant song and does not measure fairness across people or artists. The dataset's popularity and audio-related metadata are illustrative and may not reflect real-world measurements.

## 7. Evaluation

The included CLI was run for `happy-pop`, `chill-lofi`, `intense-rock`, and a deliberately conflicting profile, and the `happy-pop` profile was compared under genre-first and mood-first modes. Happy Pop places `Sunrise City` first due to matching genre, mood, energy, valence, danceability, and tags. Chill Lofi favors low-energy acoustic lofi songs. Intense Rock puts `Storm Runner` first due to its rock/intense labels and high energy. The conflicting profile requests metal, peaceful mood, high energy, and high acousticness; `After the Fire` ranks first because the genre and energy points outweigh the acoustic mismatch. In the weight experiment, `Rooftop Lights` moves above `Gym Hero` under mood-first because mood receives more weight. The test suite passes with `python -m pytest -q` (8 tests). This evaluation is qualitative and based on expected behavior; no user study or ground-truth relevance labels were collected.

## 8. Future Work

1. Add a larger, documented dataset with reliable provenance and validate the metadata.
2. Evaluate with explicit user feedback and ranking metrics rather than intuition alone.
3. Experiment with popularity, instrumentalness, and lyrical complexity only after deciding how they should influence the result and checking for unwanted bias.
4. Add a hybrid recommender using anonymized interaction data, with privacy and cold-start considerations.
5. Improve explanations and diversity controls, and allow users to adjust feature weights.

## 9. Personal Reflection

This project showed how a transparent scoring rule can produce useful-looking recommendations without training a complex machine-learning model. It also showed that the weights encode assumptions: increasing genre weight can make the output less varied, while increasing mood weight can promote songs from other genres. The reasons list helps explain the output, but it cannot prove that a user will like the song. AI assistance can help design and debug a modular implementation, but code, arithmetic, tests, and documentation must be checked instead of accepting generated output uncritically. If I continued the project, I would collect feedback on recommendations, test more profiles, and compare relevance against diversity on a larger dataset.
