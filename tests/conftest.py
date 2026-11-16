"""Shared fixtures for agent tests."""

import pytest
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.agent import initialize_agent
from app.config import settings


@pytest.fixture
def agent():
    """Return the async agent callable."""
    return initialize_agent(settings)


class JudgeVerdict(BaseModel):
    """Structured LLM judge result."""

    passed: bool = Field(description="Whether the agent output satisfies the expected behavior")
    score: float = Field(ge=0, le=1)
    reasons: list[str]


@pytest.fixture(scope="session")
def judge():
    """One shared structured-output judge model for the entire test session."""
    if not settings.openai_configured:
        return None
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    ).with_structured_output(JudgeVerdict)


def user_messages(text: str, *, chat_id: str = "test-chat") -> list[dict[str, str]]:
    """Build the message-list input expected by the agent."""
    return [{
        "chat_id": chat_id,
        "user_id": "test-user",
        "message_id": "message-1",
        "actor": "user",
        "text": text,
    }]
