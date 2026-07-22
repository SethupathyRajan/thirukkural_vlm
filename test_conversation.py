"""
Test for the Conversation Engine module.

This test creates mock Prediction and Explanation objects and tests
the conversation engine's ability to initialize and answer questions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from prediction import Prediction, MatchResult
from explanation import Explanation
from conversation_engine import ConversationEngine
from conversation_models import MockConversationModel
from conversation_memory import ConversationMemory
from context_builder import ContextBuilder


def create_mock_prediction() -> Prediction:
    """Create a mock Prediction object for testing."""
    # Create a mock MatchResult for top match
    top_match = MatchResult(
        scenario_id="S042",
        combined_score=0.91,
        image_similarity=0.92,
        knowledge_similarity=0.88,
        concept="Compassion",
        english_kural="With pain they guard their stores, yet 'All forlorn are we,' they'll cry,  Who cherish not their guests, nor kindly help supply"
    )

    # Create additional mock matches for alternatives
    alt1 = MatchResult(
        scenario_id="S043",
        combined_score=0.85,
        image_similarity=0.86,
        knowledge_similarity=0.84,
        concept="Justice",
        english_kural="The world is maintained by justice,  And if it departs, it perishes."
    )

    alt2 = MatchResult(
        scenario_id="S044",
        combined_score=0.80,
        image_similarity=0.81,
        knowledge_similarity=0.79,
        concept="Truth",
        english_kural="Falsehood never succeeds,  Truth alone triumphs."
    )

    top_matches = [top_match, alt1, alt2]

    # Create prediction
    prediction = Prediction(
        scenario_id="S042",
        kural_id=42,
        concept="Compassion",
        adhigaram="Chapter 4",
        paal="Aram",
        english_kural="With pain they guard their stores, yet 'All forlorn are we,' they'll cry,  Who cherish not their guests, nor kindly help supply",
        scenario="A person helping a stranger in need.",
        question="What is the right action?",
        correct_answer="Help the stranger.",
        explanation="Helping others is a core virtue.",
        image_similarity=0.92,
        knowledge_similarity=0.88,
        combined_score=0.91,
        confidence=0.91,
        top_matches=top_matches
    )

    return prediction


def create_mock_explanation() -> Explanation:
    """Create a mock Explanation object for testing."""
    # We'll create this manually since we don't have the actual Explanation class
    # but we know its structure from explanation.py

    explanation = Explanation(
        prediction_summary="The uploaded image most closely matches Scenario S042, representing the concept of Compassion. Therefore, the system retrieved Thirukkural 42.",
        matched_concept="Compassion under Chapter 4 (Aram)",
        matched_kural="42",
        matched_scenario="S042",
        scenario_description="A person helping a stranger in need.",
        question="What is the right action?",
        correct_answer="Help the stranger.",
        ethical_reasoning="Helping others is a core virtue.",
        confidence_level="Very High",
        confidence_value=0.91,
        retrieval_scores={
            "image_similarity": 0.92,
            "knowledge_similarity": 0.88,
            "combined_score": 0.91
        },
        alternatives=[
            {
                "scenario_id": "S043",
                "concept": "Justice",
                "combined_score": 0.85,
                "english_kural": "The world is maintained by justice,  And if it departs, it perishes."
            },
            {
                "scenario_id": "S044",
                "concept": "Truth",
                "combined_score": 0.80,
                "english_kural": "Falsehood never succeeds,  Truth alone triumphs."
            }
        ]
    )

    return explanation


def test_conversation_engine():
    """Test the conversation engine with mock objects."""
    print("Creating mock prediction and explanation...")
    prediction = create_mock_prediction()
    explanation = create_mock_explanation()

    print("Creating conversation engine...")
    engine = ConversationEngine()

    print("Initializing engine with prediction and explanation...")
    engine.initialize(prediction, explanation)

    print("Testing context retrieval...")
    context = engine.get_context()
    assert context is not None, "Context should not be None after initialization"
    assert "THIRUKKURAL SCENARIO-BASED DECISION-MAKING CONTEXT" in context
    print("✓ Context retrieved successfully")

    print("Testing question asking...")
    response = engine.ask("Explain this Kural in simple English.")
    assert isinstance(response, str) and len(response) > 0, "Response should be a non-empty string"
    print(f"✓ Got response: {response[:100]}...")

    print("Testing follow-up question...")
    response2 = engine.ask("Give me another real-life example.")
    assert isinstance(response2, str) and len(response2) > 0, "Follow-up response should be a non-empty string"
    print(f"✓ Got follow-up response: {response2[:100]}...")

    print("Testing conversation history...")
    history = engine.get_history()
    assert len(history) == 4, f"Expected 4 messages in history (2 user, 2 assistant), got {len(history)}"
    print(f"✓ History has {len(history)} entries")

    print("Testing reset conversation...")
    engine.reset_conversation()
    history = engine.get_history()
    assert len(history) == 0, f"Expected 0 messages after reset, got {len(history)}"
    print("✓ Conversation history reset successfully")

    print("Testing update context...")
    # Create a different prediction/explanation for update
    prediction2 = create_mock_prediction()
    prediction2.scenario_id = "S043"
    prediction2.kural_id = 43
    explanation2 = create_mock_explanation()
    explanation2.matched_kural = "43"
    explanation2.matched_concept = "Justice under Chapter 4 (Aram)"
    explanation2.ethical_reasoning = "Justice maintains the world."

    engine.update_context(prediction2, explanation2)
    context2 = engine.get_context()
    assert "S043" in context2, "Updated context should contain new scenario ID"
    assert "Justice" in context2, "Updated context should contain new concept"
    print("✓ Context updated successfully")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_conversation_engine()