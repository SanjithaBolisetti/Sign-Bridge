class SignAvatarService:
    """Service wrapper for text-to-sign avatar generation."""

    def text_to_sign(self, text: str):
        # TODO: Integrate Whisper (or ASR) pipeline if needed for speech-to-text
        # TODO: Map text tokens to MediaPipe landmark dictionary for avatar animation
        # TODO: Build 3D coordinate mapping for avatar rigging
        words = text.split() if text else []
        return {
            "words": words or ["HELLO"],
            "animation_data": [],
        }
