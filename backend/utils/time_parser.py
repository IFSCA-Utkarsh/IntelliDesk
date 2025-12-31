from datetime import datetime, timedelta
import re

TIME_PATTERN = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", re.I)

def parse_relative_datetime(text: str):
    """
    Parses phrases like:
    - tomorrow 10am
    - today 3:30 pm
    Returns (date_str, time_str) or (None, None)
    """

    text = text.lower()
    now = datetime.now()

    if "tomorrow" in text:
        day = now + timedelta(days=1)
    elif "today" in text:
        day = now
    else:
        return None, None

    match = TIME_PATTERN.search(text)
    if not match:
        return None, None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    mer = match.group(3)

    if mer:
        mer = mer.lower()
        if mer == "pm" and hour < 12:
            hour += 12
        if mer == "am" and hour == 12:
            hour = 0

    date_str = day.strftime("%d/%m")
    time_str = f"{hour:02d}:{minute:02d}"

    return date_str, time_str


def parse_time_only(text: str):
    """
    Parses time-only input like:
    - 14:30
    - 2:30 pm
    Returns HH:MM or None
    """

    text = text.lower().strip()
    match = TIME_PATTERN.fullmatch(text)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    mer = match.group(3)

    if minute > 59:
        return None

    if mer:
        if hour > 12:
            return None
        mer = mer.lower()
        if mer == "pm" and hour < 12:
            hour += 12
        if mer == "am" and hour == 12:
            hour = 0

    if hour > 23:
        return None

    return f"{hour:02d}:{minute:02d}"
