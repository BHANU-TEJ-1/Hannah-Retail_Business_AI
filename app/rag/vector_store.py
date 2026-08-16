from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.rag.embeddings import embedding_model


class VectorStore:

    def __init__(self):

        self.persist_directory = Path("app/data/chroma_db")

        self.db = None

    def build_index(self, chunks):

        self.db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=str(self.persist_directory)
        )

        # BM25 uses the exact same semantic chunks as Chroma.
        from app.rag.bm25_store import bm25_store
        bm25_store.build_index(chunks)

    def load(self):

        self.db = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=embedding_model
        )

    def similarity_search(
        self,
        query: str,
        k: int = 5
    ):

        return self.db.similarity_search(
            query,
            k=k
        )

    def get_documents(self) -> list[Document]:
        """Read stored chunks so a BM25 index can be created without re-chunking."""
        if self.db is None:
            self.load()
        stored = self.db.get(include=["documents", "metadatas"])
        return [
            Document(page_content=content, metadata=metadata or {})
            for content, metadata in zip(stored["documents"], stored["metadatas"])
        ]


vector_store = VectorStore()
