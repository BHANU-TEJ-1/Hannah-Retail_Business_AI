class SQLValidator:
    """Deterministic SQL safety checks. No LLM calls, no query planning -
    just rule-based validation of a SQL string before it reaches the executor."""

    name = "sql_verifier"
    description = "Validates that a SQL string is a single, safe SELECT statement."

    def __init__(self):

        self.allowed_statement = "SELECT"

        self.blocked_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "REPLACE",
            "MERGE",
            "GRANT",
            "REVOKE"
        ]

    def validate(self, sql: str):

        if sql is None or not sql.strip():
            return False, "SQL statement is empty."

        sql = sql.strip()

        # Only SELECT statements are allowed
        if not sql.upper().startswith(self.allowed_statement):
            return False, "Only SELECT queries are allowed."

        # Only one SQL statement
        if sql.count(";") > 1:
            return False, "Multiple SQL statements are not allowed."

        # Block dangerous SQL keywords
        for keyword in self.blocked_keywords:
            if keyword in sql.upper():
                return False, f"{keyword} statements are not allowed."

        # Block SQL comments
        if "--" in sql or "/*" in sql or "*/" in sql:
            return False, "SQL comments are not allowed."

        return True, "SQL is valid."

    def invoke(self, sql: str) -> dict:
        valid, message = self.validate(sql)

        if valid:
            return {"success": True, "message": message}

        return {"success": False, "error": message}


sql_validator = SQLValidator()
