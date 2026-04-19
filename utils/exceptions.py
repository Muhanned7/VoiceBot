class VoiceBotError(Exception):
    """Base class for all VoiceBot errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
class ASRError(VoiceBotError):
    """Raised when anything in the speech-to-text pipeline fails."""

class UnsupportedAudioFormat(ASRError):
    """Raised when the uploaded file is not a supported format."""

class AudioTooShort(ASRError):
    """Raised when the audio clip is too short to transcribe."""

class TranscriptionEmpty(ASRError):
    """Raised when Whisper returns an empty string."""


# --- Intent Exceptions ---

class IntentError(VoiceBotError):
    """Raised when anything in the intent classification pipeline fails."""

class ModelNotLoaded(IntentError):
    """Raised when the classifier is called before load() is called."""

class LowConfidenceIntent(IntentError):
    """
    Raised when the top predicted intent scores below the confidence threshold.
    Caller should return the fallback response instead.
    """
    def __init__(self, predicted_intent: str, confidence: float):
        super().__init__(
            f"Low confidence: '{predicted_intent}' scored {confidence:.2f}"
        )
        self.predicted_intent = predicted_intent
        self.confidence = confidence