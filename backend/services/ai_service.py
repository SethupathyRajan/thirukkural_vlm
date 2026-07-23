"""
AI Service for the Thirukkural Educational API.

This service wraps the AI components (InferenceEngine, ExplainabilityEngine, ConversationEngine)
and provides a unified interface for the API routes.
"""

import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from inference import InferenceEngine
from explainability import ExplainabilityEngine
from conversation_engine import ConversationEngine
from conversation_models import MockConversationModel, GenerationConfig
from prediction import Prediction
from explanation import Explanation


class AIService:
    """
    Singleton service that manages the AI components.
    """

    def __init__(self):
        self.inference_engine: Optional[InferenceEngine] = None
        self.explainability_engine: Optional[ExplainabilityEngine] = None
        # We don't initialize conversation engine here; it's created per session

    def initialize(self):
        """
        Initialize the AI components.
        This should be called once at startup.
        """
        if self.inference_engine is None:
            self.inference_engine = InferenceEngine()
            self.inference_engine.load()

        if self.explainability_engine is None:
            self.explainability_engine = ExplainabilityEngine()

    def predict(self, image_path: str) -> Prediction:
        """
        Run inference on an image.

        Args:
            image_path: Path to the image file

        Returns:
            Prediction object
        """
        if self.inference_engine is None:
            raise RuntimeError("Inference engine not initialized")
        return self.inference_engine.predict(image_path)

    def explain(self, prediction: Prediction) -> Explanation:
        """
        Generate an explanation for a prediction.

        Args:
            prediction: Prediction object from inference

        Returns:
            Explanation object
        """
        if self.explainability_engine is None:
            raise RuntimeError("Explainability engine not initialized")
        return self.explainability_engine.generate_explanation(prediction)

    def create_conversation_engine(self) -> ConversationEngine:
        """
        Create a new conversation engine for a chat session.

        Returns:
            ConversationEngine instance
        """
        # Use a mock model for now; in production, this would be configurable
        model_config = GenerationConfig(temperature=0.7, max_tokens=500)
        model = MockConversationModel(model_config)
        return ConversationEngine(model=model)