from app.agents.contracts import success, error
from app.rag.rag_pipeline import RAGPipeline, rag_pipeline
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)


class KnowledgeAgent:
    """Public facade for the established RAG pipeline."""

    def __init__(self, pipeline: RAGPipeline = rag_pipeline) -> None:
        self._pipeline = pipeline

    def invoke(self, question: str) -> dict:
        try:
            response = self._pipeline.invoke(question)
            return success("rag", data=response, summary=response).to_dict()
        except Exception as exc:
            log_failure(logger, "knowledge_search", exc)
            return error("rag", user_friendly_error(exc, "Knowledge search")).to_dict()


knowledge_agent = KnowledgeAgent()