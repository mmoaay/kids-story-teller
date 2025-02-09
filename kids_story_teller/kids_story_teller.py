import warnings
import multiprocessing.resource_tracker as resource_tracker

# Monkey patch: Ignore registration of semaphore resources so they are not tracked.
_original_register = resource_tracker.register
def _ignore_semaphore_register(name, rtype):
    if rtype == 'semaphore':
        return  # Do not register semaphore resources
    return _original_register(name, rtype)
resource_tracker.register = _ignore_semaphore_register

# Filter out resource_tracker warnings related to leaked semaphore objects.
warnings.filterwarnings("ignore", message="resource_tracker: There appear to be", category=UserWarning)

import sys
import threading
import pygame
import pygame.locals

from config import Config
from display_manager import DisplayManager
from audio_recorder import AudioRecorder
from keyboard_monitor import KeyboardMonitor
from speech_recognizer import SpeechRecognizer
from tts_manager import TTSManager
from ollama_client import OllamaClient
from constants import INPUT_CONFIG_PATH

class KidsStoryTeller:
    """
    Main controller that integrates independent modules:
    Display, audio recording, keyboard monitoring, speech recognition, TTS, and API calls.
    """
    def __init__(self, config_path=INPUT_CONFIG_PATH):
        # Load configuration settings.
        self.config = Config(config_path)

        # Initialize Pygame and the DisplayManager, and set the application icon.
        pygame.init()
        self.display_manager = DisplayManager()
        self.display_manager.set_icon("kids_story_teller.png")  # Change the icon file as needed

        # Example usage in your main loop
        left_images = [pygame.image.load("kids_story_teller.png"), pygame.image.load("kids_story_teller.png")]
        right_images = [pygame.image.load("kids_story_teller.png"), pygame.image.load("kids_story_teller.png")]

        # In your event loop or update routine:
        self.display_manager.create_image_sliders(left_images, right_images)

        # Initialize the TTS manager.
        self.tts_manager = TTSManager()

        # Initialize the audio recording module; exit if an error occurs.
        try:
            self.audio_recorder = AudioRecorder()
        except RuntimeError as e:
            print(e)
            self.wait_exit()

        # Initialize the speech recognizer.
        self.speech_recognizer = SpeechRecognizer(
            self.config.whisper_recognition.modelPath,
            self.config.whisper_recognition.lang
        )

        # Initialize the Ollama API client.
        self.ollama_client = OllamaClient(
            self.config.ollama.url,
            self.config.ollama.model,
            self.config.conversation.context
        )
        self.conversation_context = []

        # Initialize the keyboard monitor with the trigger key (here, the SPACE key).
        self.keyboard_monitor = KeyboardMonitor(trigger_key=pygame.K_SPACE)

        # Greet the user.
        self.display_manager.display_message(self.config.messages.pressSpace)
        self.tts_manager.speak(self.config.conversation.greeting)
        

    def wait_exit(self):
        """
        Display an error message and wait for the user to quit.
        """
        while True:
            self.display_manager.display_message(self.config.messages.noAudioInput)
            self.display_manager.tick(60)

            # Check for quit events using peek so the KeyboardMonitor doesn't consume them.
            if pygame.event.peek(pygame.QUIT):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.shutdown()

    def shutdown(self):
        """
        Clean up resources and exit the program.
        """
        self.audio_recorder.terminate()
        pygame.quit()
        sys.exit()

    def handle_push_to_talk(self):
        """
        Process audio recording, speech recognition, and API calls in a background thread.
        The recording duration is controlled by the external keyboard events via keyboard_monitor.is_recording.
        """

        waveform = self.audio_recorder.record_audio(
            should_continue_fn=self.keyboard_monitor.is_recording,
            display_energy_callback=self.display_manager.display_sound_energy
        )
        recognized_text = self.speech_recognizer.speech_to_text(waveform)

        self.display_manager.display_message(self.config.conversation.llmWaitMsg + recognized_text)
        self.tts_manager.speak(self.config.conversation.llmWaitMsg + recognized_text)

        self.ollama_client.ask(recognized_text, self.conversation_context, self._ollama_callback)
        self.display_manager.display_message(self.config.messages.pressSpace)

    def run(self):
        """
        Main event loop:
         - Uses KeyboardMonitor to listen for the trigger key.
         - Records audio via AudioRecorder (recording time is controlled by the keyboard state).
         - Processes speech recognition, TTS, and Ollama API calls.
         - Handles quit events.
        """
        # Flag to avoid repeatedly starting the recording thread.
        already_recording = False

        while True:
            self.display_manager.tick(60)

            # Pre-check for quit events.
            if pygame.event.peek(pygame.QUIT):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.shutdown()

            # Update keyboard state.
            self.keyboard_monitor.process_events()

            # When the trigger key is pressed, start a new recording thread (avoiding repeated starts).
            if self.keyboard_monitor.is_recording() and not already_recording:
                
                self.display_manager.display_message(self.config.conversation.recognitionWaitMsg)

                already_recording = True
                # Set daemon=True so that the thread won't block application exit.
                threading.Thread(
                    target=self.handle_push_to_talk, daemon=True
                ).start()
            elif not self.keyboard_monitor.is_recording():
                already_recording = False

    def _ollama_callback(self, text: str):
        """
        Process the text returned from the Ollama API by speaking it and updating the display.
        """
        self.display_manager.display_message(text)
        self.tts_manager.speak(text)
        


def main():
    """
    Entry point for the Kids Story Teller application.
    """
    if sys.version_info < (3, 9):
        print("Warning: This application is recommended to run on Python 3.9 or higher.")
    app = KidsStoryTeller()
    app.run()


if __name__ == "__main__":
    main() 