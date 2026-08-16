"""Small, provider-agnostic prompt budget guard for LLM calls."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.messages import BaseMessage, SystemMessage


class TokenBudget:
    """Estimate prompt tokens and retain the most useful content within a limit.

    The estimate intentionally uses a conservative four-characters-per-token
    heuristic so it works consistently without a model-specific tokenizer.
    """

    def __init__(self, max_prompt_tokens: int) -> None:
        self.max_prompt_tokens = max_prompt_tokens

    def enforce(self, prompt: Any) -> Any:
        if self.estimate(prompt) <= self.max_prompt_tokens:
            return prompt
        if isinstance(prompt, str):
            return self._truncate_text(prompt, self.max_prompt_tokens)
        if self._is_message_sequence(prompt):
            return self._truncate_messages(prompt)
        return self._truncate_text(str(prompt), self.max_prompt_tokens)

    def estimate(self, value: Any) -> int:
        if isinstance(value, str):
            return self._estimate_text(value)
        if isinstance(value, BaseMessage):
            return self.estimate(value.content)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return sum(self.estimate(item) for item in value)
        if isinstance(value, dict):
            return sum(self.estimate(item) for item in value.values())
        return self._estimate_text(str(value))

    def _truncate_messages(self, messages: Sequence[BaseMessage]) -> list[BaseMessage]:
        system_messages = [message for message in messages if isinstance(message, SystemMessage)]
        if self.estimate(system_messages) > self.max_prompt_tokens:
            first_system_message = system_messages[0]
            return [
                self._copy_with_content(
                    first_system_message,
                    self._truncate_text(str(first_system_message.content), self.max_prompt_tokens),
                )
            ]
        remaining = max(0, self.max_prompt_tokens - self.estimate(system_messages))
        retained: list[BaseMessage] = []

        # Prefer the newest conversation turns; large tool results and stale
        # history are the least valuable when a request needs to be shortened.
        for message in reversed(messages):
            if isinstance(message, SystemMessage):
                continue
            message_tokens = self.estimate(message)
            if message_tokens <= remaining:
                retained.append(message)
                remaining -= message_tokens
            elif remaining:
                retained.append(self._copy_with_content(message, self._truncate_text(str(message.content), remaining)))
                break

        return [*system_messages, *reversed(retained)]

    @staticmethod
    def _is_message_sequence(value: Any) -> bool:
        return (
            isinstance(value, Sequence)
            and not isinstance(value, (str, bytes))
            and all(isinstance(item, BaseMessage) for item in value)
        )

    @staticmethod
    def _estimate_text(text: str) -> int:
        return max(1, (len(text) + 3) // 4)

    def _truncate_text(self, text: str, max_tokens: int) -> str:
        max_characters = max_tokens * 4
        if len(text) <= max_characters:
            return text
        marker = "\n\n[Context truncated to fit the LLM token budget]\n\n"
        if max_characters <= len(marker):
            return "[Context truncated]"[:max_characters]
        available = max(0, max_characters - len(marker))
        head = available // 2
        tail = available - head
        return f"{text[:head]}{marker}{text[-tail:]}"

    @staticmethod
    def _copy_with_content(message: BaseMessage, content: str) -> BaseMessage:
        return message.model_copy(update={"content": content})
