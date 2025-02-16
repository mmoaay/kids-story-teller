import pygame
import threading

class KeyboardMonitor:
    def __init__(self, trigger_key):
        self.trigger_key = trigger_key
        self._is_recording = False

    def process_events(self, event):
        """
        Directly process a single pygame event to update the recording state.
        This method no longer polls the event queue on its own.
        """
        if event.type == pygame.KEYDOWN and event.key == self.trigger_key:
            self._is_recording = True
        elif event.type == pygame.KEYUP and event.key == self.trigger_key:
            self._is_recording = False

    def is_recording(self):
        return self._is_recording 