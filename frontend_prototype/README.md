# Frontend Prototype

`rocket_launch.html` — the **aa** level (Rocket Launch), built end-to-end: live mic input →
loudness scoring → canvas rendering. This is the first full vertical slice proving the
pipeline works before building the other five levels.

## Running it

Browsers block microphone access on `file://` pages (not a "secure context"). You need to
serve it over `localhost`:

```bash
cd frontend_prototype
python3 -m http.server 8000
```

Then open **http://localhost:8000/rocket_launch.html** in your browser (Chrome/Edge/Firefox
all work; Safari can be pickier about mic permissions, use Chrome first if something looks
off). Allow microphone access when prompted.

## What it does

1. **Start screen** → **calibration** (2s quiet, then 2.5s of you saying "AAAA" as loud as
   you can) → **play**.
2. Calibration sets the noise floor and max-expected volume dynamically per-user, rather
   than using the fixed constants in the Python `audio_features/vowel_loudness.py` — those
   constants are still the right *starting point* reference, this just personalizes them.
3. The flame beneath the rocket is driven directly by your live volume in real time — that's
   the visual "signature," not decoration. A rocket with nose-cone detailing, side boosters
   (each with their own small flame), a windowed cockpit, two-tone fins, and a blinking
   antenna light.
4. **Speed scales with both loudness and pitch.** Louder voice climbs faster (a much wider
   range than before — barely-passing vs. really loud now feels dramatically different).
   A confidently high, sustained pitch adds up to an extra 50% speed on top, visualized as
   a distinct cyan sparkle trail (separate from the warm amber flame, so kids can tell "loud"
   apart from "loud AND high-pitched" at a glance). Pitch detection is autocorrelation-based,
   unit tested against known-frequency tones (`rocket_logic.test.js`) — including catching
   and fixing an octave error where a clean tone was initially misdetected at 1/3 its true
   frequency. **Important**: only the loudness score is what gets logged/would feed the DRL
   agent — pitch is a pure client-side game-feel bonus, not part of the trained skill.
5. **The agent gives feedback between attempts.** After each successful launch, a rule-based
   difficulty agent (same logic as `agent/baselines.py`'s `RuleBasedAgent`, ported to JS)
   looks at how long that attempt took and adjusts the loudness threshold for next time —
   raising it if you launched in under 4s ("that was fast!"), lowering it if it took over 12s
   ("let's make the next one easier"), holding otherwise. The adjustment is bounded to
   `[0.20, 0.55]` and shown as a message on the success screen — this mirrors the "safety
   envelope" principle from the project doc (a difficulty controller should only ever nudge
   within pre-approved bounds).
6. No fail state: quiet just means a gentle descent, with an encouraging caption after a few
   seconds of silence. Reaching the top triggers a celebration overlay with a replay button
   the child controls.
7. Settings (gear icon, top right): reduce motion, mute sounds, recalibrate mic (also resets
   the difficulty agent back to baseline).

## Agent feedback — what's real here vs. what's a stand-in

This prototype's live difficulty feedback is the **rule-based agent (rung 1)** of the
comparison ladder, ported to plain JS so it can run with no backend. The more advanced
agents — tabular Q-learning (`agent/baselines.py`) and PPO / recurrent PPO
(`agent/train_ppo.py`) — are real, trained, and evaluated (`agent/evaluate.py`), but they're
Python-side and would need a small API serving live decisions to actually drive this page.
That's the natural next step once there's a backend to call.

## What's simplified vs. the real Python extractor

This reimplements the RMS/threshold logic from `audio_features/vowel_loudness.py` in
JavaScript (Web Audio API doesn't run Python) — same math, same shape. The core scoring
and altitude-state logic was unit tested in isolation (`rocket_logic.js` +
`rocket_logic.test.js`, not shipped in the HTML) before being embedded here — worth
re-running those tests if you touch the scoring math.

## Known gaps before this is "done"

- Only tested with synthetic signals and manual browser testing, not real child voices yet
- No backend connection — doesn't write anything to `schemas/session_event.py`'s shape yet
- Safari's Web Audio quirks haven't been specifically tested
- Sound effects are synthesized tones (oscillators), not designed audio — fine for a
  prototype, worth commissioning/designing real ones before shipping
