"""Message interface accepted by the support-ticket graph."""

from typing import Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class Message(TypedDict):
    """One client message in the current chat context."""

    chat_id: str
    user_id: str
    message_id: str
    actor: Literal["user", "assistant"]
    text: str


class OutputSection(TypedDict):
    """One titled section in the agent response."""

    title: str
    text: str


def to_langchain_messages(messages: list[Message]) -> list[BaseMessage]:
    """Convert chat messages into LangChain prompt messages."""
    converted: list[BaseMessage] = []
    for message in messages:
        if message["actor"] == "assistant":
            converted.append(AIMessage(content=message["text"]))
        else:
            converted.append(HumanMessage(content=message["text"]))
    return converted
