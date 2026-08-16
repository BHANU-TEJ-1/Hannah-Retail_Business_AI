import json
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger
from app.reasoner.context_builder import context_builder
from app.reasoner.reasoner import reasoner
from app.schemas.chat import ChatRequest, ChatResponse

logger = get_logger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    started = time.perf_counter()

    try:
        messages = context_builder.build(request.question)
        result = reasoner.invoke(messages)

        response = ChatResponse(
            answer=result["answer"],
            tools_used=result.get("tools_used", []),
        )

        logger.info(
            "chat_completed tools_used=%s duration_ms=%d",
            response.tools_used,
            (time.perf_counter() - started) * 1000,
        )
        return response

    except Exception as error:
        log_failure(logger, "chat_request", error)
        return ChatResponse(
            answer=user_friendly_error(error, "RetailAI"),
            tools_used=[],
        )
@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    """
    Stream the RetailAI response as text chunks.
    """

    def generate():
        started = time.perf_counter()

        try:
            messages = context_builder.build(request.question)

            for event in reasoner.stream(messages):

                yield (
                    json.dumps(event)
                    + "\n"
                )

            logger.info(
                "chat_stream_completed duration_ms=%d",
                (time.perf_counter() - started) * 1000,
            )

        except Exception as error:

            log_failure(
                logger,
                "chat_stream_request",
                error,
            )

            yield (
                json.dumps(
                    {
                        "type": "error",
                        "content": user_friendly_error(
                            error,
                            "RetailAI",
                        ),
                    }
                )
                + "\n"
            )

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
    )