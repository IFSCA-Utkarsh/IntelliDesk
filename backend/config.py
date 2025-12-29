import os
from pathlib import Path

# ===============================
# ENV FILE LOADER
# ===============================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def load_env():
    """
    Custom .env loader with safe quote stripping.
    Supports:
      KEY=value
      KEY="value"
      KEY='value'
    """
    if not ENV_FILE.exists():
        raise RuntimeError(".env file missing in backend/")

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")

            os.environ[key.strip()] = value


# Load environment variables ONCE
load_env()


# ===============================
# SETTINGS
# ===============================

class Settings:
    """
    Central configuration for IntelliDesk backend.
    Fails fast if critical config is missing.
    """

    # -------------------------------
    # JWT AUTH
    # -------------------------------
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGO: str = os.getenv("JWT_ALGO", "HS256")

    # -------------------------------
    # WEBEX CONFIG
    # -------------------------------
    WEBEX_ACCOUNT_TOKENS = {
        "WebEx-1": os.getenv("WEBEX_1_TOKEN"),
        "WebEx-2": os.getenv("WEBEX_2_TOKEN"),
        "WebEx-3": os.getenv("WEBEX_3_TOKEN"),
        "WebEx-4": os.getenv("WEBEX_4_TOKEN"),
    }

    # -------------------------------
    # GMAIL OAUTH
    # -------------------------------
    GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
    GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")
    GMAIL_SENDER = os.getenv("GMAIL_SENDER")

    # -------------------------------
    # MISC
    # -------------------------------
    HR_EMAIL = os.getenv("HR_EMAIL", "hr@company.com")

    # -------------------------------
    # VALIDATION
    # -------------------------------
    def validate(self):
        # JWT validation
        if not self.JWT_SECRET:
            raise RuntimeError("JWT_SECRET is missing or empty")

        if not self.JWT_ALGO:
            raise RuntimeError("JWT_ALGO is missing")

        # WebEx validation
        missing_webex = [
            name for name, token in self.WEBEX_ACCOUNT_TOKENS.items()
            if not token
        ]
        if missing_webex:
            raise RuntimeError(
                f"Missing WebEx token(s) for accounts: {', '.join(missing_webex)}"
            )

        # Gmail validation
        if not all([
            self.GMAIL_CLIENT_ID,
            self.GMAIL_CLIENT_SECRET,
            self.GMAIL_REFRESH_TOKEN,
            self.GMAIL_SENDER
        ]):
            raise RuntimeError("Incomplete Gmail OAuth configuration")


# ===============================
# INITIALIZE & VALIDATE
# ===============================

settings = Settings()
settings.validate()
