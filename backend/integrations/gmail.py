import base64
import requests
from email.message import EmailMessage
from config import settings

TOKEN_URL = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

def _get_access_token():
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "refresh_token": settings.GMAIL_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        },
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = settings.GMAIL_SENDER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    token = _get_access_token()

    resp = requests.post(
        SEND_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={"raw": raw},
        timeout=10
    )
    resp.raise_for_status()
