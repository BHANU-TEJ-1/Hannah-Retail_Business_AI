from pydantic import BaseModel, Field


class Response(BaseModel):
    answer: str = Field(
        description="Business-friendly response for the user."
    )