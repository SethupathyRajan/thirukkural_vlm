import logging
from typing import Optional, Any
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

def preprocess_image(image: Image.Image) -> Any:
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

def encode_image(image: Image.Image) -> Optional[any]:
    """Encode an image into an embedding vector.
    
    Args:
        image: A PIL Image object.
        
    Returns:
        The embedding vector as a numpy array, or None if not implemented.
        
    Note:
        This function is a stub in this phase. In the next phase, it will
        return the actual embedding from the model.
    """
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    # This is a stub: do not compute actual embeddings in this phase.
    logger.warning("Image encoding is not implemented in this phase. Returning None.")
    return None
