from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": "37548767318-f7bfubsmb1bhdv5970hrhb8qf1oilqpn.apps.googleusercontent.com",
            "client_secret": "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",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    SCOPES
)

creds = flow.run_local_server(port=0)
print("REFRESH TOKEN:", creds.refresh_token)
