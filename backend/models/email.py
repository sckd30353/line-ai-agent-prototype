"""
테스트 전용 모델 - React 클라이언트에서는 직접 사용하지 않음
agent.py의 통합 에이전트 기능으로 대체됨
이메일 관련 기능은 agent 라우터를 통해 통합적으로 처리됨
"""
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
    sender_name: Optional[str] = None
    recipient: str
    subject: str
    content: str
    date: str
    read: bool = False
    category: str = "inbox"
    important: bool = False
    attachments: List[Dict[str, Any]] = []

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