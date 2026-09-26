"""Run with: python3 tests/test_intent.py"""

import sys
from pathlib import Path

# Make the project imports available when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brain.intent import detect_intent


def test_intent_routing():
    cases = [
        ("help", ("help", None)),
        ("app help", ("app_help", None)),
        ("website help", ("website_help", None)),
        ("search help", ("search_help", None)),
        ("folder help", ("folder_help", None)),
        ("project help", ("project_help", None)),
        ("workflow help", ("workflow_help", None)),
        ("workflows help", ("workflow_help", None)),
        ("workflow commands", ("workflow_help", None)),
        ("memory help", ("memory_help", None)),
        ("mode help", ("mode_help", None)),
        ("schedule help", ("schedule_help", None)),
        ("calendar help", ("schedule_help", None)),
        (
            "add event 2026-09-26 15:00 Calculus study",
            ("add_event", "2026-09-26 15:00 Calculus study"),
        ),
        (
            "add event 2026-09-30 CHEM lab report due",
            ("add_event", "2026-09-30 CHEM lab report due"),
        ),
        ("schedule", ("show_schedule", "upcoming")),
        ("calendar", ("show_schedule", "upcoming")),
        ("today", ("show_schedule", "today")),
        ("tomorrow", ("show_schedule", "tomorrow")),
        ("this week", ("show_schedule", "this week")),
        ("delete event 1", ("delete_event", "1")),
        ("add event", ("add_event", "")),
        ("delete event", ("delete_event", "")),
        (
            "remind me on 2026-09-30 at 5pm to do CHEM lab report",
            ("add_event", "remind me on 2026-09-30 at 5pm to do CHEM lab report"),
        ),
        (
            "remind me on 2026-09-30 to do CHEM lab report",
            ("add_event", "remind me on 2026-09-30 to do CHEM lab report"),
        ),
        (
            "I have calculus homework due 2026-09-29",
            ("add_event", "I have calculus homework due 2026-09-29"),
        ),
        (
            "I have CHEM lab due on 2026-09-30",
            ("add_event", "I have CHEM lab due on 2026-09-30"),
        ),
        ("what do I have tomorrow", ("show_schedule", "tomorrow")),
        ("what do I have today", ("show_schedule", "today")),
        ("what's my schedule this week", ("show_schedule", "this week")),
        ("what’s my schedule this week?", ("show_schedule", "this week")),
        ("what's on my calendar", ("show_schedule", "upcoming")),
        ("show my schedule", ("show_schedule", "upcoming")),
        (
            "remind me on 2026-09-30 at 5pm to do Open YouTube for CHEM",
            ("add_event", "remind me on 2026-09-30 at 5pm to do Open YouTube for CHEM"),
        ),
        (
            "I have Open YouTube for CHEM due on 2026-09-30",
            ("add_event", "I have Open YouTube for CHEM due on 2026-09-30"),
        ),
        (
            "add event 2026-09-30 10:00 Open YouTube for CHEM",
            ("add_event", "2026-09-30 10:00 Open YouTube for CHEM"),
        ),
        ("start coding", ("start_workflow", "coding")),
        ("start school", ("start_workflow", "school")),
        ("start music", ("start_workflow", "music")),
        ("open chrome", ("open_app", "chrome")),
        ("open music", ("open_app", "spotify")),
        ("play music", ("open_app", "spotify")),
        ("open spotify", ("open_app", "spotify")),
        ("open youtube", ("open_website", "youtube")),
        ("open downloads", ("open_folder", "downloads")),
        ("open kogane folder", ("open_folder", "kogane folder")),
        (
            "google search esp32 s3 pinout",
            ("search_website", ("google", "esp32 s3 pinout")),
        ),
        (
            "youtube search python classes tutorial",
            ("search_website", ("youtube", "python classes tutorial")),
        ),
        ("youtube search music", ("search_website", ("youtube", "music"))),
        ("open kogane repo", ("open_website", "kogane repo")),
        ("what is an API?", ("question", "what is an API?")),
    ]

    for command, expected in cases:
        actual = detect_intent(command)
        assert actual == expected, (
            f"{command!r}: expected {expected!r}, got {actual!r}"
        )


if __name__ == "__main__":
    test_intent_routing()
    print("All intent tests passed.")
