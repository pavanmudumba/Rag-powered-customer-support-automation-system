from pydantic import BaseModel
from typing import Optional

class SupportTicket(BaseModel):
    ticket_id: Optional[str] = None
    user_email: str
    subject: str
    message: str
