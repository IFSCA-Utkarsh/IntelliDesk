from datetime import datetime
from integrations.webex import create_webex_meeting
from integrations.gmail import send_email
from audit import log_event


def handle_meeting_automation(meeting: dict, user_email: str):
    """
    Handles post-meeting creation automation:
    - Offline → email only
    - Online → Webex meeting creation + email
    """

    # ---------------- OFFLINE MEETING ----------------
    if meeting["type"] == "offline":
        send_email(
            user_email,
            "Offline Meeting Confirmed",
            f"""
Meeting: {meeting['title']}
Date: {meeting['date']}
Time: {meeting['start_time']}
Room: {meeting['room']}
"""
        )

        log_event(
            meeting["created_by"],
            "OFFLINE_MEETING_EMAIL_SENT",
            meeting["id"]
        )
        return

    # ---------------- ONLINE MEETING ----------------
    start_iso = datetime.strptime(
        f"{meeting['date']} {meeting['start_time']}",
        "%d/%m %H:%M"
    ).isoformat()

    hours, minutes = map(int, meeting["duration"].split(":"))
    duration_minutes = hours * 60 + minutes

    webex = create_webex_meeting(
        webex_account=meeting["webex"],  # WebEx-1 / WebEx-2 / WebEx-3 / WebEx-4
        title=meeting["title"],
        start_iso=start_iso,
        duration_minutes=duration_minutes,
    )

    meeting["webex_meeting_id"] = webex["webex_meeting_id"]
    meeting["webex_join_link"] = webex["join_link"]

    send_email(
        user_email,
        "Online Meeting Confirmed",
        f"""
Meeting: {meeting['title']}
Date: {meeting['date']}
Time: {meeting['start_time']}
Room: {meeting['room']}

WebEx Join Link:
{webex['join_link']}
"""
    )

    log_event(
        meeting["created_by"],
        "WEBEX_CREATED_AND_EMAIL_SENT",
        meeting["id"]
    )
