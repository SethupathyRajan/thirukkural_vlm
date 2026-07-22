"""
Educational Conversation Engine for the Thirukkural Scenario-Based Decision-Making System.

This engine manages educational conversations about retrieved Thirukkural knowledge,
grounding all responses in the provided prediction and explanation context.
"""

from typing import List, Dict, Any, Optional
from context_builder import ContextBuilder
from conversation_memory import ConversationMemory
from conversation_models import BaseConversationModel, MockConversationModel, GenerationConfig
from explanation import Explanation
from prediction import Prediction


class ConversationEngine:
    """
    Manages educational conversations grounded in Thirukkural knowledge.

    The engine ensures that all responses are based solely on the retrieved
    knowledge (prediction and explanation) and does not perform retrieval
    or access external knowledge beyond what is provided.
    """

    def __init__(
        self,
        model: Optional[BaseConversationModel] = None,
        context_builder: Optional[ContextBuilder] = None,
        conversation_memory: Optional[ConversationMemory] = None,
        system_prompt: Optional[str] = None,
        model_config: Optional[GenerationConfig] = None
    ):
        """
        Initialize the conversation engine.

        Args:
            model: Conversation model to use for generating responses.
                   If None, a mock model will be used for testing.
            context_builder: Context builder to use. If None, a default one is created.
            conversation_memory: Conversation memory to use. If None, a default one is created.
            system_prompt: System prompt to guide the model's behavior.
                          If None, a default educational system prompt is used.
            model_config: Configuration for the model. If None, default values are used.
        """
        # Set up model configuration
        self.model_config = model_config or GenerationConfig()

        # Set up components with defaults if not provided
        self.model = model or MockConversationModel(self.model_config)
        self.context_builder = context_builder or ContextBuilder()
        self.conversation_memory = conversation_memory or ConversationMemory()

        # Default system prompt for educational conversations
        self.system_prompt = system_prompt or (
            "You are an educational assistant that helps users understand Thirukkural "
            "concepts and ethical reasoning. You must answer questions based ONLY on "
            "the provided context from the Thirukkural Scenario-Based Decision-Making "
            "system. Do not use external knowledge or make up information. If the "
            "context does not contain sufficient information to answer a question, "
            "clearly state that the answer cannot be determined from the retrieved "
            "knowledge. Keep responses educational, clear, and grounded in the "
            "provided Thirukkural context."
        )

        # Store the current context for reference
        self._current_context: Optional[str] = None
        self._current_prediction: Optional[Prediction] = None
        self._current_explanation: Optional[Explanation] = None

    def initialize(self, prediction: Prediction, explanation: Explanation) -> None:
        """
        Initialize or reset the conversation with new prediction and explanation.

        This sets the context for the conversation and clears conversation history.

        Args:
            prediction: Prediction object from inference engine
            explanation: Explanation object from explainability engine
        """
        self._current_prediction = prediction
        self._current_explanation = explanation
        self._current_context = self.context_builder.build_context(prediction, explanation)
        # Clear conversation history when initializing with new context
        self.conversation_memory.clear()

    def ask(self, question: str) -> str:
        """
        Ask a question and get a response based on the current context.

        Args:
            question: The user's question

        Returns:
            Generated response string

        Raises:
            RuntimeError: If no context has been initialized
        """
        if self._current_context is None:
            raise RuntimeError(
                "Conversation engine not initialized. Call initialize() with "
                "prediction and explanation first."
            )

        # Add user question to conversation history
        self.conversation_memory.add_message("user", question)

        # Generate response using the model
        conversation_history = self.conversation_memory.get_history()
        # Convert ConversationMessage objects to dicts for the model
        history_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history[:-1]  # Exclude the current user question
        ]

        response = self.model.generate_response(
            system_prompt=self.system_prompt,
            conversation_history=history_dicts,
            user_query=question,
            context=self._current_context
        )

        # Add assistant response to conversation history
        self.conversation_memory.add_message("assistant", response)

        return response

    def ask_followup(self, question: str) -> str:
        """
        Ask a follow-up question (alias for ask method).

        Args:
            question: The follow-up question

        Returns:
            Generated response string
        """
        return self.ask(question)

    def reset_conversation(self) -> None:
        """
        Reset the conversation history while keeping the current context.
        """
        self.conversation_memory.clear()

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.

        Returns:
            List of dictionaries with 'role' and 'content' keys.
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_memory.get_history()
        ]

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_memory.clear()

    def get_context(self) -> Optional[str]:
        """
        Get the current context string.

        Returns:
            The current context string, or None if not initialized
        """
        return self._current_context

    def update_context(self, prediction: Prediction, explanation: Explanation) -> None:
        """
        Update the context with new prediction and explanation.

        This is useful if the retrieval results change during a conversation
        (though typically the context should remain fixed for a given scenario).

        Args:
            prediction: New Prediction object
            explanation: New Explanation object
        """
        self.initialize(prediction, explanation)