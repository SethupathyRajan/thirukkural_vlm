"""
Tests for the explainability engine of the Thirukkural Scenario-Based Decision-Making system.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from explainability import ExplainabilityEngine
from explanation import Explanation
from prediction import Prediction, MatchResult


def create_mock_prediction():
    """Create a mock Prediction object for testing."""
    # Create a mock Prediction instance
    prediction = Mock(spec=Prediction)
    prediction.scenario_id = "S042"
    prediction.kural_id = 42
    prediction.concept = "Compassion"
    prediction.adhigaram = "Chapter 4"
    prediction.paal = "Aram"
    prediction.scenario = "A person helping a stranger in need."
    prediction.question = "What is the right action?"
    prediction.correct_answer = "Help the stranger."
    prediction.explanation = "Helping others is a core virtue."
    prediction.image_similarity = 0.92
    prediction.knowledge_similarity = 0.88
    prediction.combined_score = 0.91
    prediction.confidence = 0.91

    # Create mock MatchResult objects for top_matches
    match1 = Mock(spec=MatchResult)
    match1.scenario_id = "S042"
    match1.combined_score = 0.91
    match1.concept = "Compassion"
    match1.english_kular = "With pain they guard their stores, yet 'All forlorn are we,' they'll cry,  Who cherish not their guests, nor kindly help supply"

    match2 = Mock(spec=MatchResult)
    match2.scenario_id = "S043"
    match2.combined_score = 0.85
    match2.concept = "Justice"
    match2.english_kural = "The world is maintained by justice,  And if it departs, it perishes."

    match3 = Mock(spec=MatchResult)
    match3.scenario_id = "S044"
    match3.combined_score = 0.80
    match3.concept = "Truth"
    match3.english_kural = "Falsehood never succeeds,  Truth alone triumphs."

    prediction.top_matches = [match1, match2, match3]

    return prediction


def test_explainability_engine_instantiation():
    """Test that the ExplainabilityEngine can be instantiated."""
    engine = ExplainabilityEngine()
    assert isinstance(engine, ExplainabilityEngine)


def test_generate_explanation_returns_explanation_object():
    """Test that generate_explanation returns an Explanation object."""
    engine = ExplainabilityEngine()
    prediction = create_mock_prediction()
    explanation = engine.generate_explanation(prediction)
    assert isinstance(explanation, Explanation)


def test_explanation_attributes():
    """Test that the explanation object has the expected attributes."""
    engine = ExplainabilityEngine()
    prediction = create_mock_prediction()
    explanation = engine.generate_explanation(prediction)

    assert explanation.prediction_summary
    assert explanation.matched_concept == "Compassion under Chapter 4 (Aram)"
    assert explanation.matched_kural == "42"
    assert explanation.matched_scenario == "S042"
    assert explanation.scenario_description == "A person helping a stranger in need."
    assert explanation.question == "What is the right action?"
    assert explanation.correct_answer == "Help the stranger."
    assert explanation.ethical_reasoning == "Helping others is a core virtue."
    assert explanation.confidence_level == "Very High"
    assert explanation.confidence_value == 0.91  # Assuming 3 decimal places
    assert explanation.retrieval_scores["image_similarity"] == 0.92
    assert explanation.retrieval_scores["knowledge_similarity"] == 0.88
    assert explanation.retrieval_scores["combined_score"] == 0.91
    assert len(explanation.alternatives) == 2  # We asked for 2 alternatives (top_matches[1:3])


def test_format_explanation_returns_string():
    """Test that format_explanation returns a string."""
    engine = ExplainabilityEngine()
    prediction = create_mock_prediction()
    explanation = engine.generate_explanation(prediction)
    formatted = engine.format_explanation(explanation)
    assert isinstance(formatted, str)
    assert "THIRUKKURAL SCENARIO-BASED DECISION-MAKING EXPLANATION" in formatted


def test_explanation_to_dict():
    """Test that the explanation can be converted to a dictionary."""
    engine = ExplainabilityEngine()
    prediction = create_mock_prediction()
    explanation = engine.generate_explanation(prediction)
    explanation_dict = explanation.to_dict()
    assert isinstance(explanation_dict, dict)
    assert "prediction_summary" in explanation_dict
    assert "matched_concept" in explanation_dict


def test_confidence_levels():
    """Test that confidence levels are correctly categorized."""
    engine = ExplainabilityEngine()
    # Test very high
    assert engine._get_confidence_level(0.95) == "Very High"
    # Test high
    assert engine._get_confidence_level(0.80) == "High"
    # Test moderate
    assert engine._get_confidence_level(0.65) == "Moderate"
    # Test low
    assert engine._get_confidence_level(0.50) == "Low"


def test_rounding():
    """Test that values are rounded to the configured precision."""
    engine = ExplainabilityEngine()
    # Test rounding down
    assert engine._round_value(0.1234) == 0.123
    # Test rounding up
    assert engine._round_value(0.1236) == 0.124
    # Test exact value
    assert engine._round_value(0.123) == 0.123
    # Test fewer decimal places
    assert engine._round_value(0.1) == 0.1
    # Test more decimal places
    assert engine._round_value(0.123456789) == 0.123


def main():
    """Run all tests."""
    tests = [
        test_explainability_engine_instantiation,
        test_generate_explanation_returns_explanation_object,
        test_explanation_attributes,
        test_format_explanation_returns_string,
        test_explanation_to_dict,
        test_confidence_levels,
        test_rounding
    ]

    failed = 0
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1

    if failed == 0:
        print("\nAll tests passed!")
    else:
        print(f"\n{failed} test(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()