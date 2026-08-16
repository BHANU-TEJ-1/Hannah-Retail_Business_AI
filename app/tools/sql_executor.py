from app.database.connection import get_connection
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)


class SQLExecutor:
    """Executes an already-validated SQL statement. Does not generate or
    interpret SQL, and performs no reasoning of its own."""

    name = "sql_executor"
    description = "Executes a SQL statement against the database and returns structured results."

    def invoke(self, sql: str) -> dict:
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(sql)

            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            result_rows = [dict(zip(columns, row)) for row in rows]

            return {
                "success": True,
                "columns": columns,
                "rows": result_rows,
                "row_count": len(result_rows),
            }

        except Exception as error:
            log_failure(logger, "database_query", error)
            return {
                "success": False,
                "error": user_friendly_error(error, "Database query"),
            }

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


sql_executor = SQLExecutor()
