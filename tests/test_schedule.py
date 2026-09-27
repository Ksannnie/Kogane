"""Run with: python3 tests/test_schedule.py (uses temporary data only)."""

import contextlib
import io
import json
import runpy
import sys
import types
from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory import schedule_store


class FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 9, 25)


def test_schedule_store():
    with TemporaryDirectory() as directory:
        schedule_file = Path(directory) / "schedule.json"
        with patch.object(schedule_store, "SCHEDULE_FILE", schedule_file), patch.object(
            schedule_store, "date", FixedDate
        ):
            assert schedule_store.load_events() == []
            assert schedule_store.list_upcoming_events() == []

            for invalid in [
                "", "2026-09-25", "2026-09-25 15:00", "2026-02-30 Bad date",
                "20260925 Bad format", "2026-09-25 25:00 Bad hour",
                "2026-09-25 15:60 Bad minute", "2026-09-25 9:00 Bad format",
            ]:
                assert not schedule_store.add_event(invalid)[0], invalid
            assert not schedule_file.exists()

            for event in [
                "2026-10-02 Outside week",
                "2026-09-26 15:00 Tomorrow class",
                "2026-09-25 18:00 Late class",
                "2026-09-24 Past event",
                "2026-09-25 CHEM lab report due",
                "2026-10-01 Last day of week",
                "2026-09-25 09:00 Early class",
            ]:
                assert schedule_store.add_event(event)[0], event

            saved = schedule_store.load_events()
            assert len(saved) == 7
            assert json.loads(schedule_file.read_text()) == saved
            assert set(saved[0]) == {"date", "time", "title", "created_at"}
            assert saved[4]["time"] is None
            assert saved[4]["title"] == "CHEM lab report due"

            def titles(events):
                return [event["title"] for event in events]

            assert titles(schedule_store.list_upcoming_events()) == [
                "CHEM lab report due", "Early class", "Late class",
                "Tomorrow class", "Last day of week", "Outside week",
            ]
            today = schedule_store.list_today_events()
            assert titles(today) == ["CHEM lab report due", "Early class", "Late class"]
            tomorrow = schedule_store.list_tomorrow_events()
            assert titles(tomorrow) == ["Tomorrow class"]
            assert titles(schedule_store.list_week_events()) == [
                "CHEM lab report due", "Early class", "Late class",
                "Tomorrow class", "Last day of week",
            ]

            for invalid in ["", "zero", "0", "-1", "4"]:
                assert not schedule_store.delete_event(invalid, today)[0], invalid
            assert not schedule_store.delete_event("1", None)[0]
            assert schedule_store.load_events() == saved

            # Display order differs from file order; filtered views start at 1.
            assert schedule_store.delete_event("2", today)[0]
            assert titles(schedule_store.list_today_events()) == ["CHEM lab report due", "Late class"]
            assert schedule_store.delete_event("1", tomorrow)[0]
            assert schedule_store.list_tomorrow_events() == []
            assert not schedule_store.delete_event("1", tomorrow)[0]
            assert "Past event" in titles(schedule_store.load_events())

            original = schedule_file.read_text()
            with patch.object(Path, "replace", side_effect=OSError("Write failed")):
                try:
                    schedule_store.add_event("2026-09-25 Unsaved event")
                except OSError:
                    pass
                else:
                    raise AssertionError("Expected the write error to be reported")
            assert schedule_file.read_text() == original
            assert not schedule_file.with_suffix(".json.tmp").exists()

            # A damaged file must never be silently replaced with new data.
            for damaged in ["broken JSON", "{}", "[{}]"]:
                schedule_file.write_text(damaged)
                try:
                    schedule_store.add_event("2026-09-25 New event")
                except ValueError:
                    pass
                else:
                    raise AssertionError("Expected invalid saved data to be reported")
                assert schedule_file.read_text() == damaged


def test_natural_schedule_events():
    with TemporaryDirectory() as directory:
        schedule_file = Path(directory) / "schedule.json"
        with patch.object(schedule_store, "SCHEDULE_FILE", schedule_file):
            for time_text, expected_time in [
                ("5pm", "17:00"), ("5:00pm", "17:00"), ("17:00", "17:00"),
                ("9am", "09:00"), ("9:30am", "09:30"),
                ("12am", "00:00"), ("12pm", "12:00"), ("5 PM", "17:00"),
            ]:
                command = f"remind me on 2026-09-30 at {time_text} to do CHEM lab report"
                expected = ("2026-09-30", expected_time, "CHEM lab report")
                assert schedule_store.parse_natural_event(command) == expected, command
                assert schedule_store.add_event(command)[0], command
                saved = schedule_store.load_events()[-1]
                assert (saved["date"], saved["time"], saved["title"]) == expected

            for command, expected in [
                (
                    "remind me on 2026-09-30 to do CHEM lab report",
                    ("2026-09-30", None, "CHEM lab report"),
                ),
                (
                    "I have calculus homework due 2026-09-29",
                    ("2026-09-29", None, "calculus homework"),
                ),
                (
                    "I have CHEM lab due on 2026-09-30",
                    ("2026-09-30", None, "CHEM lab"),
                ),
                (
                    "I HAVE CHEM lab DUE ON 2026-09-30.",
                    ("2026-09-30", None, "CHEM lab"),
                ),
                (
                    "remind me on 2026-09-30 at 9am to Open YouTube for CHEM",
                    ("2026-09-30", "09:00", "Open YouTube for CHEM"),
                ),
                (
                    "I have 17:00 planning notes due 2026-09-30",
                    ("2026-09-30", None, "17:00 planning notes"),
                ),
            ]:
                assert schedule_store.add_event(command)[0], command
                saved = schedule_store.load_events()[-1]
                assert (saved["date"], saved["time"], saved["title"]) == expected

            original = schedule_file.read_text()
            for invalid in [
                "remind me on 2026-02-30 at 5pm to do CHEM lab",
                "I have CHEM lab due on 2026-02-30",
                "remind me on 20260930 to do CHEM lab",
                "remind me on 2026-09-30 at 5pm",
                "remind me on 2026-09-30 to do",
            ] + [
                f"remind me on 2026-09-30 at {bad_time} to do CHEM lab"
                for bad_time in ["13pm", "0am", "24:00", "9:99am", "5:7pm", "5"]
            ]:
                assert not schedule_store.add_event(invalid)[0], invalid
                assert schedule_file.read_text() == original


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 9, 25, 16, 0)  # Friday, before 5pm


def test_relative_schedule_events():
    now = FixedDateTime.now()
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    expected_weeks = {
        "": ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-09-25", "2026-09-26", "2026-09-27"],
        "this ": ["2026-09-21", "2026-09-22", "2026-09-23", "2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27"],
        "next ": ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04"],
    }
    for prefix, expected_dates in expected_weeks.items():
        for weekday, expected in zip(weekdays, expected_dates):
            phrase = prefix + weekday
            assert schedule_store._resolve_event_date(phrase, "17:00", now) == expected, phrase

    for phrase, event_time, clock, expected in [
        ("today", "15:00", now, "2026-09-25"),
        ("tomorrow", None, now, "2026-09-26"),
        ("friday", None, now, "2026-09-25"),
        ("friday", "15:00", now, "2026-10-02"),
        ("friday", "17:00", datetime(2026, 9, 25, 17), "2026-09-25"),
        ("friday", "17:00", datetime(2026, 9, 25, 17, 0, 1), "2026-10-02"),
        ("this friday", "15:00", now, "2026-09-25"),
        ("next friday", "17:00", datetime(2026, 9, 21, 10), "2026-10-02"),
        ("next monday", "08:00", datetime(2026, 9, 27, 10), "2026-09-28"),
        ("tomorrow", None, datetime(2026, 12, 31, 16), "2027-01-01"),
        ("next friday", "17:00", datetime(2026, 12, 31, 16), "2027-01-08"),
        ("tomorrow", None, datetime(2024, 2, 28, 16), "2024-02-29"),
    ]:
        assert schedule_store._resolve_event_date(phrase, event_time, clock) == expected

    with TemporaryDirectory() as directory:
        with patch.object(schedule_store, "SCHEDULE_FILE", Path(directory) / "schedule.json"), patch.object(
            schedule_store, "datetime", FixedDateTime
        ):
            cases = [
                ("put my homework that's due on friday at 5pm on the schedule", ("2026-09-25", "17:00", "homework")),
                ("put my homework due friday at 5pm on the schedule", ("2026-09-25", "17:00", "homework")),
                ("add homework due friday at 5pm", ("2026-09-25", "17:00", "homework")),
                ("add chem lab due tomorrow at 11:59pm", ("2026-09-26", "23:59", "chem lab")),
                ("schedule calculus study for monday at 3pm", ("2026-09-28", "15:00", "calculus study")),
                ("schedule gym for tomorrow at 6pm", ("2026-09-26", "18:00", "gym")),
                ("remind me friday at 5pm to do homework", ("2026-09-25", "17:00", "homework")),
                ("remind me tomorrow at 9am to do laundry", ("2026-09-26", "09:00", "laundry")),
                ("I have a quiz due next monday at 8am", ("2026-09-28", "08:00", "a quiz")),
                ("put my CHEM lab that’s due on friday at 5:00pm on the schedule", ("2026-09-25", "17:00", "CHEM lab")),
                ("schedule Open YouTube for CHEM for tomorrow at 9:30am", ("2026-09-26", "09:30", "Open YouTube for CHEM")),
                ("remind me on friday at 17:00 to do homework", ("2026-09-25", "17:00", "homework")),
                ("schedule gym for today", ("2026-09-25", None, "gym")),
                ("add homework due this monday", ("2026-09-21", None, "homework")),
                ("remind me FRIDAY at 3pm to do homework", ("2026-10-02", "15:00", "homework")),
            ]
            for command, expected in cases:
                assert schedule_store.is_natural_event_command(command), command
                assert schedule_store.parse_natural_event(command) == expected, command
                assert schedule_store.add_event(command)[0], command
                event = schedule_store.load_events()[-1]
                assert (event["date"], event["time"], event["title"]) == expected, command

            saved = schedule_store.load_events()
            for invalid in [
                "schedule gym for tomorrow at 25pm",
                "add chem lab due friday at 11:60pm",
                "remind me tomorrow at 9am",
            ]:
                assert not schedule_store.add_event(invalid)[0], invalid
                assert schedule_store.load_events() == saved


def test_deadline_statements():
    now = datetime(2026, 9, 25, 16)
    cases = [
        ("remind me my homework is due on friday at 5pm next week", ("2026-10-02", "17:00", "homework")),
        ("remind me my homework is due friday at 5pm next week", ("2026-10-02", "17:00", "homework")),
        ("put my homework that's due on friday at 5pm on the schedule", ("2026-09-25", "17:00", "homework")),
        ("put my homework due friday at 5pm on the schedule", ("2026-09-25", "17:00", "homework")),
        ("homework due friday at 5pm", ("2026-09-25", "17:00", "homework")),
        ("homework is due friday at 5pm", ("2026-09-25", "17:00", "homework")),
        ("chem lab is due tomorrow at 11:59pm", ("2026-09-26", "23:59", "chem lab")),
        ("calculus homework is due next monday at 8am", ("2026-09-28", "08:00", "calculus homework")),
    ]
    with TemporaryDirectory() as directory:
        schedule_file = Path(directory) / "schedule.json"
        with patch.object(schedule_store, "SCHEDULE_FILE", schedule_file):
            for command, expected in cases:
                assert schedule_store.parse_natural_event(command, now=now) == expected, command
                success, message = schedule_store.add_event(command, now=now)
                assert success, (command, message)
                assert message == f"Added to schedule: {expected[0]} {expected[1]} — {expected[2]}"
                event = json.loads(schedule_file.read_text())[-1]
                assert (event["date"], event["time"], event["title"]) == expected
                assert event["created_at"] == now.isoformat(timespec="microseconds")
            assert len(schedule_store.load_events()) == len(cases)

            # A deadline inside an explicit event title must not replace its date.
            explicit = "2026-09-30 CHEM lab report due friday at 5pm"
            assert schedule_store.parse_natural_event(explicit, now=now) is None
            assert schedule_store.add_event(explicit, now=now)[0]
            event = schedule_store.load_events()[-1]
            assert (event["date"], event["time"], event["title"]) == (
                "2026-09-30", None, "CHEM lab report due friday at 5pm"
            )

    for clock in [datetime(2026, 9, 21, 10), now, datetime(2026, 9, 25, 18)]:
        assert schedule_store.parse_natural_event(cases[0][0], now=clock) == cases[0][1]
    assert schedule_store.parse_natural_event("homework due friday next week", now=now) == (
        "2026-10-02", None, "homework"
    )


def test_schedule_save_confirmation():
    """Exercise routing, the real JSON writer, and main-loop messages together."""
    command = "remind me my homework is due on friday at 5pm next week"

    def run_session(commands):
        output = io.StringIO()
        ai = types.ModuleType("brain.ai_brain")
        ai.answer_question = Mock(side_effect=AssertionError("Schedule command reached AI"))
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {"brain.ai_brain": ai}))
            stack.enter_context(patch("builtins.input", side_effect=commands + ["bye"]))
            stack.enter_context(contextlib.redirect_stdout(output))
            for target in [
                "skills.app_launcher.open_app", "skills.website_launcher.open_website",
                "skills.folder_launcher.open_folder", "memory.memory_store.get_facts",
            ]:
                stack.enter_context(patch(target, side_effect=AssertionError("Unexpected external action")))
            runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="__main__")
        return output.getvalue()

    with TemporaryDirectory() as directory:
        schedule_file = Path(directory) / "schedule.json"
        with patch.object(schedule_store, "SCHEDULE_FILE", schedule_file), patch.object(
            schedule_store, "datetime", FixedDateTime
        ), patch.object(schedule_store, "date", FixedDate):
            output = run_session([command, "schedule"])
            assert "Added to schedule: 2026-10-02 17:00 — homework" in output
            assert "1. 2026-10-02 17:00 - homework" in output
            assert len(json.loads(schedule_file.read_text())) == 1

            # A fresh session must find the event in JSON, not just in memory.
            output = run_session(["schedule"])
            assert "1. 2026-10-02 17:00 - homework" in output
            original = schedule_file.read_text()

            output = run_session(["homework due friday at 25pm"])
            assert "Event not saved:" in output
            assert "Added to schedule:" not in output
            assert schedule_file.read_text() == original

            with patch.object(Path, "replace", side_effect=OSError("Write failed")):
                output = run_session([command])
            assert "I could not finish that schedule request: Write failed" in output
            assert "Added to schedule:" not in output
            assert schedule_file.read_text() == original

            # Viewing questions must use real JSON data, with no AI calls.
            views = {
                "whats on my schedule": "upcoming",
                "what's on my schedule": "upcoming",
                "what is on my schedule": "upcoming",
                "what do I have scheduled": "upcoming",
                "what do I have on my schedule": "upcoming",
                "what do I have today": "today",
                "what do I have tomorrow": "tomorrow",
                "what do I have this week": "this week",
                "do I have anything today": "today",
                "do I have anything tomorrow": "tomorrow",
                "show my schedule": "upcoming",
                "show my calendar": "upcoming",
                "what's on my calendar": "upcoming",
                "whats on my calendar": "upcoming",
                "how does my schedule look tomorrow?": "tomorrow",
            }
            schedule_store.save_events([])
            for question in views:
                output = run_session([question])
                assert "No events found, Kevin." in output, question
                assert "Your schedule (" not in output, question
                assert schedule_store.load_events() == []

            for event_text in [
                "2026-09-25 Today from JSON",
                "2026-09-26 Tomorrow from JSON",
                "2026-09-30 Week from JSON",
                "2026-10-02 Later from JSON",
            ]:
                assert schedule_store.add_event(event_text)[0]
            expected_titles = {
                "upcoming": ["Today from JSON", "Tomorrow from JSON", "Week from JSON", "Later from JSON"],
                "today": ["Today from JSON"],
                "tomorrow": ["Tomorrow from JSON"],
                "this week": ["Today from JSON", "Tomorrow from JSON", "Week from JSON"],
            }
            saved = schedule_file.read_text()
            for question, view in views.items():
                output = run_session([question])
                assert f"Your schedule ({view}):" in output, question
                displayed = [
                    line.split(" - ", 1)[1] for line in output.splitlines()
                    if line.startswith("Kogane: ") and " - " in line
                ]
                assert displayed == expected_titles[view], (question, displayed)
                assert schedule_file.read_text() == saved


if __name__ == "__main__":
    test_schedule_store()
    test_natural_schedule_events()
    test_relative_schedule_events()
    test_deadline_statements()
    test_schedule_save_confirmation()
    print("All schedule tests passed.")
