from pydantic import BaseModel, Field


class VerifierResponse(BaseModel):
    sql: str = Field(description="Verified SQL query")

    is_valid: bool = Field(description="Whether the SQL is valid after verification")