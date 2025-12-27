# integration/decision_export.py

import json
from datetime import datetime
from pathlib import Path

EXPORT_DIR = Path("integration")
EXPORT_DIR.mkdir(exist_ok=True)

HISTORY_FILE = EXPORT_DIR / "decision_history.jsonl"


def export_decision(
    ticket_id: str,
    user_email: str,
    subject: str,
    answer: str,
    confidence: float,
    action: str
):
    record = {
        "ticket_id": ticket_id,
        "user_email": user_email,
        "subject": subject,
        "answer": answer,
        "confidence": confidence,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    }

    # ✅ append-only history
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return str(HISTORY_FILE)
