import logging
from typing import Optional
import torch
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# These will be set by the model manager when the model is loaded
_model = None
_preprocess = None

def load_model() -> None:
    """Load the image model and preprocess function.

    This function delegates to the model loader to load the actual model.
    It sets the global _model and _preprocess variables.
    """
    global _model, _preprocess
    from src.model_manager import load_image_model
    try:
        model, preprocess = load_image_model()
        _model = model
        _preprocess = preprocess
        logging.getLogger(__name__).info("Image model loaded successfully.")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to load image model: {e}")
        raise

def preprocess_image(image: Image.Image) -> torch.Tensor:
    """Preprocess a PIL image for the model.

    Args:
        image: A PIL Image object.

    Returns:
        Preprocessed image tensor ready for model input.

    Note:
        This function must be called after load_model().
    """
    if _preprocess is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return _preprocess(image).unsqueeze(0)  # Add batch dimension

def encode_image(image: Image.Image) -> Optional[np.ndarray]:
    """Encode an image into an embedding vector.

    Args:
        image: A PIL Image object.

    Returns:
        The embedding vector as a numpy array, or None if encoding fails.
    """
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    try:
        # Preprocess the image
        input_tensor = preprocess_image(image)

        # Move to the same device as the model
        device = next(_model.parameters()).device
        input_tensor = input_tensor.to(device)

        # Encode the image
        with torch.no_grad():
            # For OpenCLIP, the model.encode_image method returns the image features
            image_features = _model.encode_image(input_tensor)

            # If the model returns a tuple (some models do), take the first element
            if isinstance(image_features, tuple):
                image_features = image_features[0]

        # Convert to numpy array and remove batch dimension
        embedding = image_features.cpu().numpy().squeeze(0)

        # Ensure it's a 1D array
        if embedding.ndim > 1:
            # Flatten if necessary (should be 1D already for CLIP-like models)
            embedding = embedding.flatten()

        # Normalize to unit length (L2 norm)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.astype(np.float32)
    except Exception as e:
        logger.error(f"Failed to encode image: {e}")
        return None
