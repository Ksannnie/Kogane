"""Local event storage using the computer's local date and time."""

import json
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path


SCHEDULE_FILE = Path(__file__).parent / "schedule.json"
EVENT_USAGE = "Try: add event YYYY-MM-DD [HH:MM] event title"
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
DATE_PHRASE = (
    r"(?:[0-9]{4}-[0-9]{2}-[0-9]{2}|today|tomorrow|"
    r"(?:(?:this|next)\s+)?(?:" + "|".join(WEEKDAYS) + r"))"
)


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


def _resolve_event_date(value, event_time=None, now=None):
    """Resolve relative dates locally; calendar weeks start on Monday."""
    value = " ".join(value.lower().split())
    now = now if now is not None else datetime.now()
    today = now.date()
    if value == "today":
        return today.isoformat()
    if value == "tomorrow":
        return (today + timedelta(days=1)).isoformat()

    words = value.split()
    if words[-1] in WEEKDAYS:
        weekday = WEEKDAYS.index(words[-1])
        if words[0] in ["this", "next"] and len(words) == 2:
            monday = today - timedelta(days=today.weekday())
            days = weekday + (7 if words[0] == "next" else 0)
            return (monday + timedelta(days=days)).isoformat()
        if len(words) == 1:
            days = (weekday - today.weekday()) % 7
            if days == 0 and event_time is not None and _parse_time(event_time) < now.time():
                days = 7
            return (today + timedelta(days=days)).isoformat()
    try:
        return _parse_date(value).isoformat()
    except ValueError as error:
        raise ValueError("That date is not valid. Use YYYY-MM-DD, today, tomorrow, or a weekday.") from error


def _match_natural_event(text):
    """Share the command grammar between routing and parsing; no data is read."""
    date_and_time = (
        rf"(?P<date>{DATE_PHRASE})(?:\s+at\s+(?P<time>.+?))?"
        r"(?:\s+(?P<week>next\s+week))?"
    )
    patterns = [
        ("reminder", rf"remind\s+me(?:\s+on)?\s+{date_and_time}\s+to\s+(?P<title>.+)"),
        (
            "deadline_reminder",
            rf"remind\s+me\s+(?P<title>.+?)(?:\s+is)?\s+due(?:\s+on)?\s+{date_and_time}[.!]?",
        ),
        ("assignment", rf"i\s+have\s+(?P<title>.+?)\s+due(?:\s+on)?\s+{date_and_time}[.!]?"),
        (
            "put",
            rf"put\s+(?P<title>.+?)(?:\s+that['’]s)?\s+due(?:\s+on)?\s+"
            rf"{date_and_time}\s+on\s+the\s+schedule[.!]?",
        ),
        ("add", rf"add\s+(?P<title>.+?)\s+due(?:\s+on)?\s+{date_and_time}[.!]?"),
        ("schedule", rf"schedule\s+(?P<title>.+?)\s+for\s+{date_and_time}[.!]?"),
        ("deadline", rf"(?P<title>.+?)(?:\s+is)?\s+due(?:\s+on)?\s+{date_and_time}[.!]?"),
    ]
    for kind, pattern in patterns:
        # Bare deadline statements must not consume questions or other commands.
        if kind == "deadline" and re.match(
            r"(?:what|why|how|when|where|who|can|could|should|would|is|are|do|does|did|"
            r"explain|tell|teach|open|launch|start|pull\s+up|search|remember|forget|delete|"
            r"set\s+mode|remind\s+me|put|add|schedule|i\s+have|[0-9]{4}-[0-9]{2}-[0-9]{2}|"
            r"(?:google|youtube|yt|github|git\s+hub)\s+search)\b",
            text.strip(),
            re.IGNORECASE,
        ):
            continue
        match = re.fullmatch(pattern, text.strip(), re.IGNORECASE)
        if match:
            return kind, match
    return None


def _is_dated_reminder(text):
    return re.match(
        rf"remind\s+me\s+(?:on(?:\s|$)|{DATE_PHRASE}(?:\s|$))",
        text.strip(),
        re.IGNORECASE,
    ) is not None


def is_natural_event_command(text):
    return _match_natural_event(text) is not None or _is_dated_reminder(text)


def parse_natural_event(event_text, now=None):
    """Return (date, time, title), or None; optional now fixes the local clock."""
    result = _match_natural_event(event_text)
    if result is None:
        if _is_dated_reminder(event_text):
            raise ValueError("Try: remind me tomorrow at 5pm to do TITLE, or use YYYY-MM-DD.")
        return None

    kind, match = result
    event_time = None
    if match["time"] is not None:
        event_time = _normalize_natural_time(match["time"])
    date_phrase = " ".join(match["date"].lower().split())
    if match["week"]:
        if date_phrase in WEEKDAYS:
            date_phrase = f"next {date_phrase}"
        elif date_phrase not in [f"next {weekday}" for weekday in WEEKDAYS]:
            raise ValueError("Use a weekday with 'next week', such as friday at 5pm next week.")
    event_date = _resolve_event_date(date_phrase, event_time, now)
    title = match["title"].strip()
    if kind == "reminder":
        title = re.sub(r"^do(?:\s+|$)", "", title, count=1, flags=re.IGNORECASE).strip()
    elif kind in ["put", "deadline_reminder", "deadline"]:
        title = re.sub(r"^my\s+", "", title, count=1, flags=re.IGNORECASE).strip()
    if not title:
        raise ValueError("Please give the event a title.")
    return event_date, event_time, title


def add_event(event_text, now=None):
    try:
        natural_event = parse_natural_event(event_text, now=now)
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
        "created_at": (now if now is not None else datetime.now()).isoformat(timespec="microseconds"),
    })
    save_events(events)
    return True, f"Added to schedule: {event_date} {event_time or 'All day'} — {title}"


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
