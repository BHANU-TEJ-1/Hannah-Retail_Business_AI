"""Standardised result contract shared by every RetailAI agent."""

from __future__ import annotations

from typing import Any

from app.schemas.tool_result import ToolResult, ToolName


def success(
    tool: ToolName,
    data: Any = None,
    summary: str = "",
    metadata: dict[str, Any] | None = None,
) -> ToolResult:
    """Build a successful tool result."""
    return ToolResult(
        status="success",
        tool=tool,
        data=data,
        summary=summary,
        metadata=metadata or {},
    )


def error(
    tool: ToolName,
    message: str,
    data: Any = None,
    metadata: dict[str, Any] | None = None,
) -> ToolResult:
    """Build a failed tool result with a user-safe error message."""
    return ToolResult(
        status="error",
        tool=tool,
        data=data,
        summary="",
        error=message,
        metadata=metadata or {},
    )
