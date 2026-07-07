"""
사내 문서를 청크로 분할하고 임베딩하여 Chroma 벡터스토어에 저장하는 색인 스크립트.

⚠️ data/sample_docs 안의 문서는 데모용 샘플 데이터입니다.
운영 환경에서는 .env의 DOCS_DIR을 실제 사내 규정 문서(비공개) 폴더 경로로
바꾸어 사용하세요. 이 코드는 문서 내용을 어떤 식으로든 외부로 전송하지 않고
로컬 Chroma 인덱스에만 저장합니다.

실행 방법:
    python -m src.rag.ingest
"""
import glob
import os

import chromadb
from chromadb.utils import embedding_functions

from src.config import CHROMA_DIR, COLLECTION_NAME, DOCS_DIR, EMBEDDING_MODEL


def load_documents(docs_dir: str = DOCS_DIR) -> list[dict]:
    """docs_dir 아래의 모든 마크다운 문서를 읽어옵니다."""
    docs = []
    pattern = os.path.join(docs_dir, "**/*.md")
    for path in sorted(glob.glob(pattern, recursive=True)):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        docs.append({"source": os.path.basename(path), "text": text})
    return docs


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> list[str]:
    """간단한 문자 길이 기준 슬라이딩 윈도우 청킹."""
    chunks = []
    start = 0
    text = text.strip()
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def build_index() -> None:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # 컬렉션이 없으면 무시

    collection = client.create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_fn
    )

    documents = load_documents()
    if not documents:
        print(f"'{DOCS_DIR}' 에서 색인할 .md 문서를 찾지 못했습니다.")
        return

    ids, texts, metadatas = [], [], []
    for doc in documents:
        for i, chunk in enumerate(chunk_text(doc["text"])):
            ids.append(f"{doc['source']}-{i}")
            texts.append(chunk)
            metadatas.append({"source": doc["source"]})

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    print(
        f"문서 {len(documents)}개, 총 {len(texts)}개 청크를 "
        f"'{COLLECTION_NAME}' 컬렉션에 색인했습니다. (경로: {CHROMA_DIR})"
    )


if __name__ == "__main__":
    build_index()
