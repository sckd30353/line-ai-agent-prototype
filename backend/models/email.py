from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Attachment(BaseModel):
    name: str
    type: str
    size: int
    url: Optional[str] = None

class Email(BaseModel):
    id: str
    sender: str
    sender_name: str
    recipient: str
    subject: str
    content: str
    date: datetime
    read: bool = False
    category: str = "inbox"
    important: bool = False
    attachments: List[Attachment] = []

class EmailList(BaseModel):
    emails: List[Email]

class EmailQuery(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class EmailResponse(BaseModel):
    message: str
    emails: Optional[List[Email]] = None
    conversation_id: Optional[str] = None

class EmailUpdateRequest(BaseModel):
    id: str
    changes: Dict[str, Any]