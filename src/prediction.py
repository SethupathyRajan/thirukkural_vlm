"""
Prediction data structures for the Thirukkural Scenario-Based Decision-Making inference pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class MatchResult:
    """Represents a single match result from the retrieval."""
    scenario_id: str
    combined_score: float
    image_similarity: float
    knowledge_similarity: float
    concept: str
    english_kural: str


@dataclass
class Prediction:
    """
    Prediction result for an input image.

    Attributes:
        scenario_id: The ID of the matched scenario (top-1)
        kural_id: The numeric ID extracted from scenario_id (e.g., 42 for S042)
        concept: The concept of the matched scenario
        adhigaram: The adhigaram (chapter) of the matched scenario
        paal: The paal (section) of the matched scenario
        english_kural: The English translation of the Thirukkural
        scenario: The scenario description
        question: The question associated with the scenario
        correct_answer: The correct answer to the question
        explanation: The explanation for the correct answer
        image_similarity: Similarity score between input image and matched image embedding
        knowledge_similarity: Similarity score between matched knowledge embedding and reference
        combined_score: Weighted combination of image and knowledge similarities
        confidence: Confidence score (currently set to combined_score)
        top_matches: List of top-k matches (including the top-1)
    """
    scenario_id: str
    kural_id: int
    concept: str
    adhigaram: str
    paal: str
    english_kural: str
    scenario: str
    question: str
    correct_answer: str
    explanation: str
    image_similarity: float
    knowledge_similarity: float
    combined_score: float
    confidence: float
    top_matches: List[MatchResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the prediction to a dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "kural_id": self.kural_id,
            "concept": self.concept,
            "adhigaram": self.adhigaram,
            "paal": self.paal,
            "english_kural": self.english_kural,
            "scenario": self.scenario,
            "question": self.question,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "image_similarity": self.image_similarity,
            "knowledge_similarity": self.knowledge_similarity,
            "combined_score": self.combined_score,
            "confidence": self.confidence,
            "top_matches": [
                {
                    "scenario_id": match.scenario_id,
                    "combined_score": match.combined_score,
                    "image_similarity": match.image_similarity,
                    "knowledge_similarity": match.knowledge_similarity,
                    "concept": match.concept,
                    "english_kural": match.english_kural
                }
                for match in self.top_matches
            ]
        }


def create_prediction_from_result(
    scenario_id: str,
    knowledge_object: dict,
    image_similarity: float,
    knowledge_similarity: float,
    combined_score: float,
    top_matches: List[MatchResult]
) -> Prediction:
    """
    Create a Prediction object from retrieval results.

    Args:
        scenario_id: The scenario ID of the top match
        knowledge_object: The knowledge object dictionary for the top match
        image_similarity: Image similarity score for the top match
        knowledge_similarity: Knowledge similarity score for the top match
        combined_score: Combined score for the top match
        top_matches: List of top-k MatchResult objects

    Returns:
        Prediction object
    """
    # Extract numeric ID from scenario_id (e.g., "S042" -> 42)
    try:
        kural_id = int(scenario_id[1:])  # Remove 'S' prefix and convert to int
    except ValueError:
        kural_id = -1  # Default if parsing fails

    return Prediction(
        scenario_id=scenario_id,
        kural_id=kural_id,
        concept=knowledge_object.get("concept", "Unknown"),
        adhigaram=knowledge_object.get("adhigaram", "Unknown"),
        paal=knowledge_object.get("paal", "Unknown"),
        english_kural=knowledge_object.get("english_kural", ""),
        scenario=knowledge_object.get("scenario", ""),
        question=knowledge_object.get("question", ""),
        correct_answer=knowledge_object.get("correct_answer", ""),
        explanation=knowledge_object.get("explanation", ""),
        image_similarity=float(image_similarity),
        knowledge_similarity=float(knowledge_similarity),
        combined_score=float(combined_score),
        confidence=float(combined_score),  # Initially, confidence is the combined score
        top_matches=top_matches
    )