"""
Shared contract for all phoneme feature extractors.

Mirrors BreathQuest's AudioEngine breath-value convention on purpose: that engine
returns a single normalized 0-1 value per audio frame that drives the game's
visual feedback (kite height, rocket thrust, etc). Every extractor here returns
the same shape, so integrating into BreathQuest's game loop is a drop-in swap of
"generic breath value" -> "phoneme-specific score" rather than a rewrite.
"""

from dataclasses import dataclass, field


@dataclass
class FeatureResult:
    """
    score: 0.0-1.0 normalized value that drives the on-screen mechanic directly
           (equivalent to BreathQuest's live breath-bar value).
    is_valid_attempt: whether this frame counts as a genuine attempt at the
           target sound at all (helps the game distinguish silence/noise from
           an actual attempt that just scored low).
    raw_features: diagnostic values specific to this phoneme, not used by the
           game mechanic directly but consumed by the DRL agent's state and
           useful for therapist-facing analytics.
    """
    score: float
    is_valid_attempt: bool
    raw_features: dict = field(default_factory=dict)
