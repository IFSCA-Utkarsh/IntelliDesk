from datetime import datetime, timedelta
import uuid

from utils.json_store import read_json, write_json
from audit import log_event

ROOMS = [
    {"name": "Room 1", "capacity": 11, "webex": "WebEx-1"},
    {"name": "Room 2", "capacity": 11, "webex": "WebEx-2"},
    {"name": "Room 3", "capacity": 11, "webex": "WebEx-3"},
    {"name": "Room 4", "capacity": 11, "webex": "WebEx-1"},
    {"name": "Room 5", "capacity": 11, "webex": "WebEx-2"},
    {"name": "Room 6", "capacity": 15, "webex": "WebEx-3"},
    {"name": "Room 7", "capacity": 15, "webex": "WebEx-4"},
    {"name": "Room 8", "capacity": 15, "webex": "WebEx-4"},
    {"name": "Room 9", "capacity": 21, "webex": "WebEx-2"},
    {"name": "Room 10", "capacity": 21, "webex": "WebEx-3"},
]

def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end

def find_room(meeting, existing):
    start = datetime.strptime(
        f'{meeting["date"]} {meeting["start_time"]}', "%d/%m %H:%M"
    )
    h, m = map(int, meeting["duration"].split(":"))
    end = start + timedelta(hours=h, minutes=m)

    for room in ROOMS:
        conflict = False
        for m in existing:
            if m["room"] != room["name"]:
                continue

            ms = datetime.strptime(
                f'{m["date"]} {m["start_time"]}', "%d/%m %H:%M"
            )
            mh, mm = map(int, m["duration"].split(":"))
            me = ms + timedelta(hours=mh, minutes=mm)

            if overlaps(start, end, ms, me):
                conflict = True
                break

        if not conflict and room["capacity"] >= meeting["participants"]:
            return room

    return None

def suggest_slots(meeting, meetings, attempts=3):
    base = datetime.strptime(
        f'{meeting["date"]} {meeting["start_time"]}', "%d/%m %H:%M"
    )

    suggestions = []
    for i in range(1, attempts + 1):
        candidate = meeting.copy()
        candidate_time = base + timedelta(minutes=30 * i)
        candidate["start_time"] = candidate_time.strftime("%H:%M")

        if find_room(candidate, meetings):
            suggestions.append({
                "date": candidate["date"],
                "start_time": candidate["start_time"]
            })

    return suggestions

def create_meeting(user, meeting):
    meetings = read_json("meetings.json")

    try:
        datetime.strptime(
            f'{meeting["date"]} {meeting["start_time"]}', "%d/%m %H:%M"
        )
    except ValueError:
        raise ValueError("Invalid meeting date/time")

    room = find_room(meeting, meetings)
    if not room:
        raise ValueError({
            "message": "No room available",
            "suggestions": suggest_slots(meeting, meetings)
        })

    record = {
        "id": f"MTG-{uuid.uuid4().hex[:6]}",
        "room": room["name"],
        "webex": room["webex"],
        "created_by": user["id"],
        "created_at": datetime.utcnow().isoformat(),
        **meeting
    }

    meetings.append(record)
    write_json("meetings.json", meetings)
    log_event(user["id"], "MEETING_CREATED", record["id"])
    return record
