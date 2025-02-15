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
from stable_diffusion_generator import StableDiffusionImageGenerator

class KidsStoryTeller:
    """
    Main controller that integrates independent modules:
    Display, audio recording, keyboard monitoring, speech recognition, TTS, and API calls.
    """
    def __init__(self, config_path=INPUT_CONFIG_PATH):
        # Load configuration settings.
        self.config = Config(config_path)

        # Initialize Pygame and the DisplayManager.
        pygame.init()
        self.display_manager = DisplayManager()
        # Set the window icon (retained as per request)
        self.display_manager.set_icon("kids_story_teller.png")
        self.display_manager.set_top_image("default_top_image.jpeg")

        # Initialize the TTS manager.
        self.tts_manager = TTSManager()

        # Greet the user.
        self.display_manager.set_message(self.config.messages.pressSpace)
        # Disabled speech invocation:
        self.tts_manager.speak(self.config.conversation.greeting)
        
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

        # Initialize the stable diffusion image generator.
        self.sd_image_generator = StableDiffusionImageGenerator(
            modelName=self.config.stablediffusion.modelName, 
            device=self.config.stablediffusion.device
        )

        # Initialize the keyboard monitor with the trigger key (here, using the SPACE key).
        self.keyboard_monitor = KeyboardMonitor(trigger_key=pygame.K_SPACE)

    def wait_exit(self):
        """
        Display an error message and wait for the user to quit.
        """
        while True:
            self.display_manager.set_message(self.config.messages.noAudioInput)
            self.display_manager.draw()
            self.display_manager.tick(60)

            # Process all events; check for quit event.
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
        Process audio recording and speech recognition. Once text is recognized,
        spawn two separate threads:
          - One for the Ollama API call.
          - One for generating an image using Stable Diffusion.
        """
        waveform = self.audio_recorder.record_audio(
            should_continue_fn=self.keyboard_monitor.is_recording,
            display_energy_callback=self.display_manager.set_energy
        )
        recognized_text = self.speech_recognizer.speech_to_text(waveform)

        self.display_manager.set_message(self.config.conversation.llmWaitMsg + recognized_text)
        # Disabled TTS speech invocation:
        self.tts_manager.speak(self.config.conversation.llmWaitMsg + recognized_text)

        # Start two separate threads.
        ollama_thread = threading.Thread(
            target=self._ollama_thread_func, args=(recognized_text,), daemon=True
        )
        stable_diffusion_thread = threading.Thread(
            target=self._stable_diffusion_thread_func, args=(recognized_text,), daemon=True
        )
        ollama_thread.start()
        stable_diffusion_thread.start()

        self.display_manager.set_message(self.config.messages.pressSpace)

    def _ollama_thread_func(self, recognized_text: str):
        """
        Thread function for invoking the Ollama API.
        """
        self.ollama_client.ask(recognized_text, self.conversation_context, self._ollama_callback)

    def _stable_diffusion_thread_func(self, recognized_text: str):
        """
        Thread function for generating an image using the Stable Diffusion model.
        The generated image is then displayed in the top area.
        """
        try:
            # Generate an image using the recognized text as a prompt.
            image = self.sd_image_generator.generate_image(recognized_text)
            # Update the top image in the display manager with the generated image.
            self.display_manager.set_top_image(image)
        except Exception as e:
            print(f"Stable diffusion generation failed: {e}")

    def run(self):
        """
        Main event loop which:
         - Processes events including keyboard input and quit events.
         - Forwards events to the DisplayManager for UI interactions.
         - Records audio via the AudioRecorder when the keyboard trigger is active.
         - Processes speech recognition and spawns separate threads for API calls and image generation.
        """
        already_recording = False

        while True:
            self.display_manager.tick(60)
            
            # Get and process all events once.
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.shutdown()
                # Forward events to the DisplayManager (which in turn delegates to the bottom toolbar)
                self.display_manager.handle_event(event)

                # Update keyboard state.
                self.keyboard_monitor.handle_event(event)

            # Start a recording thread if the trigger key is pressed and no recording is happening.
            if self.keyboard_monitor.is_recording() and not already_recording:
                self.display_manager.set_message(self.config.conversation.recognitionWaitMsg)
                already_recording = True
                threading.Thread(
                    target=self.handle_push_to_talk, daemon=True
                ).start()
            elif not self.keyboard_monitor.is_recording():
                already_recording = False

            self.display_manager.draw()
            self.display_manager.tick(60)

    def _ollama_callback(self, text: str):
        """
        Process the response text from the Ollama API by updating the display.
        """
        self.display_manager.set_message(text)
        # Disabled TTS speech invocation:
        self.tts_manager.speak(text)

def main():
    """
    The entry point for the Kids Story Teller application.
    """
    if sys.version_info < (3, 9):
        print("Warning: This application is recommended to run on Python 3.9 or higher.")
    app = KidsStoryTeller()
    app.run()

if __name__ == "__main__":
    main() 