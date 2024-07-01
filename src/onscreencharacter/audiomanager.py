import os
import time
import pygame


class AudioManager:
    """
    Class for playing audio files using PyGame.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

        # Initialize pygame audio mixer
        pygame.mixer.init()

    def play(self, filename: str, delete_file: bool = True):
        if pygame.mixer.get_init() is None:
            self._log("Audio mixer was not initialized. Initializing audio mixer.")
            pygame.mixer.init()

        self._log(f"Playing {filename}")
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        self._log("Waiting for file to finish playing.")
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        self._log("File playing finished.")

        if delete_file:
            try:
                os.remove(filename)
                self._log(f"{filename} was deleted.")
            except Exception as e:
                self._log(f"{filename} could not be deleted. {e}")

    def _log(self, *args):
        if self.verbose:
            print("[AudioManager]", *args)
