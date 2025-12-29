from integrations.gmail import send_email
from audit import log_event
from config import settings

def notify_hr(organizer_email, meeting, items):
    body = f"""
HR Material Request

Meeting: {meeting['title']}
Date: {meeting['date']}
Time: {meeting['start_time']}
Room: {meeting['room']}

Requested Items:
{items}
"""

    send_email(
        to=settings.HR_EMAIL,
        subject="HR Materials Request",
        body=body
    )

    send_email(
        to=organizer_email,
        subject="HR Request Submitted",
        body=body
    )

    log_event(meeting["created_by"], "HR_REQUEST_SENT", meeting["id"])
