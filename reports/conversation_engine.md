# Educational Conversation Engine

## Overview

The Educational Conversation Engine is a component of the Thirukkural Scenario-Based Decision-Making System that enables natural language interactions about the retrieved Thirukkural knowledge. It grounds all responses in the provided prediction and explanation context, ensuring that the conversation remains faithful to the retrieved knowledge without performing additional retrieval or accessing external knowledge sources.

## Architecture

The conversation engine follows this architecture:

```
User Question
      ↓
Conversation Engine
      ↓
Context Builder (uses Prediction + Explanation)
      ↓
Conversation Model (LLM abstraction)
      ↓
Educational Response
```

### Components

1. **Context Builder** (`src/context_builder.py`)
   - Creates a structured context string from Prediction and Explanation objects
   - Includes scenario information, ethical reasoning, confidence scores, and alternative matches
   - Provides both full and condensed context formats

2. **Conversation Memory** (`src/conversation_memory.py`)
   - Manages short-term conversation history for a single session
   - Stores user questions and assistant responses
   - Provides methods to add, retrieve, clear, and reset conversation history
   - Configurable history length to prevent excessive context growth

3. **Conversation Models** (`src/conversation_models.py`)
   - Abstraction layer for different LLM providers
   - `BaseConversationModel`: Abstract base class defining the interface
   - `MockConversationModel`: Rule-based model for testing and development
   - Placeholders for `OpenAIConversationModel` and `OllamaConversationModel`
   - Separates the conversation logic from specific LLM implementations

4. **Conversation Engine** (`src/conversation_engine.py`)
   - Main orchestrator that ties all components together
   - Initializes with Prediction and Explanation to set the conversation context
   - Handles user questions and generates responses using the conversation model
   - Manages conversation history and context updates

## Conversation Flow

1. **Initialization**: The engine is initialized with a Prediction object (from the inference engine) and an Explanation object (from the explainability engine).

2. **Context Building**: The ContextBuilder creates a comprehensive context string containing:
   - Scenario description, question, and correct answer
   - Ethical reasoning from the Thirukkural
   - Matched concept, chapter (adhigaram), and section (paal)
   - Confidence level and similarity scores
   - Alternative matches considered (if configured)

3. **Question Processing**: When a user asks a question:
   - The question is added to conversation history
   - The conversation model generates a response using:
     - System prompt (educational guidelines)
     - Conversation history (for context awareness)
     - User question
     - The built context (grounding in Thirukkural knowledge)
   - The response is added to conversation history
   - The response is returned to the user

4. **Conversation Management**: 
   - History can be retrieved, cleared, or reset
   - Context can be updated if the underlying prediction/explanation changes
   - The engine ensures all responses are grounded in the provided context

## Context Construction

The context includes the following elements from the Prediction and Explanation:

- **Scenario Information**: ID, description, question, correct answer
- **Ethical Reasoning**: Thirukkural number, concept, chapter, section, and explanation
- **Retrieval Evidence**: Confidence level and scores (image, knowledge, combined)
- **Alternative Matches**: Optional list of alternative scenarios considered
- **Additional Details**: Chapter, section, and English translation of the Thirukkural

This context is provided to the conversation model to ensure all responses are based solely on the retrieved knowledge.

## Prompt Engineering

The system uses a structured prompting approach:

### System Panel
```
You are an educational assistant that helps users understand Thirukkural 
concepts and ethical reasoning. You must answer questions based ONLY on 
the provided context from the Thirukkural Scenario-Based Decision-Making 
system. Do not use external knowledge or make up information. If the 
context does not contain sufficient information to answer a question, 
clearly state that the answer cannot be determined from the retrieved 
knowledge. Keep responses educational, clear, and grounded in the 
provided Thirukkural context.
```

### Context Injection
The constructed context is provided as a system message: `"Context: [built context string]"`

### Conversation History
Previous exchanges are included to maintain conversational context.

### User Query
The current question from the user.

## Conversation Model Abstraction

The design separates the conversation logic from the specific LLM implementation:

1. **BaseConversationModel**: Abstract base class defining the interface
   - `generate_response(system_prompt, history, user_query, context) -> str`
   - `is_available() -> bool`

2. **MockConversationModel**: 
   - Rule-based responses for testing
   - Pattern matching for common question types (explain, example, apply, etc.)
   - Always available for development and testing

3. **Extensibility**: 
   - To add a new LLM provider, inherit from BaseConversationModel
   - Implement the generate_response and is_available methods
   - Examples provided for OpenAI and Ollama (as placeholders)

## Educational Styles

The system supports different response styles through prompt engineering and model configuration:

- **Simple**: Basic explanations in accessible language
- **Detailed**: Comprehensive responses with contextual details
- **Student-level**: Age-appropriate explanations (school vs. college)
- **Comparative**: Drawing connections between concepts (when multiple contexts available)
- **Practical**: Focus on real-world application

These styles can be achieved by:
1. Modifying the system prompt
2. Fine-tuning the generation parameters (temperature, max_tokens, etc.)
3. Implementing specialized prompting strategies in specific model implementations

## Grounding and Safety

The system implements several mechanisms to ensure responses are grounded and safe:

1. **Context-Only Responses**: The system prompt explicitly instructs the model to use only the provided context
2. **Knowledge Boundary Awareness**: Instructions to state when information is not available in the context
3. **No External Retrieval**: The engine does not perform additional lookup or access external databases
4. **No Kural Invention**: The model cannot mention Thirukkurals not present in the context
5. **Consistent Ethical Reasoning**: Responses must align with the provided ethical explanation

## Usage Example

```python
from src.inference import InferenceEngine
from src.explainability import ExplainabilityEngine
from src.conversation_engine import ConversationEngine

# Initialize engines
inference_engine = InferenceEngine()
inference_engine.load()

# Make a prediction
prediction = inference_engine.predict("path/to/image.jpg")

# Generate explanation
explainability_engine = ExplainabilityEngine()
explanation = explainability_engine.generate_explanation(prediction)

# Initialize conversation engine
conversation = ConversationEngine()
conversation.initialize(prediction, explanation)

# Ask questions
response1 = conversation.ask("Explain this Kural in simple English.")
print(response1)

response2 = conversation.ask("Give me another real-life example.")
print(response2)

# Continue conversation...
response3 = conversation.ask("How can I apply this in daily life?")
print(response3)
```

## Configuration

The system reads configuration from `config/config.py`:

- **Model Provider**: Selected through instantiation of specific model classes
- **Temperature**: Controls response randomness (lower = more deterministic)
- **Max Tokens**: Limits response length
- **Conversation Style**: Influenced by system prompt and model parameters
- **Memory Length**: Configured in ConversationMemory (default: 10 exchanges)

## Limitations

1. **Context Bound**: Responses are limited to the information in the initial prediction and explanation
2. **No Dynamic Retrieval**: The engine cannot access additional Thirukkural couplets beyond the initial context
3. **Model Dependence**: Response quality depends on the underlying conversation model
4. **Single Context**: Designed for one scenario per conversation; switching contexts requires re-initialization
5. **No Multi-turn Reasoning**: Complex reasoning across multiple turns is limited by the model's capabilities

## Future Improvements

1. **Dynamic Context Expansion**: Allow limited, bounded retrieval of related Thirukkural concepts when explicitly requested for comparison
2. **Enhanced Memory**: Implement summarization of long conversations to maintain relevance
3. **Multi-modal Input**: Extend to handle questions about the input image itself
4. **Feedback Mechanism**: Allow users to indicate when responses are helpful or inaccurate
5. **Language Support**: Extend to handle questions in Tamil or other languages
6. **Structured Output**: Option to return responses in structured formats (e.g., JSON) for programmatic use