import pyttsx3

class TTSManager:
    """
    Manages text-to-speech conversion.
    """
    def __init__(self):
        self.engine = pyttsx3.init()

    def speak(self, text: str):
        """
        Convert text to speech and print it to the console.
        """
        print(text)
        self.engine.say(text)
        self.engine.runAndWait() 