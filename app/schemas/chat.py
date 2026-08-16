from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)


class ChatResponse(BaseModel):
    """Final answer from the Reasoner, plus which tools it used."""

    answer: str
    tools_used: list[str] = Field(default_factory=list)
