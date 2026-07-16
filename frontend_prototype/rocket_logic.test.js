const assert = require('assert');
const { computeRMS, computeLoudnessScore, updateAltitude } = require('./rocket_logic.js');

// --- computeRMS ---
assert.strictEqual(computeRMS([0, 0, 0, 0]), 0, 'silence should give RMS 0');

// Full-scale sine wave: RMS should be amplitude / sqrt(2)
const sineSamples = [];
for (let i = 0; i < 1000; i++) sineSamples.push(0.5 * Math.sin((i / 1000) * 2 * Math.PI * 20));
const sineRMS = computeRMS(sineSamples);
assert.ok(Math.abs(sineRMS - 0.5 / Math.sqrt(2)) < 0.01, `sine RMS should be ~0.354, got ${sineRMS}`);

// --- computeLoudnessScore ---
assert.strictEqual(computeLoudnessScore(0.005, 0.01, 0.3), 0, 'below noise floor should score 0');
assert.strictEqual(computeLoudnessScore(0.3, 0.01, 0.3), 1, 'at max expected should score 1');
assert.strictEqual(computeLoudnessScore(0.5, 0.01, 0.3), 1, 'above max expected should clamp to 1');
const midScore = computeLoudnessScore(0.155, 0.01, 0.3);
assert.ok(midScore > 0.4 && midScore < 0.6, `midpoint rms should give ~0.5 score, got ${midScore}`);

// --- updateAltitude ---
const config = { riseRate: 0.5, fallRate: 0.2, scoreThreshold: 0.4 };

// Sustained loud score should climb toward 1 over repeated steps and clamp there
let alt = 0;
for (let i = 0; i < 50; i++) alt = updateAltitude(alt, 0.9, 0.1, config);
assert.strictEqual(alt, 1, `sustained loud score should reach and clamp at altitude 1, got ${alt}`);

// Sustained quiet score should fall toward 0 and clamp there, never go negative
let alt2 = 1;
for (let i = 0; i < 50; i++) alt2 = updateAltitude(alt2, 0.0, 0.1, config);
assert.strictEqual(alt2, 0, `sustained quiet score should fall and clamp at altitude 0, got ${alt2}`);

// A single loud frame should raise altitude, a single quiet frame should lower it
const afterLoud = updateAltitude(0.5, 0.9, 0.1, config);
assert.ok(afterLoud > 0.5, 'one loud step should raise altitude');
const afterQuiet = updateAltitude(0.5, 0.0, 0.1, config);
assert.ok(afterQuiet < 0.5, 'one quiet step should lower altitude');

console.log('All rocket_logic tests passed.');
