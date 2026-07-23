# Backend API for Thirukkural Educational AI

## Architecture

The backend API is built using FastPGI (FastAPI) and serves as the interface between client applications and the AI core of the Thirukkural Scenario-Based Decision-Making System.

### Components

1. **Application Entrypoint** (`backend/app.py`)
   - Creates the FastAPI application
   - Configures middleware (CORS, logging, exception handling)
   - Includes API routers

2. **API Routes** (`backend/routes/`)
   - `predict.py`: Handles image prediction requests
   - `explain.py`: Handles image explanation requests (prediction + explanation)
   - `chat.py`: Handles conversational interactions with the AI
   - `health.py`: Health check endpoint (included in app.py for simplicity)

3. **Request/Response Schemas** (`backend/schemas/`)
   - `request.py`: Pydantic models for request validation
   - `response.py`: Pydantic models for response serialization

4. **AI Service** (`backend/services/ai_service.py`)
   - Singleton service that wraps the AI components (InferenceEngine, ExplainabilityEngine, ConversationEngine)
   - Handles initialization and provides a clean interface for the routes

5. **Middleware** (`backend/middleware/`)
   - `exception_handler.py`: Converts exceptions to JSON responses
   - `logging.py`: Logs each request with timing information

6. **Tests** (`backend/test_api.py`)
   - Test suite for the API endpoints

### Data Flow

The API follows a request-response pattern where:

1. Client sends a request to an endpoint
2. The request is validated by Pydantic models (if applicable)
3. The route handler interacts with the AI Service
4. The AI Service uses the underlying AI components (unchanged from Phases 2.1-3.2)
5. The response is serialized using Pydantic models and returned to the client

## API Endpoints

### Root Endpoint
```
GET /
```
Returns a welcome message.

**Response:**
```json
{
  "message": "Welcome to the Thirukkural Scenario-Based Decision-Making API"
}
```

### Health Check
```
GET /health
```
Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy"
}
```

### Prediction Endpoint
```
POST /predict
```
Accepts an image file and returns the prediction from the inference engine.

**Request:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "scenario_id": "S001",
  "kural_id": 1,
  "concept": "Wisdom",
  "adhigaram": "Chapter 1 (Aram)",
  "paal": "Aram",
  "english_kural": "Having investigated learning, it has been stated that it is unfading. Learning that is enjoyed by children and causes joy is perfect.",
  "scenario": "Student practicing Tamil letter 'அ' on slate before reading words",
  "question": "Your teacher has assigned a new Tamil poem to learn, but you're struggling with the basic letters. Skipping the alphabet practice would let you start the poem sooner. How do you approach your study session?",
  "correct_answer": "A",
  "explanation": "Strong foundations enable confident advancement in learning. When we thoroughly master basic concepts before moving to more complex material, we build lasting understanding that prevents frustration and the wasted effort of having to backtrack and relearn fundamentals later in the learning process.",
  "image_similarity": 1.0,
  "knowledge_similarity": 1.0,
  "combined_score": 1.0,
  "confidence": 1.0,
  "top_matches": [
    {
      "scenario_id": "S001",
      "combined_score": 1.0,
      "image_similarity": 1.0,
      "knowledge_similarity": 1.0,
      "concept": "Wisdom",
      "english_kural": "Having investigated learning, it has been stated that it is unfading. Learning that is enjoyed by children and causes joy is perfect."
    }
  ]
}
```

### Explanation Endpoint
```
POST /explain
```
Accepts an image file, runs prediction, then generates an explanation using the explainability engine.

**Request:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "prediction": { /* Same as prediction response */ },
  "explanation": {
    "prediction_summary": "The uploaded image most closely matches Scenario S001, representing the concept of Wisdom. Therefore, the system retrieved Thirukkural 1.",
    "matched_concept": "Wisdom under Chapter 1 (Aram)",
    "matched_kural": "1",
    "matched_scenario": "S001",
    "scenario_description": "Student practicing Tamil letter 'அ' on slate before reading words",
    "question": "Your teacher has assigned a new Tamil poem to learn, but you're struggling with the basic letters. Skipping the alphabet practice would let you start the poem sooner. How do you approach your study session?",
    "correct_answer": "A",
    "ethical_reasoning": "Strong foundations enable confident advancement in learning. When we thoroughly master basic concepts before moving to more complex material, we build lasting understanding that prevents frustration and the wasted effort of having to backtrack and relearn fundamentals later in the learning process.",
    "confidence_level": "Very High",
    "confidence_value": 1.0,
    "retrieval_scores": {
      "image_similarity": 1.0,
      "knowledge_similarity": 1.0,
      "combined_score": 1.0
    },
    "alternatives": [
      {
        "scenario_id": "S004",
        "concept": "Education",
        "combined_score": 0.68,
        "english_kural": "No fruit have men of all their studied lore,  Save they the 'Purely Wise One's' feet adore"
      }
    ]
  }
}
```

### Chat Endpoints

#### Start a Chat
```
POST /chat
```
Starts a new chat session with an image and a question.

**Request:**
```json
{
  "image": "<base64 encoded image string>",
  "question": "Explain this Kural in simple English."
}
```

**Response:**
```json
{
  "answer": "In simple terms: Strong foundations enable confident advancement in learning. When we thoroughly master basic concepts before moving to more complex material, we build lasting understanding that prevents frustration and the wasted effort of having to backtrack and relearn fundamentals later in the learning process.",
  "prediction": { /* Prediction response */ },
  "explanation": { /* Explanation response */ }
}
```

#### Follow-up Question
```
POST /chat/followup
```
Asks a follow-up question in the current chat session.

**Request:**
```json
{
  "question": "How can I apply this in daily life?"
}
```

**Response:**
```json
{
  "answer": "To apply this principle in daily life, consider how the ethical reasoning from Thirukkural 1 relates to your situation: 'Strong foundations enable confident advancement in learning...'"
}
```

#### Reset Chat
```
DELETE /chat/reset
```
Resets the current chat session.

**Response:**
```json
{
  "message": "Chat session reset"
}
```

## Startup Process

On application startup, the following occurs:

1. The FastAPI application is initialized
2. Middleware is configured (CORS, logging, exception handling)
3. The AI Service singleton is created and initialized:
   - The InferenceEngine is loaded (loads models and embeddings)
   - The ExplainabilityEngine is ready (no explicit loading needed)
   - ConversationEngine instances are created on-demand when a chat starts
4. The application is ready to accept requests

## Error Handling

The API uses centralized exception handling to return consistent JSON error responses:

- **HTTP 400**: Bad Request (e.g., missing parameters, invalid file type)
- **HTTP 422**: Validation Error (e.g., missing required fields in JSON)
- **HTTP 500**: Internal Server Error (unexpected exceptions)

Error response format:
```json
{
  "error": "HTTP 400",
  "message": "File must be an image"
}
```

## Logging

Every request is logged with:
- HTTP method and path
- Status code
- Processing time (in seconds)

Example log entry:
```
INFO:     POST /predict/ Status: 200 Duration: 0.245s
```

## Configuration

Configuration is read from `config/config.py` in the project root. The following settings are used:

- `HOST`: Host to bind the server to (default: "0.0.0.0")
- `PORT`: Port to listen on (default: 8000)
- `DEBUG`: Enable debug mode (default: False)
- `UPLOAD_SIZE`: Maximum upload size in bytes (default: 10MB)
- `CORS_ORIGINS`: List of allowed origins for CORS (default: ["*"])

## Deployment Notes

To run the API server:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

For production, consider using a process manager like Gunicorn with Uvicorn workers.

## Future Authentication Support

While authentication is not implemented in this phase, the API is designed to be extended with authentication middleware. Future work could include:

- Adding OAuth2/JWT authentication
- Protecting endpoints with dependency injection
- Adding rate limiting per user/API key

## Limitations

- The chat endpoint currently supports only a single active session (global state). For multi-user support, a session management system (e.g., using Redis or a database) would be needed.
- Uploaded images are temporarily stored in `/tmp` and deleted after processing.
- The AI components are loaded once at startup and reused for all requests, ensuring efficient resource usage.

## Conclusion

This backend API provides a clean, production-ready interface to the Thirukkural Educational AI system. It strictly adheres to the requirement of not modifying existing AI modules, instead serving as an orchestration layer that initializes and reuses the efficient components built in previous phases.