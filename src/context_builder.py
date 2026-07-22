"""
Context builder for the Educational Conversation Engine.

This module builds a context string from a Prediction and Explanation
that can be used to ground conversations with an LLM.
"""

from typing import Dict, Any, List
from explanation import Explanation
from prediction import Prediction, MatchResult


class ContextBuilder:
    """
    Builds a context string from a Prediction and Explanation for use in
    educational conversations.
    """

    def __init__(self, include_alternatives: bool = True):
        """
        Initialize the context builder.

        Args:
            include_alternatives: Whether to include alternative matches in the context.
        """
        self.include_alternatives = include_alternatives

    def build_context(self, prediction: Prediction, explanation: Explanation) -> str:
        """
        Build a comprehensive context string from prediction and explanation.

        Args:
            prediction: Prediction object from inference engine
            explanation: Explanation object from explainability engine

        Returns:
            Formatted context string
        """
        context_parts = []

        # Header
        context_parts.append("THIRUKKURAL SCENARIO-BASED DECISION-MAKING CONTEXT")
        context_parts.append("=" * 60)
        context_parts.append("")

        # Core scenario information
        context_parts.append("SCENARIO INFORMATION:")
        context_parts.append(f"  Scenario ID: {explanation.matched_scenario}")
        context_parts.append(f"  Description: {explanation.scenario_description}")
        context_parts.append(f"  Question: {explanation.question}")
        context_parts.append(f"  Correct Answer: {explanation.correct_answer}")
        context_parts.append("")

        # Ethical reasoning from Thirukkural
        context_parts.append("ETHICAL REASONING (THIRUKKURAL):")
        context_parts.append(f"  Thirukkural: {explanation.matched_kural}")
        context_parts.append(f"  Concept: {explanation.matched_concept}")
        context_parts.append(f"  Explanation: {explanation.ethical_reasoning}")
        context_parts.append("")

        # Confidence and retrieval evidence
        context_parts.append("RETREIVAL EVIDENCE:")
        context_parts.append(f"  Confidence Level: {explanation.confidence_level}")
        context_parts.append(f"  Confidence Score: {explanation.confidence_value}")
        context_parts.append(f"  Image Similarity: {explanation.retrieval_scores['image_similarity']}")
        context_parts.append(f"  Knowledge Similarity: {explanation.retrieval_scores['knowledge_similarity']}")
        context_parts.append(f"  Combined Score: {explanation.retrieval_scores['combined_score']}")
        context_parts.append("")

        # Alternative matches (if included and available)
        if self.include_alternatives and explanation.alternatives:
            context_parts.append("ALTERNATIVE MATCHES CONSIDERED:")
            for i, alt in enumerate(explanation.alternatives, 1):
                context_parts.append(
                    f"  {i}. Scenario {alt['scenario_id']} "
                    f"(Concept: {alt['concept']}, "
                    f"Score: {alt['combined_score']}, "
                    f"Kural: {alt.get('english_kural', 'N/A')})"
                )
            context_parts.append("")

        # Additional prediction details
        context_parts.append("ADDITIONAL DETAILS:")
        context_parts.append(f"  Chapter (Adhigaram): {prediction.adhigaram}")
        context_parts.append(f"  Section (Paal): {prediction.paal}")
        context_parts.append(f"  English Translation: {prediction.english_kural}")
        context_parts.append("")

        # Footer
        context_parts.append("=" * 60)
        context_parts.append("Use only the information provided above to answer questions.")
        context_parts.append("Do not use external knowledge or make up information.")
        context_parts.append("=" * 60)

        return "\n".join(context_parts)

    def build_short_context(self, prediction: Prediction, explanation: Explanation) -> str:
        """
        Build a shorter context string for concise conversations.

        Args:
            prediction: Prediction object from inference engine
            explanation: Explanation object from explainability engine

        Returns:
            Short formatted context string
        """
        context_parts = []

        context_parts.append(f"Scenario: {explanation.scenario_description}")
        context_parts.append(f"Question: {explanation.question}")
        context_parts.append(f"Correct Answer: {explanation.correct_answer}")
        context_parts.append(f"Thirukkural {explanation.matched_kural}: {explanation.ethical_reasoning}")
        context_parts.append(f"Concept: {explanation.matched_concept}")
        context_parts.append(f"Confidence: {explanation.confidence_level} ({explanation.confidence_value})")

        return " | ".join(context_parts)