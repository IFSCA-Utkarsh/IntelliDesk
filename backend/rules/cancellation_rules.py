from datetime import datetime, timedelta

def find_larger_room_meetings(cancelled, meetings):
    cs = datetime.strptime(
        f'{cancelled["date"]} {cancelled["start_time"]}', "%d/%m %H:%M"
    )
    h, m = map(int, cancelled["duration"].split(":"))
    ce = cs + timedelta(hours=h, minutes=m)

    results = []

    for m in meetings:
        if m["id"] == cancelled["id"]:
            continue

        ms = datetime.strptime(
            f'{m["date"]} {m["start_time"]}', "%d/%m %H:%M"
        )
        mh, mm = map(int, m["duration"].split(":"))
        me = ms + timedelta(hours=mh, minutes=mm)

        if cs < me and ms < ce:
            if m["participants"] <= 4:
                results.append(m)

    return results
