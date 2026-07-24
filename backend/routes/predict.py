from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "services"))

from inference import InferenceEngine
from prediction import Prediction, MatchResult
from services.ai_service import AIService
from schemas.response import PredictionResponse, MatchResult as ResponseMatchResult

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI service (singleton)
ai_service = AIService()
# Initialize AI service (singleton)
ai_service = AIService()

@router.on_event("startup")
async def load_model():
    """Load the AI service on startup."""
    global ai_service
    try:
        ai_service.initialize()
        logger.info("AI service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")
        raise

@router.post("/", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...)):
    """
    Predict the Thirukkural scenario for an uploaded image.

    - **file**: Image file (JPEG, PNG, etc.)
    - Returns: Prediction result
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read file content
        contents = await file.read()

        # Save to temporary file
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Make prediction using the AI service
        prediction: Prediction = ai_service.predict(temp_path)

        # Clean up temporary file
        os.remove(temp_path)

        # Convert Prediction to PredictionResponse
        top_matches = []
        for match in prediction.top_matches:
            top_matches.append(
                ResponseMatchResult(
                    scenario_id=match.scenario_id,
                    combined_score=match.combined_score,
                    image_similarity=match.image_similarity,
                    knowledge_similarity=match.knowledge_similarity,
                    concept=match.concept,
                    english_kural=match.english_kural
                )
            )

        response = PredictionResponse(
            scenario_id=prediction.scenario_id,
            kural_id=prediction.kural_id,
            concept=prediction.concept,
            adhigaram=prediction.adhigaram,
            paal=prediction.paal,
            english_kural=prediction.english_kural,
            scenario=prediction.scenario,
            question=prediction.question,
            correct_answer=prediction.correct_answer,
            explanation=prediction.explanation,
            image_similarity=prediction.image_similarity,
            knowledge_similarity=prediction.knowledge_similarity,
            combined_score=prediction.combined_score,
            confidence=prediction.confidence,
            top_matches=top_matches
        )

        return response

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))