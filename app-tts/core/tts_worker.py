"""TTS worker thread. Owns the SAPI COM object — must create it inside run()."""

from __future__ import annotations

import threading

from PyQt6.QtCore import QThread, pyqtSignal


class TTSWorker(QThread):
    paragraph_started = pyqtSignal(int)   # paragraph index
    chapter_finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(
        self,
        paragraphs: list[str],
        rate: int = 6,
        volume: int = 100,
        voice_name: str = "Zira",
        start_index: int = 0,
    ):
        super().__init__()
        self._paragraphs = paragraphs
        self._rate = rate
        self._volume = volume
        self._voice_name = voice_name
        self._start_index = start_index

        self._stop = False
        self._pause_event = threading.Event()
        self._pause_event.set()  # set = running, clear = paused

        # Written from main thread, read by worker — use lock for rate/volume
        self._lock = threading.Lock()
        self._pending_rate: int | None = None
        self._pending_volume: int | None = None

    # ------------------------------------------------------------------
    # Public control API (called from main thread)
    # ------------------------------------------------------------------

    def pause(self) -> None:
        self._pause_event.clear()
        if self._speaker is not None:
            try:
                self._speaker.Pause()
            except Exception:
                pass

    def resume(self) -> None:
        if self._speaker is not None:
            try:
                self._speaker.Resume()
            except Exception:
                pass
        self._pause_event.set()

    def stop(self) -> None:
        self._stop = True
        self._pause_event.set()  # unblock if paused
        if self._speaker is not None:
            try:
                self._speaker.Skip("Sentence", 1000)
            except Exception:
                pass

    def set_rate(self, rate: int) -> None:
        with self._lock:
            self._pending_rate = rate

    def set_volume(self, volume: int) -> None:
        with self._lock:
            self._pending_volume = volume

    # ------------------------------------------------------------------
    # Thread entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        # COM object MUST be created on this thread
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception as e:
            self.error.emit(f"SAPI init failed: {e}")
            return

        self._speaker = speaker

        # Select voice
        try:
            voices = speaker.GetVoices()
            for i in range(voices.Count):
                if self._voice_name.lower() in voices.Item(i).GetDescription().lower():
                    speaker.Voice = voices.Item(i)
                    break
        except Exception:
            pass

        speaker.Rate = self._rate
        speaker.Volume = self._volume

        try:
            for idx in range(self._start_index, len(self._paragraphs)):
                if self._stop:
                    break

                # Apply any pending rate/volume changes
                with self._lock:
                    if self._pending_rate is not None:
                        speaker.Rate = self._pending_rate
                        self._pending_rate = None
                    if self._pending_volume is not None:
                        speaker.Volume = self._pending_volume
                        self._pending_volume = None

                self.paragraph_started.emit(idx)

                para = self._paragraphs[idx]
                speaker.Speak(para, 1)  # 1 = SVSFlagsAsync

                # Poll until done, checking stop/pause each 100ms
                while True:
                    if self._stop:
                        break
                    done = speaker.WaitUntilDone(100)
                    if done:
                        break
                    # Check pause
                    if not self._pause_event.is_set():
                        # Already called speaker.Pause() in pause()
                        self._pause_event.wait()  # blocks until resume()
                        # After resume, speaker.Resume() was called before set()

                if self._stop:
                    break

            if not self._stop:
                self.chapter_finished.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._speaker = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    _speaker = None  # class-level default so pause/resume are safe before run()


def get_available_voices() -> list[str]:
    """Query SAPI for installed voice names. Call from main thread at startup."""
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = speaker.GetVoices()
        return [voices.Item(i).GetDescription() for i in range(voices.Count)]
    except Exception:
        return []
