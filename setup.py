from setuptools import setup, find_packages

setup(
    name="kids-story-teller",
    version="0.1.0",
    description="Kids Story Teller application using Whisper and the Ollama API",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pygame",
        "pyaudio",
        "whisper",
        "pyttsx3",
        "requests",
        "pyyaml",
        "torch",  # required if using GPU acceleration
        "numpy"
    ],
    entry_points={
        'console_scripts': [
            'kids-story-teller=kids_story_teller.kids_story_teller:main',
        ],
    },
) 