from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.services.tts_service import text_to_speech


router = APIRouter(prefix="/voice", tags=["voice"])


class SpeechRequest(BaseModel):
    text: str


@router.post("/speak")
async def speak(request: SpeechRequest):
    """
    Convert text into speech and return the generated MP3 audio.
    """

    try:
        audio = await text_to_speech(request.text)

        return Response(
            content=audio,
            media_type="audio/mpeg",
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error