"""Unified structured result returned by every RetailAI agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Status = Literal["success", "error"]
ToolName = Literal["sql", "analysis", "rag", "browser", "calculator", "mail", "payment"]


@dataclass
class ToolResult:
    """Single contract consumed by the Response Generator (LLM #2) and the graph.

    Every agent returns this shape so the downstream pipeline always sees the
    same keys regardless of which tool executed.
    """

    status: Status
    tool: ToolName
    data: Any = None
    summary: str = ""
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "tool": self.tool,
            "data": self.data,
            "summary": self.summary,
            "error": self.error,
            "metadata": self.metadata,
        }
