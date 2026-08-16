"""Builds the explicit, initial message state handed to the Reasoner."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.reasoner.prompts import SYSTEM_PROMPT


class ContextBuilder:
    """Turns an incoming question into the starting message list."""

    def build(self, question: str) -> list:
        return [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]


context_builder = ContextBuilder()