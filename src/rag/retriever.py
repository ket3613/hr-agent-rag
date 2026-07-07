"""
Chroma 벡터스토어에서 관련 문서 청크를 검색하는 Retriever.
"""
import chromadb
from chromadb.utils import embedding_functions

from src.config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL


class Retriever:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=self.embedding_fn
        )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """질의어와 관련된 상위 top_k개 문서 청크를 반환합니다.

        반환 형식: [{"text": str, "source": str}, ...]
        """
        if self.collection.count() == 0:
            return []

        results = self.collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        return [
            {"text": doc, "source": meta.get("source", "unknown")}
            for doc, meta in zip(docs, metas)
        ]
