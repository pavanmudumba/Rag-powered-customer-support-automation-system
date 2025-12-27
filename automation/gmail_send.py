# automation/gmail_send.py

import base64
from automation.gmail_service import get_gmail_service

def send_draft(draft_id: str):
    service = get_gmail_service()

    sent = service.users().drafts().send(
        userId="me",
        body={"id": draft_id}
    ).execute()

    return {
        "message_id": sent["id"],
        "thread_id": sent.get("threadId")
    }
