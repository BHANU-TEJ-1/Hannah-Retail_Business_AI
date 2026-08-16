from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.voice import router as voice_router
from app.api.chat import router as chat_router
from app.database.schema_manager import schema_manager
from app.logging_config import get_logger


logger = get_logger(__name__)

app = FastAPI(title="RetailAI")
frontend_path = Path(__file__).resolve().parent.parent / "frontend"


@app.on_event("startup")
def startup() -> None:
    """Refresh the cached database schema before serving requests. The
    Reasoner's prompt already has a cached schema on disk, so a database
    that is temporarily unreachable should not stop the app from starting.
    """
    try:
        schema_manager.load_schema()
    except Exception as error:
        logger.warning("schema_refresh_skipped error=%s", error)
    logger.info("retailai_ready")

app.include_router(voice_router)
app.include_router(chat_router)
app.mount(
    "/",
    StaticFiles(
        directory=frontend_path,
        html=True,
    ),
    name="frontend",
)