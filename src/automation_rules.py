# src/automation_rules.py

def decide_action(confidence: float):
    """
    Day-4 rules:
    - High confidence → PENDING_APPROVAL
    - Medium confidence → SAVE_DRAFT
    - Low confidence → ESCALATE
    """
    if confidence >= 0.75:
        return "PENDING_APPROVAL"
    elif confidence >= 0.40:
        return "SAVE_DRAFT"
    else:
        return "ESCALATE"
