"""Structured contract for the RetailAI V1 planner."""

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


Workflow = Literal[
    "sql",
    "analysis",
    "rag",
    "browser",
    "calculator",
    "mail",
    "payment",
    "chat",
]


class RouterResponse(BaseModel):
    """The only output permitted from the planner."""

    workflow: Workflow
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=300)
    needs_clarification: bool = False
    tool_input: dict[str, Any] = Field(default_factory=dict)
    followup: Workflow | None = None

    @model_validator(mode="after")
    def followup_is_controlled(self) -> "RouterResponse":
        """Only permit the one safe, sequential follow-up supported by the graph."""
        if self.followup is not None and (self.workflow not in {"sql", "analysis"} or self.followup != "mail"):
            raise ValueError("Only sql/analysis may request a mail follow-up")
        if self.needs_clarification and self.followup is not None:
            raise ValueError("Clarification requests cannot schedule a follow-up")
        return self
