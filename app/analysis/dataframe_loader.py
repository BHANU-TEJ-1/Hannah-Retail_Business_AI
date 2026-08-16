"""Load SQL Agent results into request-scoped Pandas DataFrames."""

import time
from dataclasses import dataclass

import pandas as pd

from app.logging_config import get_logger


logger = get_logger(__name__)


@dataclass
class DataFrameLoadResult:
    dataframe: pd.DataFrame
    error: str | None = None
    cache_hit: bool = False


class DataFrameLoader:
    """Reuse SQL Agent data and avoid duplicate SQL calls during one request."""

    def __init__(self, sql_agent, cache: dict[str, pd.DataFrame] | None = None) -> None:
        self._sql_agent = sql_agent
        self._cache = cache if cache is not None else {}

    def load(self, question: str, required_columns: list[str] | None = None) -> DataFrameLoadResult:
        started = time.perf_counter()
        if question in self._cache:
            dataframe = self._cache[question].copy()
            logger.info("dataframe_cache_hit query=%r rows=%d", question, len(dataframe))
            return self._validate(dataframe, required_columns, cache_hit=True)

        logger.info("dataframe_cache_miss query=%r", question)
        try:
            sql_result = self._sql_agent.invoke(question)
            if sql_result.get("status") != "success":
                return DataFrameLoadResult(pd.DataFrame(), sql_result.get("summary", "SQL retrieval failed."))

            rows = sql_result.get("data") or []
            dataframe = pd.DataFrame(rows)
            self._cache[question] = dataframe.copy()
            logger.info(
                "dataframe_created rows=%d columns=%s duration_ms=%d",
                len(dataframe), list(dataframe.columns), (time.perf_counter() - started) * 1000,
            )
            return self._validate(dataframe, required_columns)
        except Exception as error:
            logger.exception("dataframe_load_failed error_type=%s", type(error).__name__)
            return DataFrameLoadResult(pd.DataFrame(), "Data could not be loaded for analysis.")

    @staticmethod
    def _validate(
        dataframe: pd.DataFrame,
        required_columns: list[str] | None,
        cache_hit: bool = False,
    ) -> DataFrameLoadResult:
        if dataframe.empty:
            return DataFrameLoadResult(dataframe, "No data was available for this analysis.", cache_hit)
        missing = [column for column in required_columns or [] if column not in dataframe.columns]
        if missing:
            return DataFrameLoadResult(
                dataframe,
                f"The analysis data is missing required columns: {', '.join(missing)}.",
                cache_hit,
            )
        return DataFrameLoadResult(dataframe, cache_hit=cache_hit)
