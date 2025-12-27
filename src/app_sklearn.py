# src/app_sklearn.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback
import json
from pathlib import Path

from src.ticket_schema import SupportTicket
from src.rag_generate import generate_answer
from src.automation_rules import decide_action
from src.logger import log_ticket
from src.draft_store import (
    save_draft,
    load_draft,
    list_pending_approvals
)
from integration.decision_export import export_decision

# REAL GMAIL INTEGRATION
from automation.gmail_draft import create_draft
from automation.gmail_send import send_draft


app = FastAPI(title="RAG PoC - sklearn Retrieval")

DECISION_HISTORY_FILE = Path("integration/decision_history.jsonl")


# ----------------------------
# API Models
# ----------------------------
class ApprovalRequest(BaseModel):
    ticket_id: str


class OverrideRequest(BaseModel):
    ticket_id: str
    new_action: str  # SAVE_DRAFT | ESCALATE


# ----------------------------
# Core Endpoint
# ----------------------------
@app.post("/process_ticket")
def process_ticket(ticket: SupportTicket):
    try:
        # 1️⃣ Build RAG query
        full_query = f"Subject: {ticket.subject}\nMessage: {ticket.message}"

        rag_output = generate_answer(full_query)
        answer = rag_output["answer"]
        confidence = rag_output["confidence"]

        # 2️⃣ Decide action
        action = decide_action(confidence)

        # 3️⃣ Log decision
        log_ticket(
            ticket_id=ticket.ticket_id,
            email=ticket.user_email,
            confidence=confidence,
            action=action,
            answer=answer
        )

        # 4️⃣ Export decision
        if action in ["SAVE_DRAFT", "PENDING_APPROVAL"]:
            export_decision(
                ticket_id=ticket.ticket_id,
                user_email=ticket.user_email,
                subject=ticket.subject,
                answer=answer,
                confidence=confidence,
                action=action
            )

        draft_result = None
        gmail_draft_id = None

        # 5️⃣ Create Gmail Draft AND persist ID
        if action in ["SAVE_DRAFT", "PENDING_APPROVAL"]:
            gmail_draft = create_draft(
                to_email=ticket.user_email,
                subject=f"Re: {ticket.subject}",
                body=answer
            )

            gmail_draft_id = gmail_draft["draft_id"]

            draft_result = save_draft(
                ticket_id=ticket.ticket_id,
                email=ticket.user_email,
                body=answer,
                confidence=confidence,
                status="PENDING_APPROVAL",
                gmail_draft_id=gmail_draft_id  # ✅ REQUIRED
            )

        return {
            "ticket_id": ticket.ticket_id,
            "user_email": ticket.user_email,
            "draft_reply": answer,
            "confidence": confidence,
            "action": action,
            "draft_saved": draft_result,
            "gmail_draft_id": gmail_draft_id,
            "contexts_used": rag_output["contexts"]
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Approval Endpoints
# ----------------------------
@app.post("/approve_ticket")
def approve_ticket(req: ApprovalRequest):
    draft = load_draft(req.ticket_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    gmail_draft_id = draft.get("gmail_draft_id")
    if not gmail_draft_id:
        raise HTTPException(
            status_code=400,
            detail="No Gmail draft ID found for this ticket"
        )

    # ✅ ACTUAL SEND (ONLY HERE)
    send_result = send_draft(gmail_draft_id)

    save_draft(
        req.ticket_id,
        draft["email"],
        draft["draft"],
        draft["confidence"],
        status="SENT",
        gmail_draft_id=gmail_draft_id
    )

    return {
        "ticket_id": req.ticket_id,
        "status": "EMAIL_SENT",
        "gmail_message_id": send_result["message_id"]
    }


@app.post("/reject_ticket")
def reject_ticket(req: ApprovalRequest):
    draft = load_draft(req.ticket_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    save_draft(
        req.ticket_id,
        draft["email"],
        draft["draft"],
        draft["confidence"],
        status="REJECTED",
        gmail_draft_id=draft.get("gmail_draft_id")
    )

    return {
        "ticket_id": req.ticket_id,
        "status": "REJECTED"
    }


# ----------------------------
# Approval Queue
# ----------------------------
@app.get("/pending_approvals")
def pending_approvals():
    approvals = list_pending_approvals()
    return {
        "count": len(approvals),
        "items": approvals
    }


# ----------------------------
# Decision Status
# ----------------------------
@app.get("/decision_status/{ticket_id}")
def decision_status(ticket_id: str):
    if not DECISION_HISTORY_FILE.exists():
        raise HTTPException(status_code=404, detail="Decision history not found")

    history = []
    with open(DECISION_HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if record["ticket_id"] == ticket_id:
                history.append(record)

    if not history:
        raise HTTPException(status_code=404, detail="No decisions found for this ticket")

    return {
        "ticket_id": ticket_id,
        "latest_decision": history[-1],
        "history": history
    }


# ----------------------------
# Admin Override (SAFE)
# ----------------------------
@app.post("/override_decision")
def override_decision(req: OverrideRequest):
    draft = load_draft(req.ticket_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found for override")

    action = req.new_action.upper()
    if action not in ["SAVE_DRAFT", "ESCALATE"]:
        raise HTTPException(
            status_code=400,
            detail="AUTO_SEND is disabled for safety"
        )

    if action == "SAVE_DRAFT":
        save_draft(
            req.ticket_id,
            draft["email"],
            draft["draft"],
            draft["confidence"],
            status="ADMIN_DRAFT",
            gmail_draft_id=draft.get("gmail_draft_id")
        )
        status = "DRAFT_SAVED_BY_ADMIN"
    else:
        status = "ESCALATED_BY_ADMIN"

    log_ticket(
        ticket_id=req.ticket_id,
        email=draft["email"],
        confidence=draft["confidence"],
        action=f"ADMIN_OVERRIDE_{action}",
        answer=draft["draft"]
    )

    return {
        "ticket_id": req.ticket_id,
        "override_action": action,
        "status": status
    }
