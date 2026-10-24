import io
import runpy
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brain import intent
from voice.tts import VoiceManager


def test_voice_intent_routing():
    cases = [
        ("voice on", ("voice_on", None)),
        ("voice off", ("voice_off", None)),
        ("voice status", ("voice_status", None)),
        ("voice help", ("voice_help", None)),
        ("voice", ("voice_status", None)),
    ]

    for command, expected in cases:
        actual = intent.detect_intent(command)
        assert actual == expected, f"{command!r}: expected {expected!r}, got {actual!r}"


def test_voice_status_and_toggling_without_audio_output():
    manager = VoiceManager()
    assert manager.status() == "off"

    manager.enable()
    assert manager.status() == "on"

    manager.disable()
    assert manager.status() == "off"


def test_voice_speaks_expected_text_and_handles_errors():
    manager = VoiceManager()
    with patch("subprocess.Popen") as popen_mock:
        manager.speak("hello world")
        assert popen_mock.call_count == 0

        manager.enable()
        manager.speak("hello world")
        args, _ = popen_mock.call_args
        assert args[0] == ["say", "hello world"]

    with patch("subprocess.Popen", side_effect=OSError("speech failed")):
        manager.enable()
        assert manager.speak("broken text") is False


def test_main_voice_commands_are_non_blocking_and_text_stays_available():
    output = io.StringIO()
    with patch("builtins.input", side_effect=["voice on", "voice help", "voice status", "bye"]):
        with patch("voice.tts.subprocess.Popen") as popen_mock:
            with patch("sys.stdout", output):
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="__main__")

    rendered = output.getvalue()
    assert "Voice is currently off" in rendered or "Voice is currently on" in rendered
    assert "voice help" in rendered.lower() or "Voice commands" in rendered
    assert "Kogane: Awaiting your command" in rendered

    # A normal text path still works even when voice is off.
    assert "I could not understand that schedule question" not in rendered
