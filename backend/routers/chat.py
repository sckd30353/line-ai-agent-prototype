from fastapi import APIRouter, Body, HTTPException
from backend.models.chat import ChatRequest, ChatResponse
from backend.line_agents.chat_agent import create_chat_agent
import asyncio
import uuid
import os
import logging
import sys

# 상위 디렉토리를 파이썬 경로에 추가 (config 모듈을 임포트하기 위함)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import (
    DEBUG, LOG_LEVEL, USE_WEB_SEARCH, WEB_SEARCH_LOCATION,
    SYSTEM_INSTRUCTIONS, WEB_SEARCH_INSTRUCTIONS, MODEL
)

# 로깅 설정 - 파일 저장 제외하고 터미널에만 표시
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 콘솔에만 출력
    ]
)
logger = logging.getLogger("chat_api")

router = APIRouter()

# 간단한 인메모리 대화 저장소 (개발용)
conversations = {}

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest = Body(...)):
    try:
        # 로그 시작
        logger.info(f"채팅 요청 수신: {request.message[:50]}...")
        
        # 대화 ID가 없으면 새로 생성
        conversation_id = request.conversation_id or str(uuid.uuid4())
        logger.info(f"대화 ID: {conversation_id}")
        
        # OpenAI 클라이언트 생성
        client = create_chat_agent()
        
        # 이전 대화 내용 가져오기 (또는 초기화)
        chat_history = conversations.get(conversation_id, [])
        logger.info(f"대화 기록 길이: {len(chat_history)}")
        
        try:
            if USE_WEB_SEARCH:
                # Responses API를 사용하여 웹 검색 기능 사용
                logger.info("Responses API로 웹 검색 시도 중...")
                
                # 간소화된 방식으로 API 호출 - 단일 메시지만 처리
                response = client.responses.create(
                    model=MODEL,  # 환경 변수에서 모델 가져오기
                    tools=[{
                        "type": "web_search",
                        "user_location": WEB_SEARCH_LOCATION
                    }],
                    tool_choice={"type": "web_search"},  # 웹 검색 도구를 강제로 사용
                    instructions=WEB_SEARCH_INSTRUCTIONS,
                    input=request.message
                )
                
                # Responses API에서 텍스트 응답 추출
                result = response.output_text
                logger.info("웹 검색 응답 생성 완료")
            else:
                # 웹 검색을 사용하지 않는 경우 기본 채팅 API 사용
                raise Exception("웹 검색 사용이 비활성화되어 있습니다. 기본 채팅 API로 대체합니다.")
            
        except Exception as api_error:
            # Responses API가 실패한 경우 기본 채팅 API로 대체
            logger.warning(f"Responses API 오류 발생: {str(api_error)}. 기본 채팅 API로 대체합니다.")
            
            # 시스템 메시지 정의
            system_message = {
                "role": "system", 
                "content": SYSTEM_INSTRUCTIONS
            }
            
            # API 호출을 위한 메시지 준비
            api_messages = [system_message]
            if chat_history:
                api_messages.extend(chat_history)
            api_messages.append({"role": "user", "content": request.message})
            
            # 기본 Chat API 호출
            logger.info("기본 Chat API 호출 중...")
            fallback_response = client.chat.completions.create(
                model=MODEL,
                messages=api_messages
            )
            
            # 응답 메시지 추출
            result = fallback_response.choices[0].message.content
            logger.info("기본 채팅 응답 생성 완료")
        
        # 대화 기록 저장
        chat_history.append({"role": "user", "content": request.message})
        chat_history.append({"role": "assistant", "content": result})
        conversations[conversation_id] = chat_history
        
        # 응답 생성
        response = ChatResponse(
            message=result,
            conversation_id=conversation_id
        )
        
        logger.info(f"응답 길이: {len(result)}")
        return response
    except Exception as e:
        # 예외 처리
        logger.error(f"채팅 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    logger.info("헬스 체크 요청")
    return {"status": "healthy"} 