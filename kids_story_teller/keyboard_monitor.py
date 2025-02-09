import pygame
import threading

class KeyboardMonitor:
    def __init__(self, trigger_key=pygame.K_SPACE):
        self.trigger_key = trigger_key
        self._recording = False
        self._lock = threading.Lock()

    def process_events(self):
        """
        Process pygame events and update the recording state.
        This method should be called periodically in the main loop.
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == self.trigger_key:
                with self._lock:
                    self._recording = True
            elif event.type == pygame.KEYUP and event.key == self.trigger_key:
                with self._lock:
                    self._recording = False

    def is_recording(self) -> bool:
        """
        Returns whether the trigger key is currently pressed.
        """
        with self._lock:
            return self._recording 