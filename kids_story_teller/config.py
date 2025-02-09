import yaml
from yaml import Loader

class Config:
    """
    Configuration class: Loads default settings and overrides them with an external YAML configuration.
    """
    def __init__(self, config_path: str):
        # Default configuration options
        self.messages = type("Messages", (), {})()
        self.messages.pressSpace = "Press the space key to begin speaking and then release it."
        self.messages.loadingModel = "Loading model..."
        self.messages.noAudioInput = "Error: No audio input."

        self.whisper_recognition = type("WhisperRecognition", (), {})()
        self.whisper_recognition.modelPath = "whisper/large-v3.pt"
        self.whisper_recognition.lang = "en"

        self.ollama = type("OllamaConfig", (), {})()
        self.ollama.url = "http://localhost:11434/api/generate"
        self.ollama.model = 'deepseek-r1:7b'

        self.stablediffusion = type("StableDiffusionConfig", (), {})()
        self.stablediffusion.modelName = "CompVis/stable-diffusion-v1-4"
        self.stablediffusion.device = "cpu"

        self.conversation = type("Conversation", (), {})()
        self.conversation.context = "This is a discussion in English.\n"
        self.conversation.greeting = "I am listening to you."
        self.conversation.recognitionWaitMsg = "Yes."
        self.conversation.llmWaitMsg = "Let me think."

        # Attempt to load external configuration from a YAML file to override defaults
        try:
            with open(config_path, 'r', encoding="utf-8") as stream:
                external_config = yaml.load(stream, Loader=Loader)
            self._apply_overrides(external_config)
        except Exception as e:
            print(f"Failed to load config file {config_path}: {e}")

    def _apply_overrides(self, config_overrides: dict):
        """
        Override default configuration values with the values from the YAML file.
        """
        for section, overrides in config_overrides.items():
            if hasattr(self, section):
                section_obj = getattr(self, section)
                for key, value in overrides.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
                    else:
                        print(f"Ignoring unknown setting: {key} in {section}")
            else:
                print("Ignoring unknown setting:", section) 