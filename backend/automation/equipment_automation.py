from integrations.gmail import send_email
from audit import log_event

def send_equipment_submission_reminder(user_email: str, equipment: dict):
    send_email(
        user_email,
        "Equipment Request Submitted",
        f"""
Your equipment request has been submitted.

Equipment: {equipment['name']}
Meeting ID: {equipment['meeting_id']}
Return By: {equipment['return_by']}
Secret Code: {equipment['secret_code']}
"""
    )

    log_event(
        equipment["assigned_to"],
        "EQUIPMENT_SUBMISSION_EMAIL_SENT",
        equipment["equipment_id"]
    )
