# Kids Story Teller

A kids' story teller application that leverages Whisper for offline speech recognition and interacts with a local instance of the Ollama API for generating text responses. This application combines several technologies:
- **Speech Recognition:** Uses [Whisper](https://github.com/openai/whisper) for converting speech to text.
- **Language Processing:** Integrates with [Ollama](https://ollama.ai/) for generating language responses.
- **Text-to-Speech:** Employs [pyttsx3](https://pypi.org/project/pyttsx3/) for converting text to audible speech.
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
│   └── tts_manager.py           # Text-to-Speech module (using pyttsx3)
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

*Note:* Ensure that the icon file `kids_story_teller.png` is available in the expected location or update the icon path in `kids_story_teller.py` accordingly.

## Prerequisites

- **CUDA:** If you plan to run Whisper on a GPU, make sure you have the appropriate CUDA drivers and libraries installed.
- **Ollama:** Ensure that the Ollama server is installed and running locally.

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
- [pyttsx3](https://pypi.org/project/pyttsx3/)
- [Pygame](https://www.pygame.org/)