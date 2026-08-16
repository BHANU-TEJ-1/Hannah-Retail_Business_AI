import time

from app.database.schema_manager import schema_manager
from app.llm.llm_factory import llm_factory
from app.pipelines.sql_pipeline import SQLPipeline
from app.tools.sql_executor import sql_executor
from app.tools.sql_validator import sql_validator
from app.logging_config import get_logger


logger = get_logger(__name__)


class SQLAgent:
    """Public SQL facade. Its pipeline is intentionally opaque to callers."""

    def __init__(self, pipeline: SQLPipeline | None = None) -> None:
        self._pipeline = pipeline or SQLPipeline(
            llm_factory=llm_factory,
            schema_manager=schema_manager,
            validator=sql_validator,
            executor=sql_executor,
        )

    def invoke(self, question: str) -> dict:
        started = time.perf_counter()
        logger.info("sql_request query=%r", question)
        result = self._pipeline.run(question)
        logger.info(
            "sql_completed status=%s duration_ms=%d",
            result.get("status"),
            (time.perf_counter() - started) * 1000,
        )
        return result


sql_agent = SQLAgent()