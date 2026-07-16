"""
word level — whole-word intelligibility, via ASR.

The one level with no BreathQuest equivalent to reuse. Wraps faster-whisper
(already deployed in VaakSiddhi) rather than adding a second STT dependency.

TODO: swap in the actual faster-whisper model call once merged — this stub
defines the interface so the rest of the pipeline (schemas, agent state) can
be built against it now without needing the model loaded locally.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class WordMatchResult:
    transcript: str
    confidence: float          # ASR confidence, 0.0-1.0
    match_score: float         # similarity to target word, 0.0-1.0
    is_valid_attempt: bool


def score_word_attempt(transcript: str, target_word: str, asr_confidence: float) -> WordMatchResult:
    """
    Call this with faster-whisper's output once integrated:
        segments, info = whisper_model.transcribe(audio_path)
        transcript = segments[0].text
        asr_confidence = ... (derive from segment.avg_logprob or similar)
    """
    if not transcript.strip():
        return WordMatchResult(transcript="", confidence=0.0, match_score=0.0, is_valid_attempt=False)

    similarity = SequenceMatcher(None, transcript.strip().lower(), target_word.strip().lower()).ratio()
    return WordMatchResult(
        transcript=transcript,
        confidence=asr_confidence,
        match_score=similarity,
        is_valid_attempt=True,
    )
