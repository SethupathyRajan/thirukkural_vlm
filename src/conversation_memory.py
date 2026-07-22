"""
Conversation memory for the Educational Conversation Engine.

Manages short-term conversation history for a single session.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ConversationMessage:
    """Represents a single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    # Optional: timestamp or other metadata can be added later


class ConversationMemory:
    """
    Manages conversation history for a single session.

    Stores the conversation history and provides methods to add, retrieve,
    and clear messages.
    """

    def __init__(self, max_history_length: int = 10):
        """
        Initialize conversation memory.

        Args:
            max_history_length: Maximum number of messages to keep in history.
                               Older messages are removed when limit is exceeded.
        """
        self.max_history_length = max_history_length
        self.messages: List[ConversationMessage] = []

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: Either "user" or "assistant"
            content: The message content
        """
        self.messages.append(ConversationMessage(role=role, content=content))
        self._trim_history()

    def get_history(self) -> List[ConversationMessage]:
        """
        Get the full conversation history.

        Returns:
            List of ConversationMessage objects in chronological order.
        """
        return self.messages.copy()

    def get_history_as_string(self) -> str:
        """
        Get conversation history as a formatted string.

        Returns:
            Formatted string representing the conversation history.
        """
        if not self.messages:
            return "No conversation history."

        history_lines = []
        for msg in self.messages:
            history_lines.append(f"{msg.role.capitalize()}: {msg.content}")
        return "\n".join(history_lines)

    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages.clear()

    def _trim_history(self) -> None:
        """Trim history to max_history_length, removing oldest messages first."""
        if len(self.messages) > self.max_history_length:
            self.messages = self.messages[-self.max_history_length:]