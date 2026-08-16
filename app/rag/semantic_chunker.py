from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

from app.rag.embeddings import embedding_model


class SemanticDocumentChunker:

    def __init__(self):

        self.chunker = SemanticChunker(
            embedding_model
        )

    def chunk_documents(
        self,
        documents: list[Document]
    ) -> list[Document]:

        return self.chunker.split_documents(documents)


semantic_chunker = SemanticDocumentChunker()