# automation/gmail_service.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PATH = "automation/token.json"

def get_gmail_service():
    if not os.path.exists(TOKEN_PATH):
        raise RuntimeError("token.json not found. Run gmail_auth.py first.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("gmail", "v1", credentials=creds)
    return service
