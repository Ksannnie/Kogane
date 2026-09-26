"""Run with: python3 tests/test_schedule.py (uses temporary data only)."""

import json
import sys
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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


if __name__ == "__main__":
    test_schedule_store()
    test_natural_schedule_events()
    print("All schedule tests passed.")
