"""
Response schemas for the Thirukkural Educational API.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MatchResult(BaseModel):
    """Represents a single match result from the retrieval."""
    scenario_id: str
    combined_score: float
    image_similarity: float
    knowledge_similarity: float
    concept: str
    english_kural: str

class PredictionResponse(BaseModel):
    """Response for a prediction request."""
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
    top_matches: List[MatchResult]

    class Config:
        orm_mode = True

class ExplanationResponse(BaseModel):
    """Response for an explanation request."""
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

    class Config:
        orm_mode = True

class ExplainResponse(BaseModel):
    """Response for an explanation request (combined prediction and explanation)."""
    prediction: PredictionResponse
    explanation: ExplanationResponse

    class Config:
        orm_mode = True

class ChatResponse(BaseModel):
    """Response for a chat request."""
    answer: str
    prediction: PredictionResponse
    explanation: ExplanationResponse

    class Config:
        orm_mode = True