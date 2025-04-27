from fastapi import APIRouter, Body, HTTPException
import json
import os
import logging
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.models.chat import ChatRequest, ChatResponse
from backend.models.email import EmailQuery, EmailResponse, Email
from backend.line_agents.chat_agent import create_chat_agent
from backend.config import MODEL, DEBUG, LOG_LEVEL, WEB_SEARCH_LOCATION, SYSTEM_INSTRUCTIONS

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("agent_api")

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

async def process_general_chat(query: str):
    """일반 대화 처리 함수"""
    logger.info(f"일반 대화 처리 - 쿼리: {query}")
    
    client = create_chat_agent()
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": query}
        ]
    )
    
    return response.choices[0].message.content

async def process_web_search(query: str):
    """웹 검색 처리 함수"""
    logger.info(f"웹 검색 처리 - 쿼리: {query}")
    
    client = create_chat_agent()
    
    response = client.responses.create(
        model=MODEL,
        tools=[{
            "type": "web_search",
            "user_location": WEB_SEARCH_LOCATION
        }],
        instructions="웹에서 최신 정보를 검색하여 사용자의 질문에 답변하세요.",
        input=query
    )
    
    return response.output_text

async def process_email_query(query: str, filter_type: Optional[str] = None, filter_value: Optional[str] = None):
    """이메일 쿼리 처리 함수"""
    logger.info(f"이메일 쿼리 처리 - 쿼리: {query}, 필터 타입: {filter_type}, 필터 값: {filter_value}")
    
    # 이메일 데이터 로드
    emails = load_emails()
    
    # 필터링
    filtered_emails = emails
    
    if filter_type and filter_value:
        if filter_type == "date":
            if filter_value.lower() == "today":
                today = datetime.today().strftime("%Y-%m-%d")
                filtered_emails = [e for e in emails if e.get("date", "").startswith(today)]
            # 다른 날짜 필터 로직 추가 가능
        elif filter_type == "category":
            filtered_emails = [e for e in emails if e.get("category") == filter_value]
        elif filter_type == "importance":
            is_important = filter_value.lower() == "important"
            filtered_emails = [e for e in emails if e.get("important") == is_important]
        elif filter_type == "read":
            is_read = filter_value.lower() == "read"
            filtered_emails = [e for e in emails if e.get("read") == is_read]
    
    # 이메일 데이터 요약 (컨텍스트 크기 제한을 위해)
    email_context = []
    for email in filtered_emails:
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
        
        제공된 이메일 데이터를 기반으로 최대한 정확하게 답변하세요.
        
        가능하면 이메일 목록을 표 형식으로 보기 좋게 정리해서 보여주세요."""
    }
    
    # API 호출을 위한 메시지 준비
    api_messages = [
        system_message,
        {"role": "user", "content": f"다음은 내 이메일 목록입니다:\n\n{json.dumps(email_context, ensure_ascii=False, indent=2)}\n\n{query}"}
    ]
    
    # OpenAI API 호출
    response = client.chat.completions.create(
        model=MODEL,
        messages=api_messages
    )
    
    # 응답 메시지 추출
    result = response.choices[0].message.content
    
    return result

@router.post("/", response_model=ChatResponse)
async def agent_endpoint(request: ChatRequest = Body(...)):
    """
    통합 에이전트 엔드포인트 - 모든 사용자 질문을 처리합니다.
    """
    try:
        logger.info(f"에이전트 요청 수신: {request.message[:50]}... (대화 ID: {request.conversation_id})")
        
        # 대화 ID가 없으면 새로 생성
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # OpenAI 클라이언트 생성
        client = create_chat_agent()
        
        # 함수 정의
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "handle_general_chat",
                    "description": "일반적인 대화나 질문에 답변합니다. 최신 정보가 필요하지 않은 일반적인 질문이나 대화에 사용합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "사용자의 질문이나 대화 내용"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "handle_web_search",
                    "description": "최신 정보, 뉴스, 날씨, 주가 등 웹 검색이 필요한 질문에 답변합니다. 사용자가 명시적으로 '검색'을 요청하거나 최신 정보가 필요한 질문에 사용합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {"type": "string", "description": "검색할 쿼리"}
                        },
                        "required": ["search_query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "handle_email_query",
                    "description": "이메일 조회, 관리, 요약 등 이메일 관련 작업을 처리합니다. '이메일', '메일', '스팸' 등의 단어가 포함된 요청에 사용합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email_query": {"type": "string", "description": "이메일 관련 쿼리"},
                            "filter_type": {
                                "type": "string", 
                                "enum": ["date", "category", "importance", "read"], 
                                "description": "필터링 유형"
                            },
                            "filter_value": {"type": "string", "description": "필터 값 (오늘, 스팸, 중요 등)"}
                        },
                        "required": ["email_query"]
                    }
                }
            }
        ]
        
        # 도구 선택을 위한 첫 번째 API 호출
        tool_selection_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "사용자의 질문을 분석하여 적절한 기능을 호출하세요."},
                {"role": "user", "content": request.message}
            ],
            tools=functions,
            tool_choice="auto"  # AI가 적절한 함수를 선택하도록 함
        )
        
        # 도구 호출 응답 처리
        message = tool_selection_response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # 함수 호출에 따른 처리
            if function_name == "handle_general_chat":
                result = await process_general_chat(function_args["query"])
            elif function_name == "handle_web_search":
                result = await process_web_search(function_args["search_query"])
            elif function_name == "handle_email_query":
                result = await process_email_query(
                    function_args["email_query"],
                    function_args.get("filter_type"),
                    function_args.get("filter_value")
                )
            else:
                result = "지원하지 않는 기능입니다."
        else:
            # 기본 응답
            result = message.content or await process_general_chat(request.message)
        
        # 응답 생성
        response = ChatResponse(
            message=result,
            conversation_id=conversation_id
        )
        
        logger.info(f"에이전트 응답 완료 - 응답 길이: {len(result)}")
        return response
    except Exception as e:
        logger.error(f"에이전트 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    logger.info("헬스 체크 요청")
    return {"status": "healthy"}