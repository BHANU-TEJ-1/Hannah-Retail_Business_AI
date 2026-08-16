from app.rag.loader import document_loader
from app.rag.semantic_chunker import semantic_chunker
from app.rag.vector_store import vector_store
from app.logging_config import get_logger


logger = get_logger(__name__)


def build():

    logger.info("document_load_started")

    documents = document_loader.load_documents()

    logger.info("document_load_finished count=%d", len(documents))

    logger.info("chunking_started")

    chunks = semantic_chunker.chunk_documents(documents)

    logger.info("chunking_finished count=%d", len(chunks))

    logger.info("vector_index_build_started")

    vector_store.build_index(chunks)

    logger.info("vector_index_build_finished")


if __name__ == "__main__":
    build()
