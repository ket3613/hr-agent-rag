"""
환경 변수 기반 설정 모듈.

.env 파일 또는 실제 환경 변수에서 값을 읽어옵니다.
자세한 설정 항목은 .env.example 을 참고하세요.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# Anthropic (Claude) API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

# RAG / Vector DB
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "hr_docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# 문서 폴더
# ⚠️ 기본값은 데모용 샘플 문서 폴더입니다.
# 운영 환경에서는 이 값을 실제(비공개) 사내 문서 폴더 경로로 교체하세요.
DOCS_DIR = os.getenv("DOCS_DIR", "data/sample_docs")
