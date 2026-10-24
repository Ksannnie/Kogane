import contextlib
import io
import runpy
import sys
import types
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brain import ai_brain, intent
from memory import memory_store, schedule_store


def test_local_routing_for_memory_and_schedule_questions():
    with TemporaryDirectory() as directory:
        memory_file = Path(directory) / "memory.json"
        schedule_file = Path(directory) / "schedule.json"

        with patch.object(memory_store, "MEMORY_FILE", memory_file), patch.object(
            schedule_store, "SCHEDULE_FILE", schedule_file
        ):
            memory_store.save_memory({
                "facts": [
                    {"text": "I am studying computer engineering", "created_at": "2026-10-23T00:00:00"}
                ]
            })
            schedule_store.save_events([
                {
                    "date": "2026-10-24",
                    "time": "17:00",
                    "title": "Homework due",
                    "created_at": "2026-10-23T00:00:00",
                }
            ])

            assert intent.detect_intent("what do you remember about me?") == ("recall_memory", None)
            assert intent.detect_intent("do i have homework tomorrow?") == ("show_schedule", "tomorrow")
            assert intent.detect_intent("what's on my schedule?") == ("show_schedule", "upcoming")
            assert intent.detect_intent("remind me my homework is due next Friday at 5pm.") == (
                "add_event",
                "remind me my homework is due next Friday at 5pm.",
            )


def test_unrecognized_schedule_question_is_local_and_not_ai():
    output = io.StringIO()
    ai = types.ModuleType("brain.ai_brain")
    ai.answer_question = Mock(side_effect=AssertionError("AI should not answer schedule questions"))

    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.dict(sys.modules, {"brain.ai_brain": ai}))
        stack.enter_context(patch("builtins.input", side_effect=["when is my next meeting?", "bye"]))
        stack.enter_context(contextlib.redirect_stdout(output))
        for target in [
            "skills.app_launcher.open_app",
            "skills.website_launcher.open_website",
            "skills.folder_launcher.open_folder",
        ]:
            stack.enter_context(patch(target, side_effect=AssertionError("Unexpected external action")))
        runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="__main__")

    rendered = output.getvalue()
    assert "I could not understand that schedule question, Kevin." in rendered
    assert "Try asking for today, tomorrow, this week" in rendered


def test_memory_query_uses_saved_data_not_ai():
    with TemporaryDirectory() as directory:
        memory_file = Path(directory) / "memory.json"
        with patch.object(memory_store, "MEMORY_FILE", memory_file):
            memory_store.save_memory({
                "facts": [
                    {"text": "I am studying computer engineering", "created_at": "2026-10-23T00:00:00"}
                ]
            })

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                with patch("builtins.input", side_effect=["what do you remember about me?", "bye"]):
                    with patch("brain.ai_brain.answer_question", side_effect=AssertionError("AI should not answer memory questions")):
                        runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="__main__")

            rendered = output.getvalue()
            assert "I am studying computer engineering" in rendered


def test_ai_fallback_handles_ollama_errors():
    with patch("brain.ai_brain.chat", side_effect=TimeoutError("timed out")):
        response = ai_brain.answer_question("What is computer engineering?", "Kevin", "introvert")

    assert "too long to respond" in response.lower()
    assert "local schedule" in response.lower()


def test_open_ended_question_still_uses_ai():
    with patch("brain.ai_brain.chat", return_value={"message": {"content": "Computer engineering studies computing systems and hardware."}}):
        response = ai_brain.answer_question("What is computer engineering?", "Kevin", "introvert")

    assert "Computer engineering" in response
