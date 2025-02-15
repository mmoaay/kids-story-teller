# Kids Story Teller

A kids' story teller application that leverages Whisper for offline speech recognition, interacts with a local instance of the Ollama API for generating text responses, and uses a locally installed Stable Diffusion model for image generation. This application combines several technologies:
- **Speech Recognition:** Uses [Whisper](https://github.com/openai/whisper) for converting speech to text.
- **Language Processing:** Integrates with [Ollama](https://ollama.ai/) for generating language responses.
- **Image Generation:** Utilizes a Stable Diffusion model through the [diffusers](https://huggingface.co/docs/diffusers/index) library with a cancellation mechanism to ensure that if a new image generation request arrives, the previous one is canceled.
- **Text-to-Speech:** Uses [gTTS](https://gtts.readthedocs.io/) for converting text to audible speech.
- **Graphical Interface:** Uses [Pygame](https://www.pygame.org/) for a basic visual interface.
- **Configuration Management:** Supports YAML-based configuration for easy customization.

## Project Structure

The project is organized as follows:

```
kids-story-teller/
│
├── LICENSE
├── README.md              # This file
├── requirements.txt       # Third-party dependencies
├── setup.py               # Packaging and installation script
│
├── kids_story_teller/     # Main source package
│   ├── __init__.py
│   ├── kids_story_teller.py   # Main controller and entry point
│   ├── audio_recorder.py        # Audio recording module
│   ├── config.py                # Configuration management via YAML
│   ├── constants.py             # Global constants
│   ├── display_manager.py       # Display and drawing module (using Pygame)
│   ├── ollama_client.py         # Interacts with the Ollama API
│   ├── speech_recognizer.py     # Speech recognition using Whisper
│   ├── tts_manager.py           # Text-to-Speech module (using gTTS)
│   └── stable_diffusion_generator.py   # Image generation via Stable Diffusion with cancellation support
│
└── tests/                 # Unit tests
    ├── __init__.py
    └── test_basic.py
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/kids-story-teller.git
   ```

2. **Navigate to the Project Directory:**

   ```bash
   cd kids-story-teller
   ```

3. **Install the Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Install the Project as a Package:**

   ```bash
   pip install -e .
   ```

## Usage

You can run the application using one of the following methods:

- **Directly via Python module:**

  ```bash
  python -m kids_story_teller.kids_story_teller
  ```

- **Using the Command-Line Script (if installed via setup.py):**

  ```bash
  kids-story-teller
  ```

For image generation, the system employs a cancellation mechanism so that if a new image generation request starts while a previous one is processing, the previous one will be cancelled.

*Note:* Ensure that assets such as model files or icon files are available in the expected locations or update the paths accordingly in the code.

## Prerequisites

- **CUDA:** If you plan to run Whisper on a GPU, ensure that you have the appropriate CUDA drivers and libraries installed.
- **Ollama:** Make sure the Ollama server is installed and running locally.
- **Stable Diffusion & diffusers:** For image generation, ensure the corresponding model and requirements are available. A GPU or Apple M-series chip (using MPS) might be required for optimal performance.

## Testing

Run the unit tests using [pytest](https://docs.pytest.org/):

```bash
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open pull requests or open issues to help improve this project.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Ollama](https://ollama.ai/)
- [gTTS](https://gtts.readthedocs.io/)
- [Pygame](https://www.pygame.org/)
- [diffusers](https://huggingface.co/docs/diffusers/index)