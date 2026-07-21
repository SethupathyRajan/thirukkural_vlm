# Thirukkural Scenario-Based Decision-Making System: Inference Pipeline

## Overview

The inference pipeline provides a reusable interface for making predictions using the Thirukkural multimodal retrieval system. It accepts image inputs in various formats (file path, PIL Image, or numpy array) and returns structured prediction objects containing the retrieved Thirukkural knowledge object with retrieval metadata.

## System Architecture

The inference engine follows a singleton-like pattern where expensive resources (models, embeddings, knowledge objects) are loaded once during initialization and reused for subsequent predictions. This design ensures optimal performance for applications requiring multiple predictions.

### Component Relationships

```
InferenceEngine
├── Loads resources once:
│   ├── Image model (OpenCLIP ViT-B-32)
│   ├── Precomputed image embeddings
│   ├── Precomputed knowledge embeddings  
│   └── Knowledge objects (Thirukkural scenarios)
├── predict() -> Single prediction
└── predict_top_k() -> Multiple predictions
```

## Prediction Flow

1. **Input Validation**: Accepts image as file path (str/Path), PIL Image, or numpy array (HWC, RGB)
2. **Preprocessing**: Converts all inputs to PIL Image in RGB format
3. **Image Encoding**: Uses OpenCLIP model to generate 512-dimensional image embedding
4. **Similarity Computation**: 
   - Computes cosine similarity between query image and all image embeddings
   - Retrieves top-k candidates by image similarity
   - Computes knowledge similarity using reference embedding approach
5. **Score Fusion**: Combines image and knowledge similarities using weighted sum
6. **Re-ranking**: Applies reciprocal rank fusion for final ranking
7. **Output Formatting**: Creates structured Prediction objects with metadata

## Supported Input Formats

| Format | Description | Example |
|--------|-------------|---------|
| `str` or `Path` | File path to image | `"/path/to/image.jpg"` or `Path("image.jpg")` |
| `PIL.Image.Image` | PIL Image object | `Image.open("image.jpg").convert("RGB")` |
| `numpy.ndarray` | RGB image array (HWC, uint8 or float32/64) | `np.array(Image.open("image.jpg"))` |

All inputs are internally normalized to PIL Image RGB format for processing.

## Output Structure

The `predict()` method returns a `Prediction` object with the following fields:

### Primary Fields
- `scenario_id` (str): Identifier of matched scenario (e.g., "S042")
- `kural_id` (int): Numeric ID extracted from scenario_id (e.g., 42)
- `concept` (str): Concept/category of the matched scenario
- `adhigaram` (str): Chapter of the matched scenario
- `paal` (str): Section of the matched scenario
- `english_kural` (str): English translation of the Thirukkural

### Scenario Details
- `scenario` (str): Scenario description
- `question` (str): Question associated with the scenario
- `correct_answer` (str): Correct answer to the question
- `explanation` (str): Explanation for the correct answer

### Similarity Scores
- `image_similarity` (float): Cosine similarity between input image and matched image embedding [0, 1]
- `knowledge_similarity` (float): Similarity between matched knowledge embedding and reference [0, 1]
- `combined_score` (float): Weighted combination of image and knowledge similarities [0, 1]
- `confidence` (float): Confidence score (currently set equal to combined_score)

### Top Matches
- `top_matches` (List[MatchResult]): Top-k matches including the top-1 result
  - Each `MatchResult` contains:
    - `scenario_id` (str): Scenario identifier
    - `combined_score` (float): Fusion score [0, 1]
    - `image_similarity` (float): Image similarity [0, 1]
    - `knowledge_similarity` (float): Knowledge similarity [0, 1]
    - `concept` (str): Concept of the scenario
    - `english_kural` (str): English translation of the Thirukkural

## Configuration Options

The inference engine reads configuration from `config/config.py`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `DEVICE` | Compute device (`"cuda"` or `"cpu"`) | `"cuda"` if available, else `"cpu"` |
| `RETRIEVAL_TOP_K` | Number of top candidates to consider | `10` |
| `IMAGE_WEIGHT` | Weight for image similarity in fusion | `0.7` |
| `KNOWLEDGE_WEIGHT` | Weight for knowledge similarity in fusion | `0.3` |

Note: `IMAGE_WEIGHT + KNOWLEDGE_WEIGHT` should equal `1.0` for proper normalization.

## Error Handling

The inference engine provides comprehensive error handling:

| Error Condition | Exception Type | Description |
|-----------------|----------------|-------------|
| Non-existent image file | `FileNotFoundError` | Raised when image file path doesn't exist |
| Corrupted/unreadable image | `ValueError` | Raised when image file cannot be opened or decoded |
| Unsupported input type | `ValueError` | Raised when input is not str/Path, PIL Image, or numpy array |
| Invalid numpy array shape/dtype | `ValueError` | Raised when numpy array doesn't meet HWC, RGB requirements |
| Model loading failure | `RuntimeError` | Raised when OpenCLIP model fails to load |
| Embedding loading failure | `RuntimeError` | Raised when embedding files are missing or corrupted |
| Prediction failure | `RuntimeError` | Raised when encoding or retrieval processes fail |

## Performance Characteristics

### Initialization
- **One-time cost**: Loading model (~2-5 seconds) and embeddings (~0.5-2 seconds)
- **Memory usage**: ~500MB for model + embeddings + knowledge objects

### Prediction Latency
- **Typical**: 50-200ms per prediction on CPU
- **GPU accelerated to 178ms on GPU
-initialization)
- **Factors affecting latency**:
  - Image preprocessing time
  - Model inference time (OpenCLIP ViT-B-32)
  - Similarity computation (CPU-bound for small datasets)
  - Score fusion and re-ranking overhead

### Throughput Optimization
For batch processing applications:
1. Load the inference engine once
2. Call `predict()` or `predict_top_k()` repeatedly
3. The engine reuses loaded resources, avoiding reload overhead

## Usage Examples

### Basic Usage
```python
from src.inference import InferenceEngine

# Initialize and load resources (do this once)
engine = InferenceEngine()
engine.load()

# Make a prediction
prediction = engine.predict("path/to/image.jpg")

# Access results
print(f"Matched scenario: {prediction.scenario_id}")
print(f"Confidence: {prediction.confidence:.3f}")
print(f"Explanation: {prediction.explanation}")

# Get top-k predictions
top_5 = engine.predict_top_k("path/to/image.jpg", k=5)
for i, pred in enumerate(top_5):
    print(f"{i+1}. {pred.scenario_id} (score: {pred.combined_score:.3f})")
```

### With Different Input Types
```python
from PIL import Image
import numpy as np
from src.inference import InferenceEngine

engine = InferenceEngine()
engine.load()

# File path
pred1 = engine.predict("/images/sample.jpg")

# PIL Image
pil_img = Image.open("/images/sample.jpg").convert("RGB")
pred2 = engine.predict(pil_img)

# Numpy array
np_img = np.array(pil_img)
pred3 = engine.predict(np_img)
```

### Performance Monitoring
```python
from src.inference import InferenceEngine
import time

engine = InferenceEngine()
engine.load()

# Track prediction latency
start = time.time()
prediction = engine.predict("image.jpg")
latency = time.time() - start

# Get average latency over multiple runs
avg_latency = engine.get_average_prediction_time()

# Reset tracking
engine.reset_performance_tracking()
```

## Integration Notes

### Thread Safety
The inference engine is **not thread-safe** by design. For multi-threaded applications:
- Create one instance per thread, or
- Implement external synchronization when sharing an instance

### Resource Management
- Explicitly call `load()` before making predictions
- The engine holds resources in memory until garbage collected
- For long-running applications, the engine can persist for the lifetime of the application

### Serialization
Prediction objects can be serialized using the `to_dict()` method:
```python
prediction_dict = prediction.to_dict()
# Can be JSON serialized, stored in databases, etc.
```

## Limitations and Future Work

### Current Limitations
1. **Single Image Input**: Currently processes one image at a time
2. **Fixed Confidence Scoring**: Confidence is currently set equal to combined_score (no calibration)
3. **CPU-based Similarity**: Knowledge similarity computation runs on CPU
4. **Static Embeddings**: Uses precomputed embeddings; no online learning capability

### Planned Enhancements
1. **Batch Processing**: Add support for batch image inputs
2. **Confidence Calibration**: Implement Platt scaling or isotonic regression for better confidence estimates
3. **GPU Acceleration**: Move similarity computation to GPU for large knowledge bases
4. **Dynamic Embeddings**: Option to compute embeddings on-the-fly for out-of-distribution inputs

## Conclusion

The inference pipeline provides a production-ready interface for the Thirukkural retrieval system that balances performance, usability, and correctness. By loading resources once and providing flexible input handling, it enables efficient integration into various applications while maintaining the accuracy of the underlying multimodal retrieval engine.