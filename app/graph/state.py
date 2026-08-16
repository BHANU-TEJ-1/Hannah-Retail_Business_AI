from typing import Any, TypedDict

from app.schemas.router_response import RouterResponse


class RetailState(TypedDict):
    """State passed through the top-level RetailAI workflow."""

    question: str
    decision: RouterResponse
    tool_result: dict[str, Any]
    answer: str
