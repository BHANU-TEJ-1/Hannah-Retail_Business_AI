"""The single Reasoner LLM.

Hannah understands the request, decides whether tools are needed,
uses the tools when required, and produces the final answer.
There is no planner or second agent.
"""

from langchain.chat_models import init_chat_model

from app.config import (
    DEEPSEEK_MODEL,
    GRAPH_RECURSION_LIMIT,
    LLM_MAX_RETRIES,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
)
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger
from app.reasoner.tool_runtime import TOOLS, tool_runtime


logger = get_logger(__name__)


class Reasoner:
    """Runs Hannah's reasoning and tool-calling loop."""

    def __init__(
        self,
        llm=None,
        runtime=tool_runtime,
        max_iterations: int = GRAPH_RECURSION_LIMIT,
    ):

        if llm is None:

            llm = init_chat_model(
                model=DEEPSEEK_MODEL,
                model_provider="openai",
                api_key=OPENROUTER_API_KEY,
                base_url=OPENROUTER_BASE_URL,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                timeout=LLM_TIMEOUT,
                max_retries=LLM_MAX_RETRIES,
            )

        self._llm = llm.bind_tools(TOOLS)

        self._runtime = runtime

        self._max_iterations = max_iterations


    def invoke(self, messages: list) -> dict:

        used_tools: list[str] = []

        for _ in range(self._max_iterations):

            try:

                response = self._llm.invoke(
                    messages
                )

            except Exception as error:

                log_failure(
                    logger,
                    "reasoner_llm_call",
                    error,
                )

                return {
                    "answer": user_friendly_error(
                        error,
                        "Hannah",
                    ),
                    "tools_used": used_tools,
                }


            messages.append(response)


            tool_calls = getattr(
                response,
                "tool_calls",
                None,
            )


            # No tool call means the model
            # has produced the final answer.
            if not tool_calls:

                return {
                    "answer": response.content,
                    "tools_used": used_tools,
                }


            used_tools.extend(
                call["name"]
                for call in tool_calls
            )


            messages.extend(
                self._runtime.run(
                    tool_calls
                )
            )


        logger.info(
            "reasoner_max_iterations_reached "
            "tools_used=%s",
            used_tools,
        )


        return {
            "answer": (
                "I could not finish this request "
                "within the allowed number of steps."
            ),
            "tools_used": used_tools,
        }


    def stream(self, messages: list):

        """Stream Hannah's response while supporting tools."""

        used_tools: list[str] = []


        for iteration in range(
            self._max_iterations
        ):

            if iteration == 0:

                yield {
                    "type": "status",
                    "status": "UNDERSTANDING",
                }

            else:

                yield {
                    "type": "status",
                    "status": "PREPARING RESPONSE",
                }


            try:

                full_response = None


                for chunk in self._llm.stream(
                    messages
                ):

                    if full_response is None:

                        full_response = chunk

                    else:

                        full_response = (
                            full_response + chunk
                        )


                    content = getattr(
                        chunk,
                        "content",
                        "",
                    )


                    if content:

                        yield {
                            "type": "text",
                            "content": content,
                        }


            except Exception as error:

                log_failure(
                    logger,
                    "reasoner_llm_stream",
                    error,
                )


                yield {
                    "type": "error",
                    "content": user_friendly_error(
                        error,
                        "Hannah",
                    ),
                    "tools_used": used_tools,
                }

                return


            if full_response is None:

                yield {
                    "type": "error",
                    "content": (
                        "Hannah did not return "
                        "a response."
                    ),
                    "tools_used": used_tools,
                }

                return


            messages.append(
                full_response
            )


            tool_calls = getattr(
                full_response,
                "tool_calls",
                None,
            )
            logger.info(
                "reasoner_response tool_calls=%s",
                [
                    call["name"]
                    for call in tool_calls
                ] if tool_calls else [],
            )


            # Final answer.
            if not tool_calls:

                yield {
                    "type": "status",
                    "status": "PREPARING VOICE",
                }

                yield {
                    "type": "done",
                    "tools_used": used_tools,
                }

                return


            # Tools are required.
            yield {
                "type": "status",
                "status": "PREPARING TOOLS",
            }


            used_tools.extend(
                call["name"]
                for call in tool_calls
            )


            for call in tool_calls:

                tool_name = call["name"]


                yield {
                    "type": "status",
                    "status": (
                        f"USING {tool_name}"
                    ),
                }


            yield {
                "type": "status",
                "status": "PROCESSING RESULTS",
            }


            messages.extend(
                self._runtime.run(
                    tool_calls
                )
            )


        logger.info(
            "reasoner_stream_max_iterations_reached "
            "tools_used=%s",
            used_tools,
        )


        yield {
            "type": "error",
            "content": (
                "I could not finish this request "
                "within the allowed number of steps."
            ),
            "tools_used": used_tools,
        }


reasoner = Reasoner()