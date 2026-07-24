from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from middleware.exception_handler import http_exception_handler, general_exception_handler
from middleware.logging import log_requests
from routes import predict, explain, chat
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Thirukkural Scenario-Based Decision-Making API",
    description="Backend API for the Thirukkural Scenario-Based Decision-Making System",
    version="1.0.0"
)

# Add middleware
app.middleware("http")(log_requests)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router, prefix="/predict", tags=["prediction"])
app.include_router(explain.router, prefix="/explain", tags=["explanation"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the Thirukkural Scenario-Based Decision-Making API"}

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
