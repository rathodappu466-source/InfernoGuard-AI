"""
Sound alert module for InfernoGuard AI.

Plays an alarm audio file in a non-blocking daemon thread using pygame.mixer.
"""

import threading

from utils.logger import get_logger

logger = get_logger(__name__)


def play_alarm(audio_path: str) -> None:
    """
    Play the alarm audio file in a background daemon thread.

    The thread is daemonized so it does not block application shutdown.
    Failures are caught and logged without propagating.

    Args:
        audio_path: Absolute or relative path to the alarm MP3/WAV file.
    """
    def _play():
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            # Block the thread until playback finishes
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as exc:
            logger.error("Sound alert failed: %s", exc, exc_info=True)

    thread = threading.Thread(target=_play, daemon=True)
    thread.start()
