"""
Exception handling middleware for the Thirukkural Educational API.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": f"HTTP {exc.status_code}", "message": exc.detail}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "An unexpected error occurred"}
    )