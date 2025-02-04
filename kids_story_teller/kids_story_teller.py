import sys
import pygame
import pygame.locals

from config import Config
from display_manager import DisplayManager
from audio_recorder import AudioRecorder
from speech_recognizer import SpeechRecognizer
from tts_manager import TTSManager
from ollama_client import OllamaClient
from constants import INPUT_CONFIG_PATH

class KidsStoryTeller:
    """
    Main controller class that integrates all modules for the kids' story teller.
    """
    def __init__(self, config_path=INPUT_CONFIG_PATH):
        # Load configuration settings.
        self.config = Config(config_path)

        # Initialize Pygame and the display manager.
        pygame.init()
        self.display_manager = DisplayManager()
        self.display_manager.set_icon("kids_story_teller.png")  # 可根据需要修改图标文件

        # Initialize the Text-to-Speech manager.
        self.tts_manager = TTSManager()

        # Initialize the audio recorder; exit if an error occurs.
        try:
            self.audio_recorder = AudioRecorder()
        except RuntimeError as e:
            print(e)
            self.wait_exit()

        # Display a loading message and speak it while loading the Whisper model.
        self.display_manager.display_message(self.config.messages.loadingModel)
        self.tts_manager.speak(self.config.messages.loadingModel)
        self.speech_recognizer = SpeechRecognizer(self.config.whisper_recognition.modelPath,
                                                  self.config.whisper_recognition.lang)

        # Initialize the Ollama API client.
        self.ollama_client = OllamaClient(self.config.ollama.url,
                                          self.config.ollama.model,
                                          self.config.conversation.context)
        # Initialize the conversation context.
        self.conversation_context = []

        # Greet the user.
        self.tts_manager.speak(self.config.conversation.greeting)
        self.display_manager.display_message(self.config.messages.pressSpace)

    def wait_exit(self):
        """
        Display an error message and wait for the user to exit.
        """
        while True:
            self.display_manager.display_message(self.config.messages.noAudioInput)
            self.display_manager.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    self.shutdown()

    def shutdown(self):
        """
        Clean up resources and exit the application.
        """
        self.audio_recorder.terminate()
        pygame.quit()
        sys.exit()

    def run(self):
        """
        Main event loop: listens for key presses, records audio, performs speech recognition,
        interacts with the Ollama API, and handles exit events.
        """
        push_to_talk_key = pygame.K_SPACE
        while True:
            self.display_manager.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == push_to_talk_key:
                    # Record audio.
                    waveform = self.audio_recorder.record_audio(self.display_manager, push_to_talk_key, pygame)
                    # Convert the audio to text using the speech recognizer.
                    recognized_text = self.speech_recognizer.speech_to_text(waveform)
                    self.tts_manager.speak(recognized_text)
                    # Send the recognized text to the Ollama API.
                    self.ollama_client.ask(recognized_text, self.conversation_context, self._ollama_callback)
                    self.display_manager.display_message(self.config.messages.pressSpace)
                if event.type == pygame.locals.QUIT:
                    self.shutdown()

    def _ollama_callback(self, text: str):
        """
        Callback function to process responses from the Ollama API.
        """
        self.tts_manager.speak(text)
        self.display_manager.display_message(text)


def main():
    """
    Entry point of the Kids Story Teller application.
    """
    # Warn users if the Python version is below 3.9.
    if sys.version_info < (3, 9):
        print("Warning: This application is recommended to run on Python 3.9 or higher.")
    app = KidsStoryTeller()
    app.run()


if __name__ == "__main__":
    main() 