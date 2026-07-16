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

## Relationship to BreathQuest

PhonemeQuest and BreathQuest are **two separate games**, each with their own levels and
mechanics, that will live on **one shared site** — same auth, same database, same
deployment. They don't reuse each other's game engines or visuals.

**PhonemeQuest's own levels:**

| Level | Extractor | Mechanic |
|---|---|---|
| aa | `audio_features/vowel_loudness.py` | Rocket Launch — sustained loud "aaa" powers a rocket up |
| oo | `audio_features/vowel_quality.py` | Submarine Dive — held, rounded "oo" dives deeper |
| ma | `audio_features/syllable_rhythm.py` | Drum Island — each clear "ma" hits a drum on the beat |
| fa | `audio_features/frication.py` | Kite Flyer — continuous "ffff" keeps a kite aloft |
| ha | `audio_features/aspiration_burst.py` | Dragon's Breath — a "ha" burst fires a balloon burner |
| word | `word_level/asr_match.py` | Village Builder — correct pronunciation places a building piece |

**Every extractor returns the same `FeatureResult` shape** (`audio_features/common.py`):
`score` (0-1, drives the on-screen mechanic directly), `is_valid_attempt`, `raw_features`
(diagnostics for the DRL agent + therapist dashboard) — a shared contract within
PhonemeQuest itself, independent of BreathQuest.

## Integration guide (for whoever merges this into the shared site)

**`schemas/session_event.py`** defines the exact shape PhonemeQuest needs written into
the shared `session_events` table (`skill_type: "phoneme"`, plus a `PhonemePayload`),
alongside BreathQuest's own rows (`skill_type: "breath"`). Do not create a second events
table — add the `skill_type` field to the existing schema and store `PhonemePayload` as
a JSON/JSONB column alongside it. Same pattern for auth/patients/sessions — one shared
identity and session model across both games, not two.

**Not yet built, by design** — these need the merged database/DRL agent to make sense of,
so building them standalone now would mean redoing them:
- Tabular Q-learning and the deep (PPO) policy — `agent/baselines.py` currently has the
  rule-based and contextual-bandit rungs of the comparison ladder only
- Absolute Learning Progress reward (see `agent/env.py`, marked with a TODO) — currently
  using the simpler target-success-rate reward
- Real audio calibration — all thresholds in the extractors are starting points, not
  calibrated against real child voice samples yet
