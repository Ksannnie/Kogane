"""Local event storage using the computer's local date and time."""

import json
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path


SCHEDULE_FILE = Path(__file__).parent / "schedule.json"
EVENT_USAGE = "Try: add event YYYY-MM-DD [HH:MM] event title"


def _parse_date(value):
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Use YYYY-MM-DD for the date.")
    return parsed


def _parse_time(value):
    parsed = time.fromisoformat(value)
    if parsed.strftime("%H:%M") != value:
        raise ValueError("Use HH:MM for the time.")
    return parsed


def load_events():
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
    except FileNotFoundError:
        return []
    except (ValueError, UnicodeError) as error:
        raise ValueError("The schedule file could not be read. It has not been changed.") from error

    # Reject damaged data instead of overwriting it with an empty schedule.
    try:
        if not isinstance(events, list):
            raise ValueError
        for event in events:
            _parse_date(event["date"])
            if event["time"] is not None:
                _parse_time(event["time"])
            if not isinstance(event["title"], str) or not event["title"].strip():
                raise ValueError
            datetime.fromisoformat(event["created_at"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("The schedule file contains invalid events. It has not been changed.") from error
    return events


def save_events(events):
    # Replace only after writing successfully, to protect the previous schedule.
    temporary_file = SCHEDULE_FILE.with_suffix(".json.tmp")
    try:
        with open(temporary_file, "w", encoding="utf-8") as file:
            json.dump(events, file, indent=4, ensure_ascii=False)
            file.write("\n")
        temporary_file.replace(SCHEDULE_FILE)
    finally:
        temporary_file.unlink(missing_ok=True)


def _normalize_natural_time(value):
    value = value.strip().lower()
    match = re.fullmatch(r"([0-9]{1,2})(?::([0-9]{2}))?\s*(am|pm)", value)
    if match:
        hour = int(match[1])
        minute = int(match[2] or "0")
        if 1 <= hour <= 12 and 0 <= minute <= 59:
            hour = hour % 12 + (12 if match[3] == "pm" else 0)
            return f"{hour:02d}:{minute:02d}"
    else:
        try:
            _parse_time(value)
            return value
        except ValueError:
            pass
    raise ValueError("That time is not valid. Try 5pm, 9:30am, or 17:00.")


def parse_natural_event(event_text):
    """Return (date, time, title) for a dated reminder/assignment, or None."""
    text = event_text.strip()
    reminder = re.fullmatch(
        r"remind\s+me\s+on\s+(?P<date>\S+)"
        r"(?:\s+at\s+(?P<time>.+?))?\s+to\s+(?P<title>.+)",
        text,
        re.IGNORECASE,
    )
    assignment = re.fullmatch(
        r"i\s+have\s+(?P<title>.+?)\s+due(?:\s+on)?\s+"
        r"(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})[.!]?",
        text,
        re.IGNORECASE,
    )
    match = reminder or assignment
    if match is None:
        if re.match(r"remind\s+me\s+on(?:\s|$)", text, re.IGNORECASE):
            raise ValueError("Try: remind me on YYYY-MM-DD [at 5pm] to do TITLE")
        return None

    event_date = match["date"]
    try:
        _parse_date(event_date)
    except ValueError as error:
        raise ValueError("That date is not valid. Use YYYY-MM-DD.") from error

    event_time = None
    title = match["title"].strip()
    if reminder:
        if reminder["time"] is not None:
            event_time = _normalize_natural_time(reminder["time"])
        title = re.sub(r"^do(?:\s+|$)", "", title, count=1, flags=re.IGNORECASE).strip()
    if not title:
        raise ValueError("Please give the event a title.")
    return event_date, event_time, title


def add_event(event_text):
    try:
        natural_event = parse_natural_event(event_text)
    except ValueError as error:
        return False, str(error)

    if natural_event is not None:
        event_date, event_time, title = natural_event
    else:
        # Preserve the original explicit add-event syntax and validation.
        parts = event_text.strip().split(maxsplit=1)
        if len(parts) < 2:
            return False, EVENT_USAGE

        event_date, title = parts
        try:
            _parse_date(event_date)
        except ValueError:
            return False, "That date is not valid. Use YYYY-MM-DD."

        event_time = None
        title_parts = title.split(maxsplit=1)
        if re.match(r"^[0-9]+:", title_parts[0]):
            event_time = title_parts[0]
            try:
                _parse_time(event_time)
            except ValueError:
                return False, "That time is not valid. Use HH:MM in 24-hour time."
            if len(title_parts) < 2:
                return False, EVENT_USAGE
            title = title_parts[1]

    events = load_events()
    events.append({
        "date": event_date,
        "time": event_time,
        "title": title,
        "created_at": datetime.now().isoformat(timespec="microseconds"),
    })
    save_events(events)
    return True, f"Added event: {event_date} {event_time or 'All day'} - {title}"


def _events_between(start_date, end_date=None):
    events = [
        event for event in load_events()
        if event["date"] >= start_date.isoformat()
        and (end_date is None or event["date"] <= end_date.isoformat())
    ]
    return sorted(events, key=lambda event: (event["date"], event["time"] or ""))


def list_upcoming_events():
    """Include all of today and future dates, with all-day events first."""
    return _events_between(date.today())


def list_today_events():
    today = date.today()
    return _events_between(today, today)


def list_tomorrow_events():
    tomorrow = date.today() + timedelta(days=1)
    return _events_between(tomorrow, tomorrow)


def list_week_events():
    today = date.today()
    return _events_between(today, today + timedelta(days=6))


def delete_event(event_number, displayed_events):
    """Delete by the number in the most recently displayed list, not file order."""
    try:
        index = int(event_number) - 1
    except (TypeError, ValueError):
        return False, "Use delete event NUMBER, with a number from your schedule."

    if displayed_events is None:
        return False, "Show your schedule first, then use delete event NUMBER."
    if index < 0 or index >= len(displayed_events):
        return False, "I could not find an event with that number in the displayed schedule."

    selected_event = displayed_events[index]
    events = load_events()
    if selected_event not in events:
        return False, "That event is no longer saved. Show your schedule again."

    events.remove(selected_event)
    save_events(events)
    return True, f"Deleted event {event_number}: {selected_event['title']}"
