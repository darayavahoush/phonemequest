"""
Phoneme-specific audio feature extractors for PhonemeQuest.

Each module exposes a single extract(audio_chunk, sample_rate) -> FeatureResult
function. See common.py for the shared FeatureResult contract, which mirrors
BreathQuest's AudioEngine breath-value convention so these drop into the
existing game loop as a swap-in, not a rewrite.

Level -> extractor -> BreathQuest engine it reuses:
  aa  -> vowel_loudness   -> Float Rider
  oo  -> vowel_quality    -> Balloon Pop
  ma  -> syllable_rhythm  -> Dandelion Storm
  fa  -> frication        -> Dragon Fire
  ha  -> aspiration_burst -> Candle Gauntlet
  word -> word_level/asr_match.py (net new, no BreathQuest equivalent)
"""

from .common import FeatureResult
from . import vowel_loudness, vowel_quality, syllable_rhythm, frication, aspiration_burst

EXTRACTORS = {
    "aa": vowel_loudness.extract,
    "oo": vowel_quality.extract,
    "ma": syllable_rhythm.extract,
    "fa": frication.extract,
    "ha": aspiration_burst.extract,
}

__all__ = ["FeatureResult", "EXTRACTORS", "vowel_loudness", "vowel_quality",
           "syllable_rhythm", "frication", "aspiration_burst"]
