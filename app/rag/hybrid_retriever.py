"""Hybrid retrieval combines semantic and BM25 results with RRF."""

from langchain_core.documents import Document

from app.rag.bm25_store import BM25Store, bm25_store
from app.rag.retriever import Retriever, retriever
from app.rag.vector_store import VectorStore, vector_store


class HybridRetriever:
    def __init__(
        self,
        semantic_retriever: Retriever = retriever,
        lexical_store: BM25Store = bm25_store,
        store: VectorStore = vector_store,
    ) -> None:
        self._semantic_retriever = semantic_retriever
        self._lexical_store = lexical_store
        self._store = store
        self._prepare_bm25_index()

    def retrieve(self, question: str, k: int = 5) -> list[Document]:
        semantic_documents = self._semantic_retriever.retrieve(question, k=k)
        bm25_documents = self._lexical_store.retrieve(question, k=k)
        return self._fuse(semantic_documents, bm25_documents, k)

    def _prepare_bm25_index(self) -> None:
        if not self._lexical_store.load():
            self._lexical_store.build_index(self._store.get_documents())

    def _fuse(
        self,
        semantic_documents: list[Document],
        bm25_documents: list[Document],
        k: int,
    ) -> list[Document]:
        """Use reciprocal rank fusion so neither retriever dominates the result."""
        scores: dict[str, float] = {}
        documents: dict[str, Document] = {}
        for result_list in (semantic_documents, bm25_documents):
            for rank, document in enumerate(result_list, start=1):
                key = document.page_content
                documents[key] = document
                scores[key] = scores.get(key, 0.0) + 1 / (60 + rank)
        ranked_keys = sorted(scores, key=scores.get, reverse=True)
        return [documents[key] for key in ranked_keys[:k]]


hybrid_retriever = HybridRetriever()
