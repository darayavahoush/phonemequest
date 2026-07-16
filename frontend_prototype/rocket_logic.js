// Pure logic, no DOM/Web Audio dependencies, so it can be unit tested directly
// in Node before being embedded in the game's <script> block.

function computeRMS(floatSamples) {
  let sumSquares = 0;
  for (let i = 0; i < floatSamples.length; i++) {
    sumSquares += floatSamples[i] * floatSamples[i];
  }
  return Math.sqrt(sumSquares / floatSamples.length);
}

function computeLoudnessScore(rms, noiseFloor, maxExpected) {
  if (rms <= noiseFloor) return 0;
  const score = (rms - noiseFloor) / (maxExpected - noiseFloor);
  return Math.max(0, Math.min(1, score));
}

// Altitude state machine: sustained loud score raises altitude smoothly,
// low score lowers it gently — never abruptly, so there's no "crash" feeling.
function updateAltitude(currentAltitude, score, dt, config) {
  const { riseRate, fallRate, scoreThreshold } = config;
  let next;
  if (score >= scoreThreshold) {
    const intensity = (score - scoreThreshold) / (1 - scoreThreshold); // 0..1
    next = currentAltitude + riseRate * (0.3 + 0.7 * intensity) * dt;
  } else {
    next = currentAltitude - fallRate * dt;
  }
  return Math.max(0, Math.min(1, next));
}

module.exports = { computeRMS, computeLoudnessScore, updateAltitude };
