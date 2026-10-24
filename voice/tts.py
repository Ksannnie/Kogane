import subprocess
import threading


class VoiceManager:
    def __init__(self):
        self.enabled = False
        self._process = None
        self._lock = threading.Lock()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
        self._stop_current()

    def status(self):
        return "on" if self.enabled else "off"

    def _stop_current(self):
        if self._process is None:
            return

        try:
            if self._process.poll() is None:
                self._process.terminate()
                self._process.wait(timeout=0.2)
        except (AttributeError, OSError, subprocess.SubprocessError, TimeoutError):
            pass
        finally:
            self._process = None

    def speak(self, text):
        if not self.enabled or not text or not str(text).strip():
            return False

        message = " ".join(str(text).strip().split())

        with self._lock:
            try:
                self._stop_current()
                self._process = subprocess.Popen(
                    ["say", message],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except (FileNotFoundError, OSError, ValueError):
                return False
