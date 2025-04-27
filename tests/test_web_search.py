import requests
import json
import time
import logging
import os
import sys

# 상위 디렉토리를 파이썬 경로에 추가 (config 모듈을 임포트하기 위함)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.config import (
    LOG_LEVEL, API_PREFIX, DEBUG
)

# 로깅 설정 - 터미널에만 출력
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("agent_test")

# API 엔드포인트 설정
BASE_URL = "http://localhost:8000"  # 서버 주소와 포트에 맞게 수정하세요
AGENT_URL = f"{BASE_URL}{API_PREFIX}/agent"

def test_agent():
    """통합 에이전트 기능을 테스트합니다."""
    
    logger.info("통합 에이전트 테스트를 시작합니다...")
    logger.info(f"디버그 모드: {DEBUG}")
    logger.info(f"로그 레벨: {LOG_LEVEL}")
    logger.info(f"API 엔드포인트: {AGENT_URL}")
    
    # 테스트할 질문 목록
    test_questions = [
        "안녕하세요",
        "오늘 날씨 알려줘",
        "오늘 온 이메일을 알려줘",
    ]
    
    # 각 질문에 대해 테스트 실행
    conversation_id = None
    
    for i, question in enumerate(test_questions):
        logger.info(f"[테스트 {i+1}] 질문: '{question}'")
        
        # 요청 데이터 준비
        request_data = {
            "message": question
        }
        
        # 대화 ID가 있으면 포함
        if conversation_id:
            request_data["conversation_id"] = conversation_id
            
        logger.info(f"요청 데이터: {json.dumps(request_data, ensure_ascii=False)}")
        
        # 요청 시작 시간 기록
        start_time = time.time()
        
        try:
            # API 요청 보내기
            response = requests.post(
                AGENT_URL,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            # 응답 시간 계산
            elapsed_time = time.time() - start_time
            
            # 응답 출력
            logger.info(f"상태 코드: {response.status_code}")
            logger.info(f"응답 시간: {elapsed_time:.2f}초")
            
            if response.status_code == 200:
                response_data = response.json()
                conversation_id = response_data.get("conversation_id")
                logger.info(f"대화 ID: {conversation_id}")
                logger.info(f"응답: {response_data.get('message')}")
            else:
                logger.error(f"오류 응답: {response.text}")
                
        except Exception as e:
            logger.error(f"요청 중 오류 발생: {str(e)}")
    
    logger.info("테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_agent()