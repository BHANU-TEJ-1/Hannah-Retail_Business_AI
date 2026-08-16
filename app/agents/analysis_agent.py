"""Analysis Agent: loads DataFrames via SQL, then generates + executes Pandas code."""

from __future__ import annotations

import time
from typing import Any

import pandas as pd

from app.agents.contracts import success, error
from app.agents.sql_agent import SQLAgent, sql_agent
from app.analysis.dataframe_loader import DataFrameLoader
from app.analysis.executor import analyse, CodeExecutionError
from app.analysis.prompt import build_analysis_prompt
from app.llm.llm_factory import llm_factory
from app.error_messages import log_failure
from app.logging_config import get_logger


logger = get_logger(__name__)


class AnalysisAgent:
    """Generate Pandas code from a natural-language question and execute it safely."""

    # Base queries that load the relevant business data into DataFrames.  These
    # are broad enough to answer most analytical questions without re-querying.
    _DATAFRAME_QUERIES = {
        "orders": "Show all sales orders with dates, amounts, quantities and customer info.",
        "products": "Show all products with names, categories, prices and stock.",
        "customers": "Show all customers with names, contact info and segment.",
        "inventory": "Show current inventory with product names, quantities and reorder levels.",
        "suppliers": "Show all suppliers with names, contact info and categories.",
    }

    def __init__(
        self,
        sql: SQLAgent = sql_agent,
        llm=None,
    ) -> None:
        self._sql = sql
        self._llm = llm or llm_factory.get_qwen()

    def invoke(self, question: str) -> dict[str, Any]:
        """Answer *question* by generating and executing Pandas code."""
        started = time.perf_counter()
        logger.info("analysis_request query=%r", question)

        try:
            dataframes = self._load_dataframes()
            if not dataframes:
                return error(
                    "analysis",
                    "No business data was available for analysis.",
                ).to_dict()

            code = self._generate_code(question, dataframes)
            logger.info("analysis_code_generated length=%d", len(code))

            result = analyse(code, dataframes)
            summary = self._build_summary(question, result)

            logger.info(
                "analysis_completed duration_ms=%d",
                (time.perf_counter() - started) * 1000,
            )
            return success(
                "analysis",
                data=result,
                summary=summary,
                metadata={"code_length": len(code)},
            ).to_dict()

        except CodeExecutionError as exc:
            logger.warning("analysis_code_error error=%s", exc)
            return error("analysis", str(exc)).to_dict()
        except Exception as exc:
            log_failure(logger, "analysis_agent", exc)
            return error("analysis", "Analysis could not be completed.").to_dict()

    def _load_dataframes(self) -> dict[str, pd.DataFrame]:
        """Load all business DataFrames from the database via SQL."""
        loader = DataFrameLoader(self._sql, cache={})
        dataframes: dict[str, pd.DataFrame] = {}
        for name, query in self._DATAFRAME_QUERIES.items():
            load_result = loader.load(query)
            if load_result.error is None:
                dataframes[name] = load_result.dataframe
        return dataframes

    def _generate_code(self, question: str, dataframes: dict[str, pd.DataFrame]) -> str:
        """Build the prompt and call the LLM to generate Pandas code."""
        schema_lines: list[str] = []
        for name, df in dataframes.items():
            columns = ", ".join(
                f"{col} ({str(df[col].dtype)})" for col in df.columns
            )
            schema_lines.append(f"- {name} ({len(df)} rows): {columns}")

        prompt = build_analysis_prompt("\n".join(schema_lines), question)

        response = self._llm.invoke(prompt)
        code = self._extract_code(response)
        return code

    @staticmethod
    def _extract_code(response: Any) -> str:
        """Extract Python code from the LLM response, stripping markdown fences."""
        content = ""
        if hasattr(response, "content"):
            if isinstance(response.content, str):
                content = response.content
            elif isinstance(response.content, list):
                content = "".join(
                    b.get("text", "") for b in response.content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
        elif isinstance(response, str):
            content = response
        else:
            content = str(response)

        # Strip markdown code fences if present
        if "```python" in content:
            content = content.split("```python", 1)[1]
            if "```" in content:
                content = content.split("```", 1)[0]
        elif "```" in content:
            content = content.split("```", 1)[1]
            if "```" in content:
                content = content.split("```", 1)[0]

        return content.strip()

    @staticmethod
    def _build_summary(question: str, result: Any) -> str:
        """Build a one-line summary from the result."""
        if isinstance(result, list):
            return f"Analysis returned {len(result)} result(s)."
        if isinstance(result, dict):
            return f"Analysis returned {len(result)} metric(s)."
        if isinstance(result, (int, float)):
            return f"Analysis result: {result}"
        return "Analysis completed successfully."


analysis_agent = AnalysisAgent()
