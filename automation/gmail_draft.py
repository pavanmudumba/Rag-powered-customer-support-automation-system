# automation/gmail_draft.py

import base64
from email.message import EmailMessage
from automation.gmail_service import get_gmail_service


def create_draft(to_email: str, subject: str, body: str):
    """
    Create a REAL Gmail draft using Gmail API.
    Does NOT send email.
    """

    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to_email
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    draft_body = {
        "message": {
            "raw": encoded_message
        }
    }

    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=draft_body)
        .execute()
    )

    return {
        "draft_id": draft["id"],
        "message_id": draft["message"]["id"]
    }
