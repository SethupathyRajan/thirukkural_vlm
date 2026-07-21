"""
Explanation data structure for the Thirukkural Scenario-Based Decision-Making system.

This module defines the Explanation dataclass used to represent explainability
outputs from the explainability engine.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class Explanation:
    """
    Structured explanation for a prediction.

    Attributes:
        prediction_summary: Human-readable summary of the prediction.
        matched_concept: The ethical concept identified (with adhigaram and paal).
        matched_kural: The Thirukkural number (e.g., "42").
        matched_scenario: The scenario ID that matched the input (e.g., "S042").
        scenario_description: The text of the matched scenario.
        question: The question associated with the scenario.
        correct_answer: The correct answer to the question.
        ethical_reasoning: The explanation for the correct answer (from the dataset).
        confidence_level: Confidence level as a string (e.g., "Very High").
        confidence_value: Numerical confidence score (0-1).
        retrieval_scores: Dictionary containing image_similarity, knowledge_similarity,
                         and combined_score (each rounded to configured precision).
        alternatives: List of dictionaries representing alternative matches.
    """
    prediction_summary: str
    matched_concept: str
    matched_kural: str
    matched_scenario: str
    scenario_description: str
    question: str
    correct_answer: str
    ethical_reasoning: str
    confidence_level: str
    confidence_value: float
    retrieval_scores: Dict[str, float]
    alternatives: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the explanation to a dictionary.

        Returns:
            Dictionary representation of the explanation.
        """
        return asdict(self)