import pyaudio
import numpy as np
from constants import INPUT_CHANNELS, INPUT_RATE, INPUT_CHUNK

class AudioRecorder:
    """
    Implements audio recording functionality using PyAudio.
    """
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        # Test if the audio input device is available
        try:
            stream = self.audio.open(format=self.format,
                                     channels=INPUT_CHANNELS,
                                     rate=INPUT_RATE,
                                     input=True,
                                     frames_per_buffer=INPUT_CHUNK)
            stream.close()
        except Exception as e:
            raise RuntimeError(f"Error initializing audio input: {e}")

    def record_audio(self, display_manager, trigger_key, pygame_module) -> np.ndarray:
        """
        Record audio while the specified trigger key is held down.
        Recording stops when the key is released.
        """
        display_manager.display_rec_start()
        stream = self.audio.open(format=self.format,
                                 channels=INPUT_CHANNELS,
                                 rate=INPUT_RATE,
                                 input=True,
                                 frames_per_buffer=INPUT_CHUNK)
        frames = []
        # Continue recording while the key is pressed.
        while True:
            pygame_module.event.pump()  # Process the event queue
            pressed = pygame_module.key.get_pressed()
            if pressed[trigger_key]:
                data = stream.read(INPUT_CHUNK)
                frames.append(data)
            else:
                break
        stream.stop_stream()
        stream.close()
        waveform = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) * (1/32768.0)
        return waveform

    def terminate(self):
        """
        Terminate the PyAudio instance.
        """
        self.audio.terminate() 