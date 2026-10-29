# AI Interactions and Agentic Workflow

This document records representative prompts and the implementation decisions they guided. The prompts below are reproducible documentation of the workflow; they should not be treated as a verbatim transcript of an external AI tool session.

## Phase 1 — Research real recommendation systems

**Prompt used / proposed:**

> Explain collaborative filtering and content-based filtering in music recommendation systems. Compare the kinds of signals each can use, describe cold-start and filter-bubble risks, and distinguish general industry practices from claims about proprietary systems. Give me a concise explanation suitable for a Python classroom project.

**Design decision:** The project uses content-based filtering because its scoring can be inspected and explained. The README describes collaborative, content-based, and hybrid approaches without claiming access to any platform's proprietary ranking implementation.

## Phase 2 — Analyze the dataset and design the scoring rule

**Prompt used / proposed:**

> Inspect the songs.csv headers and values. Recommend a small set of categorical and numerical features for a transparent recommender. Propose a normalized similarity formula that gives a higher score when a numeric song feature is closer to the user's target, not simply higher. Explain weights and how to keep the single-song scoring rule separate from ranking a list.

**Decision:** Genre-first baseline weights are +2.0 for exact genre, +1.0 for exact mood, and up to +1.5 for energy similarity. Additional preference fields contribute only when the profile supplies a target. Ranking is a separate step that sorts/selects the top k.

## Phase 2 — Expand the dataset (Stretch Goal 1)

**Prompt used / proposed:**

> Extend this small song catalog by ten illustrative rows with diverse genres and moods. Preserve the existing CSV headers and valid CSV quoting. Add five advanced fields: popularity (0–100), release decade, semicolon-separated mood tags, instrumentalness (0–1), and lyrical complexity (0–1). Avoid duplicate IDs and explain that these are synthetic values, not verified audio measurements.

**Changes:** Added 10 records for a total of 20 songs. Added `popularity`, `release_decade`, `mood_tags`, `instrumentalness`, and `lyrical_complexity`. Numeric values are converted during CSV loading. Mood tags are parsed into a list.

**Manual verification:** Confirmed all 20 records load, numeric columns are converted to numeric types, tags parse correctly, and tests cover the data loader. All five advanced fields can affect scores when the user profile explicitly supplies corresponding targets; popularity uses a 0–100 range and instrumentalness/lyrical complexity use 0–1 ranges. The chosen weights are modest and mode-specific.

## Phase 3 — Implement and explain the scoring function

**Prompt used / proposed:**

> Implement score_song so it accepts a preference dictionary and one song dictionary, returns `(numeric_score, reasons)`, handles genre and mood matches, and calculates numerical similarity as `max(0, 1 - abs(actual - target))` for normalized features. Include clear explanations for each contribution and validate the scoring mode.

**Changes:** Implemented `score_song` with a tuple return value and reason strings. Added three explicit weight configurations: `genre-first`, `mood-first`, and `energy-focused`.

**Manual verification:** Unit tests check genre/mood reasons, target-energy closeness, and invalid modes. A close energy value scores higher than a distant value for the same target.

## Phase 3 — Ranking and CLI table (Stretch Goals 2 and 4)

**Prompt used / proposed:**

> Implement a ranking function that scores every song, sorts by the selected mode, and returns the top k as `(song, score, explanation)`. Keep score_song responsible for one song and recommend_songs responsible for list ranking. Add a CLI with several profiles and an ASCII table that includes title, artist, score, and reasons.

**Changes:** Implemented `recommend_songs`, six named evaluation profiles, command-line options for profile/mode/k, and a terminal table. `sorted`/selection logic operates on scored records without mutating the source song catalog.

**Manual verification:** Ran `python -m src.main` and profile/mode variations. Verified that the default profile loads 20 songs and returns five ranked results.

## Stretch Goal 3 — Diversity and fairness logic

**Prompt used / proposed:**

> Add an optional diversity penalty during re-ranking. Penalize a candidate when its artist already appears in the selected results, and apply a smaller penalty when its genre repeats. Recompute candidate ranking at each selection step and include the penalty in the explanation. Keep the default penalty at zero so baseline behavior remains available.

**Changes:** Added `diversity_penalty`; repeated artists receive the full penalty and repeated genres receive half. The greedy selection process recalculates adjusted scores after each pick.

**Manual verification:** Ran the default profile with and without a penalty and tested that explanations contain diversity-penalty reasons. The feature can alter later selections but does not guarantee a mathematically optimal diversity ranking.

## Phase 4 — Evaluation and edge cases

**Prompt used / proposed:**

> Suggest edge-case profiles for a small content-based recommender, including a conflicting profile with high energy and high acousticness but a peaceful mood. Predict which features may dominate, then propose a controlled experiment that changes only the scoring mode or diversity penalty.

**Experiment performed:** Compared `happy-pop` under `genre-first` and `mood-first`, ran `chill-lofi` and `intense-rock`, and ran a conflicting profile. The top results differ in ways consistent with the weights. Under mood-first, `Rooftop Lights` outranks `Gym Hero` for happy-pop because the mood weight increases while genre weight decreases.

**Interpretation:** The conflicting profile demonstrates a limitation of additive scoring: strong points in one dimension can outweigh a mismatch in another. The system does not infer that the profile may be internally inconsistent.
