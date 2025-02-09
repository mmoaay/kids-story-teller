import numpy as np
import pyaudio

# Configuration parameters (adjust as needed)
INPUT_CHANNELS = 1
INPUT_RATE = 16000
INPUT_CHUNK = 1024

class AudioRecorder:
    """
    Implements audio recording functionality using PyAudio.
    """
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.stream = None
        # Test if the audio input device is available
        try:
            self._open_stream()
            self.stream.close()
        except Exception as e:
            raise RuntimeError(f"Error initializing audio input: {e}")

    def _open_stream(self):
        self.stream = self.audio.open(
            format=self.format,
            channels=INPUT_CHANNELS,
            rate=INPUT_RATE,
            input=True,
            frames_per_buffer=INPUT_CHUNK
        )

    def record_audio(self, should_continue_fn, display_energy_callback=None) -> np.ndarray:
        """
        Record audio data. Continue recording as long as should_continue_fn() returns True.

        Parameters:
            should_continue_fn: A callback function that returns a boolean to determine whether to continue recording.
            display_energy_callback: Optional callable that receives the current sound energy. This can be used
                                     to update a volume display (e.g. via DisplayManager.display_sound_energy).

        Returns:
            np.ndarray: Recorded audio data (normalized float32 array).
        """
        self._open_stream()
        frames = []
        while should_continue_fn():
            try:
                data = self.stream.read(INPUT_CHUNK, exception_on_overflow=False)
            except Exception as e:
                print(f"Error reading audio data: {e}")
                break

            # Calculate normalized RMS energy for the current audio chunk
            raw = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            normalized = raw / 32768.0
            rms = np.sqrt(np.mean(normalized ** 2))
            # Call the display energy callback if provided
            if display_energy_callback is not None:
                display_energy_callback(rms)

            frames.append(data)
        self.stream.stop_stream()
        self.stream.close()
        waveform = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) * (1/32768.0)
        return waveform

    def terminate(self):
        """
        Clean up audio resources.
        """
        self.audio.terminate() 