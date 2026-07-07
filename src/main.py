"""
FastAPI 엔트리포인트.

실행:
    uvicorn src.main:app --reload

사전 준비:
    1) .env 파일에 ANTHROPIC_API_KEY 설정
    2) python -m src.rag.ingest 로 RAG 인덱스 생성
"""
from fastapi import FastAPI
from pydantic import BaseModel

from src.agent.orchestrator import HRAgent

app = FastAPI(title="HR Agent + RAG API", version="0.1.0")
agent = HRAgent()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = agent.chat(session_id=req.session_id, user_message=req.message)
    return ChatResponse(answer=result["answer"])
