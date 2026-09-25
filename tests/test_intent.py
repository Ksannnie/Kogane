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
        ("memory help", ("memory_help", None)),
        ("mode help", ("mode_help", None)),
        ("open chrome", ("open_app", "chrome")),
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
