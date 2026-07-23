from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "services"))

from inference import InferenceEngine
from prediction import Prediction
from explanation import Explanation
from services.ai_service import AIService
from schemas.response import ExplainResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI service (singleton)
ai_service = AIService()

@router.on_event("startup")
async def load_models():
    """Load the AI service on startup."""
    global ai_service
    try:
        ai_service.initialize()
        logger.info("AI service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")
        raise

@router.post("/", response_model=ExplainResponse)
async def explain_image(file: UploadFile = File(...)):
    """
    Get an explanation for the Thirukkural scenario in an uploaded image.

    - **file**: Image file (JPEG, PNG, etc.)
    - Returns: Explanation object including prediction summary, concept, ethical reasoning, etc.
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

        # Generate explanation using the AI service
        explanation: Explanation = ai_service.explain(prediction)

        # Clean up temporary file
        os.remove(temp_path)

        # Return the response using Pydantic models
        return ExplainResponse(
            prediction=prediction,
            explanation=explanation
        )

    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))