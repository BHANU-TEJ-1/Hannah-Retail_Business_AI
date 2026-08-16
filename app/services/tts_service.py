import httpx

from app.config import OPENROUTER_API_KEY
from app.logging_config import get_logger


logger = get_logger(__name__)


OPENROUTER_TTS_URL = (
    "https://openrouter.ai/api/v1/audio/speech"
)

TTS_MODEL = "deepgram/flux-tts:free"

# We will verify the exact supported voice with the
# OpenRouter model response.
TTS_VOICE = "flux-hannah-en"


async def text_to_speech(text: str) -> bytes:
    """
    Convert text into speech using Deepgram Flux TTS
    through OpenRouter.
    """

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty."
        )

    payload = {
        "model": TTS_MODEL,
        "input": text,
        "voice": TTS_VOICE,
        "response_format": "mp3",
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info(
        "tts_request_started model=%s voice=%s",
        TTS_MODEL,
        TTS_VOICE,
    )

    async with httpx.AsyncClient(timeout=60) as client:

        response = await client.post(
            OPENROUTER_TTS_URL,
            headers=headers,
            json=payload,
        )

    if not response.is_success:

        logger.error(
            "tts_request_failed status=%s response=%s",
            response.status_code,
            response.text,
        )

        raise RuntimeError(
            f"OpenRouter TTS failed "
            f"with status {response.status_code}: "
            f"{response.text}"
        )

    logger.info(
        "tts_completed characters=%d",
        len(text),
    )

    return response.content