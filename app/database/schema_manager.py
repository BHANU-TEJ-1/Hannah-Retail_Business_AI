from pathlib import Path
import json

from app.database.connection import get_connection
from app.logging_config import get_logger


logger = get_logger(__name__)


class SchemaManager:

    def __init__(self):
        self.schema = ""

        self.prompts_folder = Path("app/prompts")
        self.schema_file = self.prompts_folder / "schema.py"
        self.metadata_file = self.prompts_folder / "metadata.json"

    def load_schema(self):
        logger.info("schema_load_started")

        schema = self.fetch_schema()

        self.generate_metadata_file(schema)

        # Store the existing static schema in memory
        self.schema = self.schema_file.read_text(
            encoding="utf-8"
        )

        logger.info(
            "schema_load_finished table_count=%d",
            len(schema)
        )

    def fetch_schema(self):

        query = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        schema = {}

        for table, column, datatype in rows:

            if table not in schema:
                schema[table] = []

            schema[table].append({
                "column": column,
                "type": datatype
            })

        return schema

    def generate_schema_file(self, schema):

        lines = []

        for table, columns in schema.items():

            lines.append(
                f"Table: {table}"
            )

            for column in columns:

                lines.append(
                    f"- {column['column']} ({column['type']})"
                )

            lines.append("")

        content = 'DATABASE_SCHEMA = """\n'
        content += "\n".join(lines)
        content += '\n"""'

        self.schema_file.write_text(
            content,
            encoding="utf-8"
        )

    def generate_metadata_file(self, schema):

        metadata = {
            "tables": []
        }

        for table, columns in schema.items():

            metadata["tables"].append({
                "table": table,
                "columns": columns
            })

        with open(
            self.metadata_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4
            )


schema_manager = SchemaManager()