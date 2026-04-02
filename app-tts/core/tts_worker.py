"""TTS worker thread — WinRT SpeechSynthesizer + sounddevice playback."""

from __future__ import annotations

import io
import threading
import wave

import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QThread, pyqtSignal

import winrt._winrt as _winrt
from winrt.windows.media.speechsynthesis import SpeechSynthesizer
from winrt.windows.storage.streams import DataReader

CHUNK = 2048


def _map_rate(rate: int) -> float:
    """Slider -10..+10 → speaking_rate 0.5..2.0."""
    return 0.5 + (rate + 10) / 20.0 * 1.5


class TTSWorker(QThread):
    paragraph_started = pyqtSignal(int)   # paragraph index
    chapter_finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(
        self,
        paragraphs: list[str],
        rate: int = 6,
        volume: int = 100,
        voice_name: str = "",
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

        self._lock = threading.Lock()
        self._pending_rate: int | None = None
        self._pending_volume: int | None = None

    # ------------------------------------------------------------------
    # Public control API (called from main thread)
    # ------------------------------------------------------------------

    def pause(self) -> None:
        self._pause_event.clear()

    def resume(self) -> None:
        self._pause_event.set()

    def stop(self) -> None:
        self._stop = True
        self._pause_event.set()  # unblock any wait()

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
        _winrt.init_apartment(_winrt.MTA)
        try:
            self._run_inner()
        finally:
            _winrt.uninit_apartment()

    def _run_inner(self) -> None:
        try:
            synth = SpeechSynthesizer()
        except Exception as e:
            self.error.emit(f"WinRT SpeechSynthesizer init failed: {e}")
            return

        # Select voice
        if self._voice_name:
            try:
                voices = SpeechSynthesizer.all_voices
                for v in voices:
                    if self._voice_name.lower() in v.display_name.lower():
                        synth.voice = v
                        break
            except Exception:
                pass

        # Apply initial rate/volume
        try:
            synth.options.speaking_rate = _map_rate(self._rate)
            synth.options.audio_volume = self._volume / 100.0
        except Exception:
            pass

        try:
            for idx in range(self._start_index, len(self._paragraphs)):
                if self._stop:
                    break

                para = self._paragraphs[idx]
                if not para.strip():
                    continue

                # Apply any pending rate/volume changes
                with self._lock:
                    if self._pending_rate is not None:
                        try:
                            synth.options.speaking_rate = _map_rate(self._pending_rate)
                        except Exception:
                            pass
                        self._pending_rate = None
                    if self._pending_volume is not None:
                        try:
                            synth.options.audio_volume = self._pending_volume / 100.0
                        except Exception:
                            pass
                        self._pending_volume = None

                self.paragraph_started.emit(idx)

                # Synthesize to WAV stream (blocking)
                try:
                    stream = synth.synthesize_text_to_stream_async(para).get()
                    size = stream.size
                    reader = DataReader(stream.get_input_stream_at(0))
                    reader.load_async(size).get()
                    buf = bytearray(size)
                    reader.read_bytes(buf)
                    reader.close()
                    stream.close()
                except Exception as e:
                    self.error.emit(f"Synthesis error: {e}")
                    return

                # Decode WAV
                try:
                    with wave.open(io.BytesIO(bytes(buf))) as wf:
                        n_channels = wf.getnchannels()
                        sample_rate = wf.getframerate()
                        raw = wf.readframes(wf.getnframes())
                except Exception as e:
                    self.error.emit(f"WAV decode error: {e}")
                    return

                pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                if n_channels > 1:
                    pcm = pcm.reshape(-1, n_channels)

                # Chunk playback with pause/resume
                try:
                    with sd.OutputStream(
                        samplerate=sample_rate,
                        channels=n_channels,
                        dtype="float32",
                        blocksize=CHUNK,
                    ) as out:
                        pos = 0
                        while pos < len(pcm):
                            if self._stop:
                                break
                            if not self._pause_event.is_set():
                                out.stop()
                                self._pause_event.wait()
                                if self._stop:
                                    break
                                out.start()
                            out.write(pcm[pos : pos + CHUNK])
                            pos += CHUNK
                except Exception as e:
                    self.error.emit(f"Audio playback error: {e}")
                    return

                if self._stop:
                    break

            if not self._stop:
                self.chapter_finished.emit()
        except Exception as e:
            self.error.emit(str(e))


def get_available_voices() -> list[str]:
    """Return WinRT voice display names. Call from main thread at startup."""
    inited = False
    try:
        _winrt.init_apartment(_winrt.MTA)
        inited = True
    except OSError:
        pass  # apartment already initialized (e.g. by Qt)
    try:
        voices = SpeechSynthesizer.all_voices
        return [v.display_name for v in voices]
    except Exception:
        return []
    finally:
        if inited:
            _winrt.uninit_apartment()
