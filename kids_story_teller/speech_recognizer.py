import whisper
import torch

class SpeechRecognizer:
    """
    Uses the Whisper model to perform speech-to-text conversion.
    """
    def __init__(self, model_path: str, language: str):
        # Load the Whisper model from the specified path.
        self.model = whisper.load_model(model_path)
        self.language = language

    def speech_to_text(self, waveform) -> str:
        """
        Convert an audio waveform to text using the Whisper model.
        """
        transcript = self.model.transcribe(waveform, language=self.language, fp16=torch.cuda.is_available())
        text = transcript.get("text", "")
        return text 