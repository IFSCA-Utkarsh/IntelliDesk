from datetime import datetime, timedelta

ROOMS = [
    {"name": "Room 1", "capacity": 11, "webex": "WebEx-1"},
    {"name": "Room 2", "capacity": 11, "webex": "WebEx-2"},
    {"name": "Room 3", "capacity": 11, "webex": "WebEx-3"},
    {"name": "Room 4", "capacity": 11, "webex": "WebEx-1"},
    {"name": "Room 5", "capacity": 11, "webex": "WebEx-2"},
    {"name": "Room 6", "capacity": 15,  "webex": "WebEx-3"},
    {"name": "Room 7", "capacity": 15,  "webex": "WebEx-4"},
    {"name": "Room 8", "capacity": 15,  "webex": "WebEx-4"},
    {"name": "Room 9", "capacity": 21,  "webex": "WebEx-2"},
    {"name": "Room 10","capacity": 21,  "webex": "WebEx-3"},
]

def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end

def find_room(meeting, existing):
    start = datetime.strptime(
        f'{meeting["date"]} {meeting["start_time"]}', "%d/%m %H:%M"
    )
    h, m = map(int, meeting["duration"].split(":"))
    end = start + timedelta(hours=h, minutes=m)

    # smallest sufficient room first
    candidates = sorted(
        [r for r in ROOMS if r["capacity"] >= meeting["participants"]],
        key=lambda r: r["capacity"]
    )

    for room in candidates:
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

        if not conflict:
            return room

    return None