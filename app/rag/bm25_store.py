"""A small persistent BM25 index for lexical RAG retrieval."""

import json
import math
import re
from collections import Counter
from pathlib import Path

from langchain_core.documents import Document


class BM25Store:
    def __init__(self, index_file: Path | None = None) -> None:
        self._index_file = index_file or Path("app/data/bm25_index.json")
        self._documents: list[Document] = []
        self._document_terms: list[Counter] = []
        self._document_frequency: Counter = Counter()
        self._average_document_length = 0.0

    def build_index(self, documents: list[Document]) -> None:
        """Build and persist the lexical index from the existing semantic chunks."""
        self._documents = documents
        self._document_terms = [Counter(self._tokens(document.page_content)) for document in documents]
        self._document_frequency = Counter()
        for terms in self._document_terms:
            self._document_frequency.update(terms.keys())
        total_terms = sum(sum(terms.values()) for terms in self._document_terms)
        self._average_document_length = total_terms / len(documents) if documents else 0.0
        self._save()

    def load(self) -> bool:
        """Load a previously built index. Returns False when it does not exist."""
        if not self._index_file.exists():
            return False
        records = json.loads(self._index_file.read_text(encoding="utf-8"))
        documents = [Document(page_content=record["content"], metadata=record["metadata"]) for record in records]
        self.build_index(documents)
        return True

    def retrieve(self, question: str, k: int = 5) -> list[Document]:
        if not self._documents:
            return []
        query_terms = self._tokens(question)
        scored_documents = [
            (self._score(query_terms, terms), index)
            for index, terms in enumerate(self._document_terms)
        ]
        scored_documents.sort(reverse=True)
        return [self._documents[index] for score, index in scored_documents[:k] if score > 0]

    def _score(self, query_terms: list[str], document_terms: Counter) -> float:
        score = 0.0
        document_count = len(self._documents)
        document_length = sum(document_terms.values())
        for term in query_terms:
            frequency = document_terms[term]
            if not frequency:
                continue
            matching_documents = self._document_frequency[term]
            inverse_frequency = math.log(1 + (document_count - matching_documents + 0.5) / (matching_documents + 0.5))
            denominator = frequency + 1.5 * (1 - 0.75 + 0.75 * document_length / self._average_document_length)
            score += inverse_frequency * frequency * 2.5 / denominator
        return score

    def _save(self) -> None:
        self._index_file.parent.mkdir(parents=True, exist_ok=True)
        records = [
            {"content": document.page_content, "metadata": document.metadata}
            for document in self._documents
        ]
        self._index_file.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")

    def _tokens(self, text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())


bm25_store = BM25Store()
