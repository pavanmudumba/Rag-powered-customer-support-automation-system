# src/draft_store.py

from datetime import datetime
from pathlib import Path
import json
from typing import Optional, List, Dict

DRAFT_DIR = Path("drafts")
DRAFT_DIR.mkdir(exist_ok=True)


def save_draft(
    ticket_id: str,
    email: str,
    body: str,
    confidence: float,
    status: str = "SAVE_DRAFT",
    gmail_draft_id: Optional[str] = None
) -> str:
    """
    Persist a ticket draft to disk.
    This is the single source of truth for approval + Gmail workflow.
    """

    data = {
        "ticket_id": ticket_id,
        "email": email,
        "draft": body,
        "confidence": confidence,
        "status": status,
        "gmail_draft_id": gmail_draft_id,   # MUST be persisted
        "timestamp": datetime.utcnow().isoformat()
    }

    path = DRAFT_DIR / f"draft_{ticket_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return str(path)


def load_draft(ticket_id: str) -> Optional[Dict]:
    """
    Load a draft by ticket_id.
    """
    path = DRAFT_DIR / f"draft_{ticket_id}.json"
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_pending_approvals() -> List[Dict]:
    """
    Return drafts that still require human action.
    """
    drafts = []

    for path in DRAFT_DIR.glob("draft_*.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

            if data.get("status") in {
                "PENDING_APPROVAL",
                "SAVE_DRAFT",
                "ADMIN_DRAFT"
            }:
                drafts.append(data)

    return drafts
