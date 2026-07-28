from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import base64
import os
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent / "services"))

from inference import InferenceEngine
from explainability import ExplainabilityEngine
from conversation_engine import ConversationEngine
from prediction import Prediction
from explanation import Explanation
from services.ai_service import AIService
from schemas.response import ChatResponse
from schemas.request import ChatRequest, ChatFollowupRequest

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI service (singleton)
ai_service = AIService()
# Global conversation engine for the current session (simple approach)
conversation_engine = None

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

@router.post("/", response_model=ChatResponse)
async def chat_with_image(request: ChatRequest):
    """
    Start a chat session with an image and a question.

    - **image**: Base64 encoded image string
    - **question**: The user's question
    - Returns: Answer, along with the prediction and explanation used to initialize the conversation
    """
    global conversation_engine
    try:
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.image)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image")

        # Save to temporary file
        temp_path = f"/tmp/temp_image_{os.urandom(8).hex()}"
        with open(temp_path, "wb") as f:
            f.write(image_data)

        # Run inference and explanation
        prediction: Prediction = ai_service.predict(temp_path)
        explanation: Explanation = ai_service.explain(prediction)

        # Initialize conversation engine for this session
        conversation_engine = ConversationEngine()
        # Initialize with prediction and explanation
        conversation_engine.initialize(prediction, explanation)
        # Note: In a real app, we would pass a configured model (e.g., OpenAI, Ollama)
        # For now, we use the default (which uses a mock model)

        # Clean up temporary file
        os.remove(temp_path)

        # Get the answer to the question
        answer = conversation_engine.ask(request.question)

        # Convert prediction and explanation to dicts for response validation
        prediction_dict = prediction.to_dict()
        explanation_dict = explanation.to_dict()

        # Return the response
        return ChatResponse(
            answer=answer,
            prediction=prediction_dict,
            explanation=explanation_dict
        )

    except HTTPException:
        # Re-raise HTTP exceptions to let FastAPI handle them
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/followup", response_model=dict)
async def chat_followup(request: ChatFollowupRequest):
    """
    Ask a follow-up question in the current chat session.

    - **question**: The follow-up question
    - Returns: Answer from the conversation engine
    """
    global conversation_engine
    try:
        question = request.question
        if not question:
            raise HTTPException(status_code=400, detail="'question' is required")

        if conversation_engine is None:
            raise HTTPException(status_code=400, detail="No active chat session. Please start a chat with an image first.")

        answer = conversation_engine.ask(question)

        return {"answer": answer}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Followup chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reset", response_model=dict)
async def reset_chat():
    """
    Reset the current chat session.
    """
    global conversation_engine
    try:
        conversation_engine = None
        return {"message": "Chat session reset"}
    except Exception as e:
        logger.error(f"Error resetting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))