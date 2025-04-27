from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import sys

# 상위 디렉토리를 파이썬 경로에 추가 (config 모듈을 임포트하기 위함)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import API_KEY, LOG_LEVEL, DEBUG

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("chat_agent")

def create_chat_agent():
    """
    OpenAI의 웹 검색 기능을 사용하는 클라이언트를 생성합니다.
    
    Returns:
        OpenAI client: OpenAI API 클라이언트 객체
    """
    api_key = API_KEY
    if not api_key:
        logger.error("OpenAI API 키가 없습니다.")
        raise ValueError("OpenAI API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
    
    if DEBUG:
        logger.info(f"API 키 확인: {'유효함' if api_key else '유효하지 않음'}")
    
    # OpenAI 클라이언트 생성
    try:
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI 클라이언트 생성 성공")
        return client
    except Exception as e:
        logger.error(f"OpenAI 클라이언트 생성 실패: {str(e)}")
        raise 