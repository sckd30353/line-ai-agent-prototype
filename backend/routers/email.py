from fastapi import APIRouter, Body, HTTPException, Query
from typing import List, Optional
import json
import os
import uuid
import logging
from datetime import datetime, timedelta
import sys

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.models.email import Email, EmailList, EmailQuery, EmailResponse, EmailUpdateRequest
from backend.config import MODEL, DEBUG, LOG_LEVEL

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("email_api")

router = APIRouter()

# 이메일 데이터 파일 경로
EMAIL_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datas", "emails.json")

def load_emails():
    """이메일 데이터 로드"""
    try:
        if os.path.exists(EMAIL_DATA_PATH):
            with open(EMAIL_DATA_PATH, "r", encoding="utf-8") as f:
                emails = json.load(f)
            return emails
        else:
            logger.warning(f"이메일 데이터 파일이 없습니다: {EMAIL_DATA_PATH}")
            return []
    except Exception as e:
        logger.error(f"이메일 데이터 로드 중 오류: {str(e)}")
        return []

def save_emails(emails):
    """이메일 데이터 저장"""
    try:
        # data 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(EMAIL_DATA_PATH), exist_ok=True)
        
        with open(EMAIL_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(emails, f, ensure_ascii=False, indent=2)
        logger.info("이메일 데이터 저장 완료")
    except Exception as e:
        logger.error(f"이메일 데이터 저장 중 오류: {str(e)}")

@router.get("/", response_model=EmailList)
async def get_emails(
    category: Optional[str] = None,
    important: Optional[bool] = None,
    read: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    이메일 목록을 가져옵니다. 필터링 옵션을 제공합니다.
    """
    logger.info(f"이메일 목록 요청 - 카테고리: {category}, 중요: {important}, 읽음: {read}")
    
    emails = load_emails()
    
    # 필터링
    if category:
        emails = [email for email in emails if email.get("category") == category]
    if important is not None:
        emails = [email for email in emails if email.get("important") == important]
    if read is not None:
        emails = [email for email in emails if email.get("read") == read]
    
    # 정렬 (날짜 내림차순)
    emails.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # 페이지네이션
    paginated_emails = emails[offset:offset+limit]
    
    logger.info(f"이메일 {len(paginated_emails)}개 반환")
    return EmailList(emails=paginated_emails)

@router.get("/{email_id}", response_model=Email)
async def get_email(email_id: str):
    """
    특정 ID의 이메일을 가져옵니다.
    """
    logger.info(f"이메일 상세 요청 - ID: {email_id}")
    
    emails = load_emails()
    
    # ID로 이메일 찾기
    email = next((e for e in emails if e.get("id") == email_id), None)
    
    if not email:
        logger.warning(f"이메일을 찾을 수 없음 - ID: {email_id}")
        raise HTTPException(status_code=404, detail="Email not found")
    
    # 읽음 상태 업데이트
    if not email.get("read"):
        email["read"] = True
        for i, e in enumerate(emails):
            if e.get("id") == email_id:
                emails[i] = email
                break
        save_emails(emails)
    
    logger.info(f"이메일 반환 - ID: {email_id}")
    return email

@router.post("/query", response_model=EmailResponse)
async def query_emails(request: EmailQuery = Body(...)):
    """
    AI를 사용하여 이메일 쿼리를 처리합니다.
    """
    from openai import OpenAI
    from backend.line_agents.chat_agent import create_chat_agent
    
    logger.info(f"이메일 쿼리 요청: {request.query}")
    
    # 대화 ID가 없으면 새로 생성
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # 이메일 데이터 로드
    emails = load_emails()
    
    # 이메일 데이터 요약 (컨텍스트 크기 제한을 위해)
    email_context = []
    for email in emails:
        summary = {
            "id": email.get("id"),
            "sender": email.get("sender"),
            "sender_name": email.get("sender_name"),
            "subject": email.get("subject"),
            "date": email.get("date"),
            "category": email.get("category"),
            "read": email.get("read"),
            "important": email.get("important"),
            "content_preview": email.get("content")[:100] + "..." if len(email.get("content", "")) > 100 else email.get("content", "")
        }
        email_context.append(summary)
    
    # OpenAI 클라이언트 생성
    client = create_chat_agent()
    
    # 시스템 메시지 정의
    system_message = {
        "role": "system", 
        "content": """당신은 이메일 관리를 도와주는 Line AI Assistant입니다. 
        사용자의 이메일에 대한 질문에 답변하고, 이메일을 관리하는 작업을 수행합니다.
        
        사용자가 특정 카테고리(받은편지함, 스팸 등)의 이메일을 요청하면 해당 카테고리의 이메일만 보여주세요.
        사용자가 오늘 또는 특정 날짜의 이메일을 요청하면 해당 날짜의 이메일만 보여주세요.
        사용자가 스팸 메일을 정리해달라고 하면, 스팸으로 분류된 이메일들의 목록을 보여주고 어떻게 처리할지 제안하세요.
        
        제공된 이메일 데이터를 기반으로 최대한 정확하게 답변하세요."""
    }
    
    # API 호출을 위한 메시지 준비
    api_messages = [
        system_message,
        {"role": "user", "content": f"다음은 내 이메일 목록입니다:\n\n{json.dumps(email_context, ensure_ascii=False, indent=2)}\n\n{request.query}"}
    ]
    
    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model=MODEL,
            messages=api_messages
        )
        
        # 응답 메시지 추출
        result = response.choices[0].message.content
        
        logger.info("이메일 쿼리 응답 생성 완료")
        
        # 응답 생성
        return EmailResponse(
            message=result,
            conversation_id=conversation_id
        )
    except Exception as e:
        logger.error(f"이메일 쿼리 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email query error: {str(e)}")

@router.patch("/{email_id}", response_model=Email)
async def update_email(email_id: str, request: EmailUpdateRequest = Body(...)):
    """
    이메일을 업데이트합니다 (읽음 상태, 중요 표시, 카테고리 등).
    """
    logger.info(f"이메일 업데이트 요청 - ID: {email_id}")
    
    emails = load_emails()
    
    # ID로 이메일 찾기
    email_index = None
    for i, email in enumerate(emails):
        if email.get("id") == email_id:
            email_index = i
            break
    
    if email_index is None:
        logger.warning(f"이메일을 찾을 수 없음 - ID: {email_id}")
        raise HTTPException(status_code=404, detail="Email not found")
    
    # 이메일 업데이트
    for key, value in request.changes.items():
        if key in ["read", "important", "category"]:
            emails[email_index][key] = value
    
    # 데이터 저장
    save_emails(emails)
    
    logger.info(f"이메일 업데이트 완료 - ID: {email_id}")
    return emails[email_index]

@router.delete("/{email_id}", status_code=204)
async def delete_email(email_id: str):
    """
    이메일을 삭제합니다.
    """
    logger.info(f"이메일 삭제 요청 - ID: {email_id}")
    
    emails = load_emails()
    
    # 삭제 전 이메일 수
    original_count = len(emails)
    
    # 이메일 필터링 (삭제할 이메일 제외)
    filtered_emails = [email for email in emails if email.get("id") != email_id]
    
    # 이메일이 실제로 삭제되었는지 확인
    if len(filtered_emails) == original_count:
        logger.warning(f"이메일을 찾을 수 없음 - ID: {email_id}")
        raise HTTPException(status_code=404, detail="Email not found")
    
    # 데이터 저장
    save_emails(filtered_emails)
    
    logger.info(f"이메일 삭제 완료 - ID: {email_id}")