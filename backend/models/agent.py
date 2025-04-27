"""
React 클라이언트에서 사용하는 주요 모델
통합 에이전트 기능을 위한 요청 및 응답 모델
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AgentRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class AgentResponse(BaseModel):
    message: str
    conversation_id: str
    source_type: Optional[str] = None  # "chat", "web_search", "email" 등 응답 소스 표시 (선택적)