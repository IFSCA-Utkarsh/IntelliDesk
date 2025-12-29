import requests
from config import settings

WEBEX_API_URL = "https://webexapis.com/v1/meetings"


def create_webex_meeting(
    webex_account: str,
    title: str,
    start_iso: str,
    duration_minutes: int
):
    """
    Creates a Webex meeting using the token mapped to a Webex account
    (e.g. WebEx-1, WebEx-2, etc.)
    """

    token = settings.WEBEX_ACCOUNT_TOKENS.get(webex_account)
    if not token:
        raise RuntimeError(f"No WebEx token configured for account: {webex_account}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "title": title,
        "start": start_iso,
        "duration": duration_minutes,
        "meetingType": "meetingCenter",  # IMPORTANT for bots/accounts
    }

    resp = requests.post(
        WEBEX_API_URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    if not resp.ok:
        raise RuntimeError(
            f"WebEx API error [{resp.status_code}]: {resp.text}"
        )

    data = resp.json()

    return {
        "webex_meeting_id": data["id"],
        "join_link": data["joinWebexMeetingUrl"],
    }
