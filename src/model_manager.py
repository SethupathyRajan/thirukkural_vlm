import logging
from typing import Tuple, Any
from config.config import DEVICE, IMAGE_MODEL_NAME, IMAGE_MODEL_PRETRAINED, TEXT_MODEL_NAME

logger = logging.getLogger(__name__)

# Cache for loaded models
_image_model_cache = None
_image_preprocess_cache = None
_text_model_cache = None

def load_image_model() -> tuple:
    """Load the image model and preprocessing function.
    
    Returns:
        A tuple (model, preprocess) where model is the image model and
        preprocess is a function that takes a PIL image and returns a tensor.
        
    Note:
        This function uses OpenCLIP. The model is moved to the configured device.
    """
    global _image_model_cache, _image_preprocess_cache
    if _image_model_cache is not None and _image_preprocess_cache is not None:
        return _image_model_cache, _image_preprocess_cache
    
    try:
        import torch
        import open_clip
    except ImportError as e:
        logging.getLogger(__name__).error(f"Required package not installed for image model: {e}")
        raise
    
    try:
        logger.info(f"Loading image model: {IMAGE_MODEL_NAME} with pretrained {IMAGE_MODEL_PRETRAINED}")
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name=IMAGE_MODEL_NAME,
            pretrained=IMAGE_MODEL_PRETRAINED,
            device=DEVICE
        )
        model.eval()  # set to evaluation mode
        _image_model_cache = model
        _image_preprocess_cache = preprocess
        logger.info("Image model loaded successfully.")
        return _image_model_cache, _image_preprocess_cache
    except Exception as e:
        logger.error(f"Failed to load image model: {e}")
        raise

def load_text_model() -> Any:
    """Load the text model.
    
    Returns:
        A SentenceTransformer model instance.
        
    Note:
        The model is moved to the configured device.
    """
    global _text_model_cache
    if _text_model_cache is not None:
        return _text_model_cache
    
    try:
        from sentence_transformers import SentenceTransformer
        import torch
    except ImportError as e:
        logger.error(f"Required package not installed for text model: {e}")
        raise
    
    try:
        logger.info(f"Loading text model: {TEXT_MODEL_NAME}")
        model = SentenceTransformer(TEXT_MODEL_NAME, device=DEVICE)
        _text_model_cache = model
        logger.info("Text model loaded successfully.")
        return _text_model_cache
    except Exception as e:
        logger.error(f"Failed to load text model: {e}")
        raise
