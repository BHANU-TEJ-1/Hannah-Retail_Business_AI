
'''This is the SQLResponse schema for structured output.
    
'''

from pydantic import BaseModel, Field


class SQLResponse(BaseModel):
    """
    Structured output returned by the SQL Generator.
    """

    sql: str = Field(
        description="The generated SQL query."
    )