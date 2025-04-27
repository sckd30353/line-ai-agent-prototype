from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys

# 상위 디렉토리를 파이썬 경로에 추가 (config 모듈을 임포트하기 위함)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.config import (
    SERVER_HOST, SERVER_PORT, DEBUG, LOG_LEVEL, API_PREFIX
)
from backend.routers import chat, email

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("server")

# FastAPI 앱 생성
app = FastAPI(title="Line AI Agent")
logger.info("FastAPI 앱 생성 완료")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS 미들웨어 설정 완료")

# 라우터 등록
app.include_router(chat.router, prefix=f"{API_PREFIX}/chat", tags=["chat"])
app.include_router(email.router, prefix=f"{API_PREFIX}/email", tags=["email"])
logger.info(f"채팅 라우터 등록 완료 (경로: {API_PREFIX}/chat)")

@app.get("/")
async def read_root():
    logger.info("루트 경로 접속")
    return {"message": "Line AI Agent API"}

if __name__ == "__main__":
    import uvicorn
    logger.info("서버 시작 중...")
    uvicorn.run("app:app", host=SERVER_HOST, port=SERVER_PORT, reload=True) 