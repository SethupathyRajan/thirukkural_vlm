"""
Explainability engine for the Thirukkural Scenario-Based Decision-Making system.

This module provides tools to generate human-readable explanations for predictions
made by the inference engine.
"""

from explanation import Explanation
from prediction import Prediction, MatchResult
from config.config import (
    EXPLAINABILITY_DECIMAL_PRECISION,
    EXPLAINABILITY_NUM_ALTERNATIVE_MATCHES,
    CONFIDENCE_VERY_HIGH_THRESHOLD,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MODERATE_THRESHOLD
)


class ExplainabilityEngine:
    """
    Generates explanations for predictions made by the inference engine.
    """

    def __init__(self):
        """Initialize the explainability engine."""
        pass

    def _get_confidence_level(self, score: float) -> str:
        """
        Determine the confidence level label based on thresholds.

        Args:
            score: Confidence score (between 0 and 1).

        Returns:
            A string label: "Very High", "High", "Moderate", or "Low".
        """
        if score >= CONFIDENCE_VERY_HIGH_THRESHOLD:
            return "Very High"
        elif score >= CONFIDENCE_HIGH_THRESHOLD:
            return "High"
        elif score >= CONFIDENCE_MODERATE_THRESHOLD:
            return "Moderate"
        else:
            return "Low"

    def _round_value(self, value: float) -> float:
        """
        Round a float to the configured decimal precision.

        Args:
            value: Value to round.

        Returns:
            Rounded value.
        """
        return round(value, EXPLAINABILITY_DECIMAL_PRECISION)

    def generate_explanation(self, prediction: Prediction) -> Explanation:
        """
        Generate a structured explanation for a prediction.

        Args:
            prediction: Prediction object from the inference engine.

        Returns:
            Explanation object containing explanation components.
        """
        # Determine confidence level
        confidence_level = self._get_confidence_level(prediction.confidence)
        confidence_value = self._round_value(prediction.confidence)

        # Prepare similarity scores dictionary
        similarity_scores = {
            "image_similarity": self._round_value(prediction.image_similarity),
            "knowledge_similarity": self._round_value(prediction.knowledge_similarity),
            "combined_score": self._round_value(prediction.combined_score)
        }

        # Build the matched concept string (concept, adhigaram, paal)
        concept_parts = [prediction.concept]
        if prediction.adhigaram and prediction.adhigaram not in ["Unknown", ""]:
            concept_parts.append(f"under {prediction.adhigaram}")
        if prediction.paal and prediction.paal not in ["None", ""]:
            # paal might be stored as a string like "Aram" or None
            if isinstance(prediction.paal, str) and prediction.paal.strip():
                concept_parts.append(f"({prediction.paal})")
        matched_concept = " ".join(part for part in concept_parts if part)

        # Build the prediction summary
        prediction_summary = (
            f"The uploaded image most closely matches Scenario {prediction.scenario_id}, "
            f"representing the concept of {prediction.concept}. "
            f"Therefore, the system retrieved Thirukkural {prediction.kural_id}."
        )

        # Prepare alternative matches (excluding the top match)
        alternative_matches = []
        # We'll take the top N from prediction.top_matches, skipping the first (which is the top match)
        # But note: prediction.top_matches includes the top match as the first element.
        # We want up to EXPLAINABILITY_NUM_ALTERNATIVE_MATCHES alternatives.
        for match in prediction.top_matches[1: 1 + EXPLAINABILITY_NUM_ALTERNATIVE_MATCHES]:
            alternative_matches.append({
                "scenario_id": match.scenario_id,
                "combined_score": self._round_value(match.combined_score),
                "concept": match.concept,
                "english_kural": match.english_kural
            })

        # Create the Explanation object
        explanation = Explanation(
            prediction_summary=prediction_summary,
            matched_concept=matched_concept,
            matched_kural=str(prediction.kural_id),  # Ensure it's a string
            matched_scenario=prediction.scenario_id,
            scenario_description=getattr(prediction, 'scenario', ''),
            question=getattr(prediction, 'question', ''),
            correct_answer=getattr(prediction, 'correct_answer', ''),
            ethical_reasoning=getattr(prediction, 'explanation', ''),
            confidence_level=confidence_level,
            confidence_value=confidence_value,
            retrieval_scores=similarity_scores,
            alternatives=alternative_matches
        )

        return explanation

    def format_explanation(self, explanation: Explanation) -> str:
        """
        Format the explanation into a human-readable string.

        Args:
            explanation: Explanation object.

        Returns:
            Formatted multi-line string.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("THIRUKKURAL SCENARIO-BASED DECISION-MAKING EXPLANATION")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Prediction Summary: {explanation.prediction_summary}")
        lines.append("")
        lines.append(f"Matched Concept: {explanation.matched_concept}")
        lines.append("")
        lines.append(f"Matched Kural: {explanation.matched_kural}")
        lines.append(f"Matched Scenario ID: {explanation.matched_scenario}")
        lines.append("")
        lines.append("Scenario Description:")
        lines.append(f"  {explanation.scenario_description}")
        lines.append("")
        lines.append("Question:")
        lines.append(f"  {explanation.question}")
        lines.append("")
        lines.append("Correct Answer:")
        lines.append(f"  {explanation.correct_answer}")
        lines.append("")
        lines.append("Ethical Reasoning (Explanation):")
        lines.append(f"  {explanation.ethical_reasoning}")
        lines.append("")
        lines.append("Confidence Assessment:")
        lines.append(f"  Level: {explanation.confidence_level}")
        lines.append(f"  Score: {explanation.confidence_value}")
        lines.append("")
        lines.append("Retrieval Evidence:")
        lines.append(f"  Image Similarity: {explanation.retrieval_scores['image_similarity']}")
        lines.append(f"  Knowledge Similarity: {explanation.retrieval_scores['knowledge_similarity']}")
        lines.append(f"  Combined Score: {explanation.retrieval_scores['combined_score']}")
        lines.append("")
        lines.append("Alternative Matches Considered:")
        if explanation.alternatives:
            for i, alt in enumerate(explanation.alternatives, start=1):
                lines.append(
                    f"  {i}. Scenario {alt['scenario_id']} "
                    f"(Concept: {alt['concept']}, "
                    f"Combined Score: {alt['combined_score']}, "
                    f"Kural: {alt['english_kural']})"
                )
        else:
            lines.append("  No alternative matches available.")
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)