''' the database connection.py file , no sqlalchemy , just psycopg2, 
just returns the connection 
so application->connection->cursor->postgresql, just the normal way '''

import psycopg2

from app.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)
from app.logging_config import get_logger


logger = get_logger(__name__)


def get_connection():
    """
    Creates and returns a new PostgreSQL connection.
    """

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    logger.info("database_connected database=%s", DB_NAME)
    return connection
