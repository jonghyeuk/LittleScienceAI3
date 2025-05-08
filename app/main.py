# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from app.routes import query_router
from app.utils.cleaner import setup_logging

app = FastAPI(
    title="LittleScienceAI 도우미",
    description="고등학생을 위한 과학소논문 주제선정 서비스 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 구체적인 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)

# 라우터 포함
app.include_router(query_router.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "LittleScienceAI 도우미 API에 오신 것을 환영합니다!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
