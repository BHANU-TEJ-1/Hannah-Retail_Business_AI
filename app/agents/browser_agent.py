from app.agents.contracts import success, error
from app.llm.llm_factory import llm_factory
from app.business_context import business_context
from app.prompts.browser_prompt import build_browser_prompt
from app.tools.browser_tool import browser_tool
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)


class BrowserAgent:
    def __init__(self, llm=None, search_tool=browser_tool) -> None:
        self._llm = llm or llm_factory.get_gemini()
        self._search_tool = search_tool

    def invoke(self, question: str) -> dict:
        try:
            search_query = self._search_query(question)
            search_result = self._search_tool.search(search_query)
            context = search_result.get("answer", "")
            if not context:
                context = "\n\n".join(
                    result.get("content", "") for result in search_result.get("results", [])
                )

            prompt = build_browser_prompt(context=context, question=question)
            response = self._llm.invoke(prompt)
            answer = self._text_from_response(response)
            return success(
                "browser",
                data=answer,
                summary=answer,
                metadata={"sources": len(search_result.get("results", [])), "search_query": search_query},
            ).to_dict()
        except Exception as exc:
            log_failure(logger, "browser_search", exc)
            return error("browser", user_friendly_error(exc, "Browser search")).to_dict()

    @staticmethod
    def _search_query(question: str) -> str:
        """Add the configured locale only when the user supplied none."""
        country = business_context.country.strip()
        if not country or BrowserAgent._has_explicit_location(question):
            return question
        return f"{question} in {country}"

    @staticmethod
    def _has_explicit_location(question: str) -> bool:
        lower = question.lower()
        return any(marker in lower for marker in (" in ", " for ", " near ", " at "))

    def _text_from_response(self, response) -> str:
        if hasattr(response, "text"):
            return response.text()
        if isinstance(response.content, str):
            return response.content
        if isinstance(response.content, list):
            return "".join(
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        return str(response.content)


browser_agent = BrowserAgent()
