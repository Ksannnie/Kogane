import io
import json
import plistlib
import re
import runpy
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brain.intent import detect_intent
from voice.speech_to_text import SpeechInputError, SpeechToText, _select_transcript


def _mock_launch_result(args, returncode=0, stdout="", stderr=""):
    if args[0] == "/usr/bin/open":
        Path(args[args.index("--stdout") + 1]).write_text(stdout)
        Path(args[args.index("--stderr") + 1]).write_text(stderr)
    return subprocess.CompletedProcess(args, returncode, "", "")


def _mock_open_process(args, returncode=0, payload=None, stderr=""):
    payload = payload or {"final_transcript": "open spotify", "partial_transcript": ""}
    Path(args[args.index("--stdout") + 1]).write_text(json.dumps(payload))
    Path(args[args.index("--stderr") + 1]).write_text(stderr or "KOGANE_READY\n")
    process = Mock()
    process.poll.side_effect = [None, returncode]
    process.returncode = returncode
    process.communicate.return_value = ("", "")
    return process


def test_voice_listen_intent_is_explicit():
    assert detect_intent("voice listen") == ("voice_listen", None)
    assert detect_intent("hello") == ("greeting", None)


def test_speech_to_text_returns_trimmed_local_transcription():
    backend = SpeechToText()
    with tempfile.TemporaryDirectory() as directory:
        bundle = Path(directory) / "KoganeSpeech.app"
        with patch.object(SpeechToText, "HELPER_APP", bundle), patch(
            "voice.speech_to_text.subprocess.run"
        ) as run_mock, patch("voice.speech_to_text.subprocess.Popen") as popen_mock:
            def run_side_effect(args, **kwargs):
                if args[0] == "swiftc":
                    Path(args[args.index("-o") + 1]).write_text("mock binary")
                    return subprocess.CompletedProcess(args, 0, "", "")
                if args[0] == "codesign":
                    return subprocess.CompletedProcess(args, 0, "", "")
                raise AssertionError("Speech helper launch must use Popen")

            run_mock.side_effect = run_side_effect
            popen_mock.side_effect = lambda args, **kwargs: _mock_open_process(
                args,
                payload={"final_transcript": "  open spotify\n", "partial_transcript": ""},
                stderr="KOGANE_READY\nKOGANE_DIAGNOSTIC status=ok buffers=42 peak=0.125000\n",
            )
            ready_notifications = []
            with patch("voice.speech_to_text.sys.platform", "darwin"):
                assert backend.transcribe_once(on_ready=lambda: ready_notifications.append(True)) == "open spotify"

        plist = plistlib.loads((bundle / "Contents/Info.plist").read_bytes())
        assert plist["CFBundleExecutable"] == "KoganeSpeech"
        assert plist["CFBundleIdentifier"] == "com.kogane.speech-input"
        assert plist["CFBundlePackageType"] == "APPL"
        assert plist["NSMicrophoneUsageDescription"]
        assert plist["NSSpeechRecognitionUsageDescription"]
        assert run_mock.call_count == 2
        assert run_mock.call_args_list[0].args[0][0] == "swiftc"
        assert run_mock.call_args_list[1].args[0][0] == "codesign"
        assert "com.kogane.speech-input" in run_mock.call_args_list[1].args[0]
        assert popen_mock.call_args.args[0][:5] == [
            "/usr/bin/open", "-W", "-n", "-a", str(bundle),
        ]
        assert ready_notifications == [True]


@pytest.mark.parametrize(
    ("final_transcript", "partial_transcript", "expected", "source", "overwritten"),
    [
        ("", "Open Spotify", "Open Spotify", "partial", True),
        ("", "", "", "none", False),
        ("Open Spotify", "Open", "Open Spotify", "final", False),
    ],
)
def test_transcript_selection_preserves_only_nonempty_text(
    final_transcript, partial_transcript, expected, source, overwritten
):
    assert _select_transcript(final_transcript, partial_transcript) == (
        expected,
        source,
        overwritten,
    )


def test_partial_only_transcription_is_returned_to_python_when_validated():
    backend = SpeechToText()
    payload = {"final_transcript": "", "partial_transcript": "Open Spotify"}
    with patch.object(SpeechToText, "_ensure_helper_app", return_value=Path("/mock/KoganeSpeech.app")), patch(
        "voice.speech_to_text.subprocess.Popen",
        side_effect=lambda args, **kwargs: _mock_open_process(
            args,
            payload=payload,
            stderr=(
                "KOGANE_READY\nKOGANE_DIAGNOSTIC status=ok transcript_source=partial "
                "valid_transcript_overwritten=yes\n"
            ),
        ),
    ):
        with patch("voice.speech_to_text.sys.platform", "darwin"):
            assert backend.transcribe_once() == "Open Spotify"


def test_unvalidated_partial_transcription_is_rejected():
    backend = SpeechToText()
    with patch.object(SpeechToText, "_ensure_helper_app", return_value=Path("/mock/KoganeSpeech.app")), patch(
        "voice.speech_to_text.subprocess.Popen",
        side_effect=lambda args, **kwargs: _mock_open_process(
            args,
            payload={"final_transcript": "", "partial_transcript": "Open an unknown thing"},
        ),
    ):
        with patch("voice.speech_to_text.sys.platform", "darwin"):
            with pytest.raises(SpeechInputError, match="partial_validation"):
                backend.transcribe_once()


def test_diagnostic_details_are_shown_but_raw_stderr_is_not():
    message = SpeechToText._message_for_error(
        1,
        "untrusted extra stderr\n"
        "KOGANE_DIAGNOSTIC stage=recognition reason=SPEECH_ERROR domain=Speech code=203 "
        "device=Built_In_Microphone sample_rate=48000.0 channels=1 format=pcmFormatFloat32 "
        "buffers=42 level_samples=43008 rms=0.012000 peak=0.125000 partial_results=2 "
        "final_result=no end_audio=yes task_state=recognition_timeout",
    )

    assert "stage=recognition" in message
    assert "domain=Speech" in message
    assert "code=203" in message
    assert "device=Built_In_Microphone" in message
    assert "sample_rate=48000.0" in message
    assert "buffers=42" in message
    assert "rms=0.012000" in message
    assert "partial_results=2" in message
    assert "end_audio=yes" in message
    assert "untrusted extra stderr" not in message


def test_swift_speech_callbacks_use_a_dedicated_queue_before_task_creation():
    source = SpeechToText.HELPER_SCRIPT.read_text()

    queue_assignment = source.index("recognizer.queue = recognitionCallbackQueue")
    task_creation = source.index("recognizer.recognitionTask(with: request)")
    capture_wait = source.index(".wait(timeout: .now() + .seconds(6))")
    result_wait = source.index("completionGate.wait(timeout: .now() + .seconds(10))")

    assert source.index("recognitionCallbackQueue.maxConcurrentOperationCount = 1") < queue_assignment
    assert queue_assignment < task_creation < capture_wait < result_wait


def test_recognition_timeout_keeps_callback_state_diagnostics():
    message = SpeechToText._message_for_error(
        1,
        "KOGANE_DIAGNOSTIC stage=recognition_timeout reason=RECOGNITION_TIMEOUT "
        "buffers=59 partial_results=0 final_result=no end_audio=yes "
        "task_state=recognition_timeout error_domain=Speech error_code=203 "
        "nonempty_partial_results=2 longest_partial_characters=12 "
        "final_transcript_characters=0 valid_transcript_overwritten=yes transcript_source=partial",
    )

    assert "stage=recognition_timeout" in message
    assert "buffers=59" in message
    assert "partial_results=0" in message
    assert "final_result=no" in message
    assert "end_audio=yes" in message
    assert "error_domain=Speech" in message
    assert "error_code=203" in message
    assert "nonempty_partial_results=2" in message
    assert "longest_partial_characters=12" in message
    assert "final_transcript_characters=0" in message
    assert "valid_transcript_overwritten=yes" in message
    assert "transcript_source=partial" in message


def test_app_bundle_is_rebuilt_when_swift_helper_changes():
    backend = SpeechToText()
    with tempfile.TemporaryDirectory() as directory:
        bundle = Path(directory) / "KoganeSpeech.app"
        with patch.object(SpeechToText, "HELPER_APP", bundle), patch(
            "voice.speech_to_text.subprocess.run",
            side_effect=lambda args, **kwargs: (
                Path(args[args.index("-o") + 1]).write_text("mock binary")
                if args[0] == "swiftc"
                else subprocess.CompletedProcess(args, 0, "", "")
            ) and subprocess.CompletedProcess(args, 0, "", ""),
        ) as run_mock:
            executable = SpeechToText._ensure_helper_app()

    assert executable.name == "KoganeSpeech"
    assert run_mock.call_count == 2
    assert run_mock.call_args_list[0].args[0][0] == "swiftc"
    assert run_mock.call_args_list[1].args[0][0] == "codesign"


def test_old_direct_swift_behavior_is_removed():
    assert SpeechToText.HELPER_APP.name == "KoganeSpeech.app"


@pytest.mark.parametrize(
    ("returncode", "stderr", "expected"),
    [
        (2, "KOGANE_DIAGNOSTIC stage=microphone_authorization reason=MIC_PERMISSION_DENIED", "microphone permission"),
        (3, "KOGANE_DIAGNOSTIC stage=audio_input reason=NO_MICROPHONE", "microphone"),
        (4, "KOGANE_DIAGNOSTIC stage=recognizer reason=NO_LOCAL_RECOGNIZER", "offline speech recognition"),
        (5, "KOGANE_DIAGNOSTIC stage=transcription reason=EMPTY_TRANSCRIPTION", "did not catch"),
        (6, "KOGANE_DIAGNOSTIC stage=recognition reason=SPEECH_ERROR domain=Speech code=203", "speech recognition"),
        (7, "KOGANE_DIAGNOSTIC stage=recognition_timeout reason=RECOGNITION_TIMEOUT", "timed out"),
        (8, "KOGANE_DIAGNOSTIC stage=audio_capture reason=NO_AUDIO_BUFFERS buffers=0", "no audio buffers"),
        (9, "KOGANE_DIAGNOSTIC stage=audio_capture reason=SILENT_AUDIO buffers=120 peak=0.000000", "no input level was detected"),
    ],
)
def test_speech_errors_are_reported_safely(returncode, stderr, expected):
    backend = SpeechToText()
    with patch.object(SpeechToText, "_ensure_helper_app", return_value=Path("/mock/KoganeSpeech")), patch(
        "voice.speech_to_text.subprocess.Popen"
    ) as run_mock:
        run_mock.side_effect = lambda args, **kwargs: _mock_open_process(
            args, returncode=returncode, stderr=stderr
        )
        with pytest.raises(SpeechInputError, match=f"(?i){re.escape(expected)}") as error:
            backend.transcribe_once()
        if returncode == 6:
            assert "domain=Speech" in str(error.value)
            assert "code=203" in str(error.value)


def test_speech_timeout_is_reported():
    backend = SpeechToText()
    process = Mock()
    process.poll.return_value = None
    process.returncode = None
    with patch.object(SpeechToText, "_ensure_helper_app", return_value=Path("/mock/KoganeSpeech")), patch(
        "voice.speech_to_text.subprocess.Popen", return_value=process
    ), patch("voice.speech_to_text.time.monotonic", side_effect=[0.0, 51.0]):
        with pytest.raises(SpeechInputError, match="timed out"):
            backend.transcribe_once()
    process.kill.assert_called_once()


def test_launchservices_helper_without_output_is_reported():
    backend = SpeechToText()
    with patch.object(SpeechToText, "_ensure_helper_app", return_value=Path("/mock/KoganeSpeech.app")), patch(
        "voice.speech_to_text.subprocess.Popen",
        side_effect=lambda args, **kwargs: _mock_open_process(
            args, payload={"final_transcript": "", "partial_transcript": ""}
        ),
    ):
        with patch("voice.speech_to_text.sys.platform", "darwin"):
            with pytest.raises(SpeechInputError, match="stage=launchservices"):
                backend.transcribe_once()


def test_missing_swift_backend_is_reported():
    backend = SpeechToText()
    with patch.object(SpeechToText, "_ensure_helper_app", return_value=Path("/mock/KoganeSpeech")), patch(
        "voice.speech_to_text.subprocess.Popen", side_effect=FileNotFoundError
    ):
        with pytest.raises(SpeechInputError, match="Swift is unavailable"):
            backend.transcribe_once()


def test_voice_listen_transcription_reenters_normal_command_routing():
    output = io.StringIO()
    with patch("builtins.input", side_effect=["voice listen", "bye"]):
        with patch(
            "voice.speech_to_text.SpeechToText.transcribe_once",
            side_effect=lambda on_ready=None: (on_ready() if on_ready else None) or "open spotify",
        ) as listen_mock:
            with patch("skills.app_launcher.open_app", return_value=(True, "Opened Spotify.")):
                with patch("sys.stdout", output):
                    runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="__main__")

    rendered = output.getvalue()
    assert "Preparing local speech recognition." in rendered
    assert "Microphone is ready. Speak now." in rendered
    assert "Recognized: open spotify" in rendered
    assert "Opened Spotify." in rendered
    listen_mock.assert_called_once()


def test_voice_listen_error_does_not_crash_or_record_automatically():
    output = io.StringIO()
    with patch("builtins.input", side_effect=["hello", "voice listen", "bye"]):
        with patch("voice.speech_to_text.SpeechToText.transcribe_once", side_effect=SpeechInputError("No microphone is available.")) as listen_mock:
            with patch("sys.stdout", output):
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="__main__")

    assert listen_mock.call_count == 1
    rendered = output.getvalue()
    assert "Preparing local speech recognition." in rendered
    assert "No microphone is available." in rendered
    assert "Bye bye" in rendered


def test_no_recording_occurs_without_explicit_voice_listen():
    with patch("builtins.input", side_effect=["hello", "bye"]):
        with patch("voice.speech_to_text.SpeechToText.transcribe_once") as listen_mock:
            with patch("sys.stdout", io.StringIO()):
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="__main__")

    listen_mock.assert_not_called()
