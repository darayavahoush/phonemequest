# PhonemeQuest

Speech-sound practice game module for VaakSiddhi, designed to merge into **BreathQuest**
as a second "world" once both are ready. This repo is deliberately structured so that
merge is a matter of dropping folders in and renaming a few fields — not a rewrite.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt   # audio feature work — fast, no torch
pytest tests/ -v                  # confirm the skeleton runs
```

Only install the DRL stack once you're ready to train the agent (pulls in torch,
sizeable download):

```bash
pip install -r requirements-drl.txt
```

## Structure

```
audio_features/   five phoneme-specific extractors (aa, oo, ma, fa, ha)
word_level/       ASR-based word matching (wraps faster-whisper, already in VaakSiddhi)
schemas/          the integration contract — see below
simulator/        synthetic child model for training the DRL agent before real data exists
agent/            baseline agents (rule-based, contextual bandit) + gymnasium env
tests/            sanity tests against synthetic audio
```

## Integration guide (for whoever merges this into BreathQuest)

**Level -> extractor -> BreathQuest engine it reuses:**

| Level | Extractor | Reuses BreathQuest engine | What changes |
|---|---|---|---|
| aa | `audio_features/vowel_loudness.py` | Float Rider | swap generic amplitude for vowel-loudness scoring |
| oo | `audio_features/vowel_quality.py` | Balloon Pop | swap "any breath fills balloon" for formant + duration scoring |
| ma | `audio_features/syllable_rhythm.py` | Dandelion Storm | swap generic puff detection for syllable-onset rhythm scoring |
| fa | `audio_features/frication.py` | Dragon Fire | swap generic sustained blow for fricative noise-energy scoring |
| ha | `audio_features/aspiration_burst.py` | Candle Gauntlet | swap generic sharp puff for aspiration-burst scoring |
| word | `word_level/asr_match.py` | — none, net new | needs faster-whisper wired in |
| *(shared)* | — | Pinwheel | stays as-is, shared mic-calibration/warmup for the whole platform |

**Every extractor returns the same `FeatureResult` shape** (`audio_features/common.py`):
`score` (0-1, drives the on-screen mechanic directly, same as BreathQuest's live breath-bar
value), `is_valid_attempt`, `raw_features` (diagnostics for the DRL agent + therapist dashboard).
This mirrors BreathQuest's `AudioEngine` breath-value convention on purpose — integrating a
level should mean swapping the value that feeds the existing mechanic, not rewriting the
mechanic.

**`schemas/session_event.py`** defines the exact shape PhonemeQuest needs written into
BreathQuest's `session_events` table (`skill_type: "phoneme"`, plus a `PhonemePayload`).
Do not create a second events table — add the `skill_type` field to the existing schema
and store `PhonemePayload` as a JSON/JSONB column alongside it.

**Not yet built, by design** — these need the merged database/DRL agent to make sense of,
so building them standalone now would mean redoing them:
- Tabular Q-learning and the deep (PPO) policy — `agent/baselines.py` currently has the
  rule-based and contextual-bandit rungs of the comparison ladder only
- Absolute Learning Progress reward (see `agent/env.py`, marked with a TODO) — currently
  using the simpler target-success-rate reward
- Real audio calibration — all thresholds in the extractors are starting points, not
  calibrated against real child voice samples yet
