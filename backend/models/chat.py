"""
테스트 전용 모델 - React 클라이언트에서는 직접 사용하지 않음
agent.py의 통합 에이전트 기능으로 대체됨
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str  # "user" 또는 "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str 