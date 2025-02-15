"""
TTS Manager using gTTS.

Dependencies:
- gTTS: Google Text-to-Speech. Recommended version: gTTS==2.2.3. Install with:
    pip install gTTS==2.2.3
- playsound: Recommended version: playsound==1.2.2. Install with:
    pip install playsound==1.2.2

This module uses the gTTS library to synthesize speech from text and plays the generated audio.
It attempts to mimic a male voice by specifying the 'tld' parameter as 'co.uk', although the gender cannot be explicitly controlled.
"""

try:
    from gtts import gTTS
except ImportError as e:
    raise ImportError("gTTS dependency is required. Please install it via 'pip install gTTS==2.2.3'") from e

import tempfile
import os

try:
    from playsound import playsound
except ImportError as e:
    raise ImportError("playsound dependency is required. Please install it via 'pip install playsound==1.2.2'") from e

class TTSManager:
    """
    Text-to-Speech manager using gTTS for converting text to speech.
    Attempts to use a male voice by specifying the 'tld' parameter as 'co.uk' to hint at a British accent.
    """
    def speak(self, text: str):
        """
        Convert text to speech using gTTS with a male voice heuristic, print the text, and play the generated audio.
        """
        print(text)
        try:
            # Create a temporary MP3 file for the speech output.
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                tts = gTTS(text=text, lang='en', tld='co.uk')
                tts.save(fp.name)
                playsound(fp.name)
        except Exception as e:
            print(f"Error in TTS: {e}")