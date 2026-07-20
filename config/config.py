import os
from pathlib import Path

# Try to import torch for device detection, default to cpu if not available
try:
    import torch
    _torch_available = True
except ImportError:
    _torch_available = False

def get_device():
    """Get the appropriate device for model inference."""
    if not _torch_available:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Dataset directory (not used in this phase, but kept for reference)
DATASET_DIR = BASE_DIR / "dataset"

# Database directory
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "metadata.db"

# Embeddings directory
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
EMBEDDINGS_DIR.mkdir(exist_ok=True)

# Indexes directory
INDEXES_DIR = BASE_DIR / "indexes"
INDEXES_DIR.mkdir(exist_ok=True)

# Models directory
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Device configuration (computed lazily via function)
# For backward compatibility, we define DEVICE as a variable that calls the function
# Note: This will be evaluated at import time, but the function handles missing torch.
DEVICE = get_device()

# Model names (can be overridden by environment variables or config file)
TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
IMAGE_MODEL_NAME = os.getenv("IMAGE_MODEL_NAME", "ViT-B-32")
IMAGE_MODEL_PRETRAINED = os.getenv("IMAGE_MODEL_PRETRAINED", "laion2b_s34b_b79k")

# Embedding configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", "224"))  # for OpenCLIP

# Retrieval configuration
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "10"))
IMAGE_WEIGHT = float(os.getenv("IMAGE_WEIGHT", "0.7"))
KNOWLEDGE_WEIGHT = float(os.getenv("KNOWLEDGE_WEIGHT", "0.3"))

# Future: index configuration (e.g., FAISS index type)
INDEX_TYPE = os.getenv("INDEX_TYPE", "FlatL2")  # example for FAISS
