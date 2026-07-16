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
   the visual "signature," not decoration.
4. No fail state: quiet just means a gentle descent, with an encouraging caption after a few
   seconds of silence. Reaching the top triggers a celebration overlay with a replay button
   the child controls.
5. Settings (gear icon, top right): reduce motion, mute sounds, recalibrate mic.

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
