import os
import json
import plistlib
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


class SpeechInputError(RuntimeError):
    """A safe, user-facing push-to-talk failure."""


def _select_transcript(final_transcript, partial_transcript):
    final = " ".join(final_transcript.split())
    partial = " ".join(partial_transcript.split())
    if final:
        return final, "final", False
    if partial:
        return partial, "partial", True
    return "", "none", False


class SpeechToText:
    """Local speech input adapter; replaceable independently from command routing."""

    TIMEOUT_SECONDS = 50
    BUILD_TIMEOUT_SECONDS = 60
    SIGN_TIMEOUT_SECONDS = 30
    HELPER_SCRIPT = Path(__file__).with_name("macos_speech.swift")
    HELPER_APP = Path.home() / "Library" / "Caches" / "KOGANE" / "KoganeSpeech.app"
    _build_lock = threading.Lock()

    @classmethod
    def _ensure_helper_app(cls):
        contents = cls.HELPER_APP / "Contents"
        executable = contents / "MacOS" / "KoganeSpeech"
        info_plist = contents / "Info.plist"
        plist_data = plistlib.dumps({
            "CFBundleExecutable": "KoganeSpeech",
            "CFBundleIdentifier": "com.kogane.speech-input",
            "CFBundleName": "KOGANE Speech Input",
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "1.0",
            "LSMinimumSystemVersion": "13.0",
            "NSMicrophoneUsageDescription": "KOGANE records a short utterance only after you enter voice listen.",
            "NSSpeechRecognitionUsageDescription": "KOGANE uses on-device speech recognition only after you enter voice listen.",
        })

        with cls._build_lock:
            contents.mkdir(parents=True, exist_ok=True)
            executable.parent.mkdir(parents=True, exist_ok=True)
            if not info_plist.exists() or info_plist.read_bytes() != plist_data:
                info_plist.write_bytes(plist_data)

            if (
                not executable.exists()
                or cls.HELPER_SCRIPT.stat().st_mtime > executable.stat().st_mtime
                or info_plist.stat().st_mtime > executable.stat().st_mtime
            ):
                temporary_executable = executable.with_suffix(".tmp")
                try:
                    build = subprocess.run(
                        ["swiftc", str(cls.HELPER_SCRIPT), "-o", str(temporary_executable)],
                        capture_output=True,
                        text=True,
                        timeout=cls.BUILD_TIMEOUT_SECONDS,
                        check=False,
                    )
                except subprocess.TimeoutExpired as error:
                    raise SpeechInputError("Building local speech recognition timed out. [stage=build]") from error
                except (FileNotFoundError, OSError) as error:
                    raise SpeechInputError("Swift compiler is unavailable. [stage=build]") from error

                if build.returncode != 0:
                    temporary_executable.unlink(missing_ok=True)
                    raise SpeechInputError(
                        f"Could not build the local speech helper. [stage=build, exit={build.returncode}]"
                    )
                os.replace(temporary_executable, executable)

            try:
                signing = subprocess.run(
                    [
                        "codesign", "--force", "--deep", "--sign", "-",
                        "--identifier", "com.kogane.speech-input", "--timestamp=none",
                        str(cls.HELPER_APP),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=cls.SIGN_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                raise SpeechInputError("Signing the local speech helper timed out. [stage=sign]") from error
            except (FileNotFoundError, OSError) as error:
                raise SpeechInputError("Code signing is unavailable for the local speech helper. [stage=sign]") from error

            if signing.returncode != 0:
                raise SpeechInputError(
                    f"Could not sign the local speech helper. [stage=sign, exit={signing.returncode}]"
                )

        return executable

    def transcribe_once(self, on_ready=None):
        if sys.platform != "darwin":
            raise SpeechInputError("Push-to-talk speech input is currently supported on macOS only.")
        if not self.HELPER_SCRIPT.is_file():
            raise SpeechInputError("The local speech recognition helper is missing.")

        try:
            helper_app_executable = self._ensure_helper_app()
            with tempfile.TemporaryDirectory(prefix="kogane-speech-") as ipc_directory:
                stdout_path = Path(ipc_directory) / "transcription.txt"
                stderr_path = Path(ipc_directory) / "diagnostics.txt"
                command = [
                    "/usr/bin/open", "-W", "-n", "-a", str(self.HELPER_APP),
                    "--stdout", str(stdout_path), "--stderr", str(stderr_path),
                ]
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                deadline = time.monotonic() + self.TIMEOUT_SECONDS
                ready_notified = False
                while process.poll() is None:
                    current_diagnostics = (
                        stderr_path.read_text(errors="replace") if stderr_path.exists() else ""
                    )
                    if not ready_notified and "KOGANE_READY" in current_diagnostics:
                        ready_notified = True
                        if on_ready is not None:
                            on_ready()
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        process.kill()
                        process.communicate()
                        raise subprocess.TimeoutExpired(command, self.TIMEOUT_SECONDS)
                    time.sleep(min(0.05, remaining))

                open_stdout, open_stderr = process.communicate()
                diagnostic_output = (
                    stderr_path.read_text(errors="replace") if stderr_path.exists() else ""
                )
                if open_stderr:
                    diagnostic_output = f"{diagnostic_output}\n{open_stderr}"
                output_payload = stdout_path.read_text(errors="replace") if stdout_path.exists() else ""
                returncode = process.returncode
        except subprocess.TimeoutExpired as error:
            raise SpeechInputError("Speech recognition timed out. Please try again.") from error
        except FileNotFoundError as error:
            raise SpeechInputError("Swift is unavailable, so local speech recognition cannot start. [stage=build_or_launch]") from error
        except OSError as error:
            raise SpeechInputError("Could not prepare or launch the local speech helper. [stage=helper_launch]") from error

        diagnostic = any(
            line.startswith("KOGANE_DIAGNOSTIC ") and " reason=" in line
            for line in diagnostic_output.splitlines()
        )
        if returncode != 0 or diagnostic:
            raise SpeechInputError(self._message_for_error(returncode, diagnostic_output))

        if not ready_notified and "KOGANE_READY" in diagnostic_output:
            ready_notified = True
            if on_ready is not None:
                on_ready()
        if not ready_notified:
            raise SpeechInputError("Speech helper exited before recording was ready. [stage=readiness]")

        try:
            payload = json.loads(output_payload)
            final_candidate = payload.get("final_transcript", "")
            partial_candidate = payload.get("partial_transcript", "")
        except (json.JSONDecodeError, AttributeError) as error:
            raise SpeechInputError("Speech helper returned an invalid result. [stage=transcription_output]") from error

        transcription, source, overwritten = _select_transcript(final_candidate, partial_candidate)
        if not transcription:
            raise SpeechInputError("Speech helper returned no result. [stage=launchservices]")
        if source == "partial":
            from brain.intent import detect_intent
            from skills.app_launcher import APP_ALIASES

            intent, target = detect_intent(transcription)
            if intent != "open_app" or target not in APP_ALIASES:
                raise SpeechInputError(
                    "Only an interim transcription was available and it was not a validated app command. Please repeat it. "
                    "[stage=partial_validation]"
                )
        return transcription

    @staticmethod
    def _message_for_error(returncode, error_output):
        diagnostic = next(
            (line for line in error_output.splitlines() if line.startswith("KOGANE_DIAGNOSTIC ")),
            "",
        )
        fields = dict(
            part.split("=", 1)
            for part in diagnostic.removeprefix("KOGANE_DIAGNOSTIC ").split()
            if "=" in part
        )
        error_code = fields.get("reason", "")
        messages = {
            "MIC_PERMISSION_DENIED": "Microphone permission was denied. Allow access for KOGANE Speech Input in System Settings, then try again.",
            "AUTHORIZATION_TIMEOUT": "macOS permission authorization timed out. Check Privacy & Security settings and try again.",
            "NO_MICROPHONE": "No microphone is available. Connect or enable a microphone, then try again.",
            "NO_AUDIO_BUFFERS": "The microphone started but supplied no audio buffers.",
            "SILENT_AUDIO": "Audio buffers arrived, but no input level was detected. Check the selected microphone and input level.",
            "SPEECH_PERMISSION_DENIED": "Speech recognition permission was denied. Allow access for KOGANE Speech Input in System Settings, then try again.",
            "NO_LOCAL_RECOGNIZER": "Apple's offline speech recognition model is unavailable for this language on this Mac.",
            "RECOGNIZER_UNAVAILABLE": "Apple's en-US speech recognizer is currently unavailable on this Mac.",
            "EMPTY_TRANSCRIPTION": "I did not catch any clear speech. Please try again.",
            "RECOGNITION_TIMEOUT": "Speech recognition timed out. Please try again.",
            "SPEECH_ERROR": "Speech recognition failed. Check the diagnostic details below and try again.",
            "AUDIO_ERROR": "Audio capture failed. Check the microphone and diagnostic details below.",
            "USAGE_DESCRIPTION_MISSING": "The speech helper is missing required macOS privacy metadata. Rebuild or reinstall it, then try again.",
        }
        message = messages.get(error_code, "Local speech recognition failed.")
        if diagnostic:
            safe_details = [f"stage={fields['stage']}"] if "stage" in fields else []
            safe_keys = (
                "domain", "code", "reason", "device", "device_id", "sample_rate",
                "channels", "format", "recognizer_available", "on_device_supported",
                "buffers", "level_samples", "rms", "peak", "partial_results",
                "nonempty_partial_results", "longest_partial_characters",
                "final_transcript_characters", "valid_transcript_overwritten",
                "transcript_source", "final_result", "end_audio", "task_state",
                "error_domain", "error_code",
            )
            safe_details.extend(f"{key}={fields[key]}" for key in safe_keys if key in fields)
            return f"{message} [{', '.join(safe_details)}]"
        return f"Could not launch the local speech helper. [stage=launchservices, exit={returncode}]"
