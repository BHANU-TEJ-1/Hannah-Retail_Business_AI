import asyncio
from pathlib import Path

from app.services.tts_service import text_to_speech


async def main() -> None:

    text = (
        "Hello. This is RetailAI. "
        "Your voice assistant is working."
    )

    audio = await text_to_speech(text)

    output_file = Path("test_output.mp3")

    output_file.write_bytes(audio)

    print(
        f"Audio saved to: {output_file.resolve()}"
    )


if __name__ == "__main__":
    asyncio.run(main())