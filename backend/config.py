"""
설정 정보를 관리하는 모듈입니다.
.env 파일에서 환경 변수를 로드하고 애플리케이션 전체에서 사용할 설정값을 제공합니다.
"""
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 설정
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# 디버그 설정
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 로깅 설정
LOG_LEVEL = "INFO" if DEBUG else "WARNING"

# 웹 검색 도구 설정
USE_WEB_SEARCH = os.getenv("USE_WEB_SEARCH", "true").lower() == "true"

# 사용자 위치 설정
WEB_SEARCH_LOCATION = {
    "type": "approximate",
    "country": os.getenv("WEB_SEARCH_COUNTRY", "KR"),
    "city": os.getenv("WEB_SEARCH_CITY", "Seoul"),
    "region": os.getenv("WEB_SEARCH_REGION", "Seoul"),
    "timezone": os.getenv("WEB_SEARCH_TIMEZONE", "Asia/Seoul")
}

# 시스템 지시 메시지
SYSTEM_INSTRUCTIONS = """You are Line AI Assistant, a helpful, friendly, and professional assistant developed by Line Plus. 
You can assist with a wide range of tasks and provide information on various topics.

When the user asks about current events, weather, stock prices, or other information that might require up-to-date knowledge,
use the web search tool to find relevant information. Also use web search when the user explicitly asks you to search the web.

Respond in the same language that the user uses. If the user speaks Korean, respond in Korean. If the user speaks English, respond in English.

Always be helpful, accurate, and respectful in your responses."""

# 웹 검색 지시 메시지
WEB_SEARCH_INSTRUCTIONS = """웹에서 최신 정보를 검색하여 사용자의 질문에 한국어로 답변하세요. 
사용자가 웹 검색을 요청하면 반드시 웹 검색을 수행하세요."""

# 이메일 관련 설정
EMAIL_INSTRUCTIONS = """당신은 이메일 관리를 도와주는 Line AI Assistant입니다. 
사용자의 이메일에 대한 질문에 답변하고, 이메일을 관리하는 작업을 수행합니다.

다음과 같은 작업을 수행할 수 있습니다:
- 특정 카테고리(받은편지함, 스팸 등)의 이메일 조회
- 특정 날짜의 이메일 조회
- 스팸 메일 정리 및 제안
- 중요 이메일 식별 및 요약
- 이메일 내용 요약

제공된 이메일 데이터를 기반으로 최대한 정확하게 답변하세요."""

# 서버 설정
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# API 경로 설정
API_PREFIX = "/api"
CHAT_ENDPOINT = f"{API_PREFIX}/chat" 
EMAIL_ENDPOINT = f"{API_PREFIX}/email"