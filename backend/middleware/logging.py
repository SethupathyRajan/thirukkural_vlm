"""
Logging middleware for the Thirukkural Educational API.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next: Callable):
    """
    Log incoming requests and their processing time.
    """
    start_time = time.time()

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log the request
    logger.info(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {process_time:.3f}s"
    )

    return response