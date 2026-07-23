"""
Request schemas for the Thirukkural Educational API.
"""

from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """Request for starting a chat with an image and question."""
    image: str  # Base64 encoded image
    question: str

class ChatFollowupRequest(BaseModel):
    """Request for a follow-up question in an existing chat."""
    question: str

# Note: For predict and explain, we use file uploads, so no request body model is needed.