from datetime import datetime
from pathlib import Path

OUTBOX_DIR = Path("outbox")
OUTBOX_DIR.mkdir(exist_ok=True)

def send_email(to_email: str, subject: str, body: str):
    """
    Simulated email sender.
    Writes email to outbox as a .txt file.
    """
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = OUTBOX_DIR / f"email_{ts}_{to_email.replace('@','_')}.txt"

    content = (
        f"TO: {to_email}\n"
        f"SUBJECT: {subject}\n"
        f"SENT_AT: {datetime.utcnow().isoformat()}\n\n"
        f"{body}"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return str(filename)
