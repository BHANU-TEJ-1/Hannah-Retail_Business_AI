from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger
from app.rag.hybrid_retriever import hybrid_retriever


logger = get_logger(__name__)


class RAGRetriever:
    """Query -> retriever -> structured, ranked document chunks.

    Performs retrieval only: no answer generation, no LLM reasoning. The
    Reasoner (built in a later phase) decides how to use these results.
    """

    name = "rag"
    description = "Retrieves relevant passages from the company handbook for a query."

    def __init__(self, retriever=hybrid_retriever):
        self._retriever = retriever

    def invoke(self, query: str, k: int = 5) -> dict:
        if query is None or not query.strip():
            return {"success": False, "error": "Query is empty."}

        try:
            documents = self._retriever.retrieve(query, k=k)
        except Exception as error:
            log_failure(logger, "rag_retrieval", error)
            return {"success": False, "error": user_friendly_error(error, "Document retrieval")}

        results = [
            {
                "content": document.page_content,
                "source": document.metadata.get("source"),
                "chapter": document.metadata.get("chapter"),
            }
            for document in documents
        ]

        return {
            "success": True,
            "query": query,
            "results": results,
            "result_count": len(results),
        }


rag_retriever = RAGRetriever()
