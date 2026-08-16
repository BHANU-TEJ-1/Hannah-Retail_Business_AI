from tavily import TavilyClient

from app.config import TAVILY_API_KEY, TAVILY_MAX_RESULTS
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)


class BrowserTool:
    """Performs a web search only. Does not interpret or reason about the
    results - the Reasoner decides when to search and what to do with it."""

    name = "browser"
    description = "Searches the web for current information."

    def __init__(self):
        self.client = TavilyClient(api_key=TAVILY_API_KEY)

    def invoke(self, query: str) -> dict:
        if query is None or not query.strip():
            return {"success": False, "error": "Search query is empty."}

        try:
            result = self.client.search(
                query=query,
                search_depth="basic",
                max_results=TAVILY_MAX_RESULTS,
                include_answer=True,
                include_raw_content=False,
            )

            return {
                "success": True,
                "query": query,
                "answer": result.get("answer"),
                "results": result.get("results", []),
            }

        except Exception as error:
            log_failure(logger, "web_search", error)
            return {"success": False, "error": user_friendly_error(error, "Web search")}


browser_tool = BrowserTool()
