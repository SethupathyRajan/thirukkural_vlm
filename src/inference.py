"""
Inference engine for the Thirukkural Scenario-Based Decision-Making system.

This module provides a reusable inference pipeline that encapsulates the
multimodal retrieval engine for use in applications (web, mobile, API, etc.).
"""

import time
import torch
import numpy as np
from pathlib import Path
from typing import Union, List, Tuple, Optional, Dict, Any
from PIL import Image

# Import our own modules
from config.config import (
    EMBEDDINGS_DIR,
    DEVICE,
    RETRIEVAL_TOP_K,
    IMAGE_WEIGHT,
    KNOWLEDGE_WEIGHT
)
from src.image_encoder import load_model as load_image_encoder_model, preprocess_image, encode_image
from src.model_manager import load_image_model
from src.multimodal_retrieval import (
    encode_user_image,
    retrieve_top_k,
    load_embeddings,
    load_knowledge_objects
)
from src.prediction import Prediction, MatchResult, create_prediction_from_result
from src.utils import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)


class InferenceEngine:
    """
    A reusable inference engine for the Thirukkural retrieval system.

    The engine loads all necessary resources (model, embeddings, knowledge objects)
    once during initialization and provides fast prediction methods for subsequent use.
    """

    def __init__(self):
        """Initialize the inference engine with lazy loading."""
        self._image_model = None
        self._image_preprocess = None
        self._image_embeddings = None
        self._image_ids = None
        self._knowledge_embeddings = None
        self._knowledge_ids = None
        self._knowledge_objects = None
        self._device = DEVICE
        self._is_loaded = False

        # Performance tracking
        self._init_time = None
        self._prediction_times = []

    def _clip_score(self, score: float) -> float:
        """Clip a score to the range [0, 1]."""
        return max(0.0, min(1.0, float(score)))

    def load(self) -> None:
        """
        Load all required resources: image model, embeddings, and knowledge objects.
        This method should be called once before making predictions.
        """
        start_time = time.time()
        logger.info("Loading inference engine...")

        try:
            # 1. Load image model
            logger.info("Loading image model...")
            self._image_model, self._image_preprocess = load_image_model()
            logger.info("Image model loaded successfully.")

            # 2. Load embeddings
            logger.info("Loading embeddings...")
            self._image_embeddings, self._image_ids, self._knowledge_embeddings, self._knowledge_ids = load_embeddings()
            logger.info("Embeddings loaded successfully.")

            # 3. Load knowledge objects
            logger.info("Loading knowledge objects...")
            knowledge_objects_path = Path(__file__).parent.parent / "dataset" / "knowledge_objects.json"
            self._knowledge_objects = load_knowledge_objects(knowledge_objects_path)
            logger.info(f"Loaded {len(self._knowledge_objects)} knowledge objects.")

            self._is_loaded = True
            self._init_time = time.time() - start_time
            logger.info(f"Inference engine ready. Initialization took {self._init_time:.2f} seconds.")

        except Exception as e:
            logger.error(f"Failed to load inference engine: {e}")
            self._is_loaded = False
            raise

    def _ensure_loaded(self) -> None:
        """Ensure the engine is loaded before making predictions."""
        if not self._is_loaded:
            raise RuntimeError(
                "Inference engine not loaded. Call 'load()' before making predictions."
            )

    def _validate_and_preprocess_image(
        self, image_input: Union[str, Path, Image.Image, np.ndarray]
    ) -> Image.Image:
        """
        Validate and convert various image inputs to a PIL Image.

        Args:
            image_input: Image as file path, PIL Image, or numpy array (HWC, RGB, uint8 or float)

        Returns:
            PIL Image object in RGB mode

        Raises:
            ValueError: If the input format is not supported or the image is invalid
            FileNotFoundError: If the image file does not exist
        """
        # Handle string or Path
        if isinstance(image_input, (str, Path)):
            image_path = Path(image_input)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            try:
                image = Image.open(image_path).convert("RGB")
            except Exception as e:
                raise ValueError(f"Cannot open image file {image_path}: {e}")

        # Handle PIL Image
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")

        # Handle numpy array
        elif isinstance(image_input, np.ndarray):
            # Check array shape and type
            if image_input.ndim != 3 or image_input.shape[2] != 3:
                raise ValueError(
                    "Numpy array must have shape (height, width, 3) for RGB image"
                )

            # Convert to PIL Image
            if image_input.dtype == np.float32 or image_input.dtype == np.float64:
                # Assume float array is in [0, 1] range
                array_uint8 = (np.clip(image_input, 0, 1) * 255).astype(np.uint8)
            elif image_input.dtype == np.uint8:
                array_uint8 = image_input.copy()
            else:
                raise ValueError(
                    "Numpy array must be of type uint8 or float (32/64 bit)"
                )

            image = Image.fromarray(array_uint8, mode="RGB")

        else:
            raise ValueError(
                f"Unsupported image input type: {type(image_input)}. "
                "Supported types: str, Path, PIL.Image.Image, numpy.ndarray"
            )

        return image

    def predict(
        self, image_input: Union[str, Path, Image.Image, np.ndarray]
    ) -> Prediction:
        """
        Make a prediction for a single image.

        Args:
            image_input: Image as file path, PIL Image, or numpy array

        Returns:
            Prediction object containing the top-1 result and metadata
        """
        start_time = time.time()
        self._ensure_loaded()

        try:
            # 1. Validate and preprocess image
            image = self._validate_and_preprocess_image(image_input)

            # 2. Save image to a temporary file if it's not already a file path
            # The retrieve_top_k function expects a Path to an image file
            if isinstance(image_input, (str, Path)):
                image_path = Path(image_input)
            else:
                # For PIL Image or numpy array, we need to save it to a temporary file
                import tempfile
                import os

                # Create a temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                temp_file.close()

                # Save the image
                image.save(temp_file.name, format='JPEG')
                image_path = Path(temp_file.name)

                # We'll need to clean up this file later
                _temp_file_to_cleanup = image_path

            try:
                # 3. Use the existing retrieve_top_k function from multimodal_retrieval
                results = retrieve_top_k(
                    query_image_path=image_path,
                    image_embeddings=self._image_embeddings,
                    image_ids=self._image_ids,
                    knowledge_embeddings=self._knowledge_embeddings,
                    knowledge_ids=self._knowledge_ids,
                    knowledge_objects=self._knowledge_objects,
                    k=RETRIEVAL_TOP_K
                )

                if not results:
                    raise RuntimeError("No retrieval results returned")

                # 4. Process the results to create Prediction objects
                # Get the top-1 result
                top_result = results[0]
                top_scenario_id = top_result["scenario_id"]

                # Get the knowledge object for the top result
                top_ko = top_result.get("knowledge_object")
                if top_ko is None:
                    # Fallback: create a minimal knowledge object
                    top_ko = {
                        "scenario_id": top_scenario_id,
                        "concept": "Unknown",
                        "adhigaram": "Unknown",
                        "paal": "Unknown",
                        "english_kural": "",
                        "scenario": "",
                        "question": "",
                        "correct_answer": "",
                        "explanation": "",
                    }

                # 5. Create MatchResult objects for all results
                top_matches: List[MatchResult] = []
                for result in results:
                    scenario_id = result["scenario_id"]
                    ko = result.get("knowledge_object")
                    if ko is None:
                        ko = {
                            "scenario_id": scenario_id,
                            "concept": "Unknown",
                            "adhigaram": "Unknown",
                            "paal": "Unknown",
                            "english_kural": "",
                            "scenario": "",
                            "question": "",
                            "correct_answer": "",
                            "explanation": "",
                        }

                    match = MatchResult(
                        scenario_id=scenario_id,
                        combined_score=self._clip_score(result["combined_score"]),
                        image_similarity=self._clip_score(result["image_similarity"]),
                        knowledge_similarity=self._clip_score(result["knowledge_similarity"]),
                        concept=ko.get("concept", "Unknown"),
                        english_kural=ko.get("english_kural", ""),
                    )
                    top_matches.append(match)

                # 6. Create the prediction object from the top-1 result
                prediction = create_prediction_from_result(
                    scenario_id=top_scenario_id,
                    knowledge_object=top_ko,
                    image_similarity=self._clip_score(top_result["image_similarity"]),
                    knowledge_similarity=self._clip_score(top_result["knowledge_similarity"]),
                    combined_score=self._clip_score(top_result["combined_score"]),
                    top_matches=top_matches
                )

                # Record prediction time
                pred_time = time.time() - start_time
                self._prediction_times.append(pred_time)

                logger.info(f"Prediction completed in {pred_time:.3f} seconds.")
                return prediction

            finally:
                # Clean up temporary file if we created one
                if not isinstance(image_input, (str, Path)):
                    try:
                        os.unlink(image_path)
                    except Exception:
                        pass  # Ignore cleanup errors

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def predict_top_k(
        self, image_input: Union[str, Path, Image.Image, np.ndarray], k: int = None
    ) -> List[Prediction]:
        """
        Get top-k predictions for a single image.

        Args:
            image_input: Image as file path, PIL Image, or numpy array
            k: Number of top predictions to return (default: RETRIEVAL_TOP_K from config)

        Returns:
            List of Prediction objects, sorted by combined score (descending)
        """
        if k is None:
            k = RETRIEVAL_TOP_K

        # We'll reuse the prediction logic but return all top-k
        start_time = time.time()
        self._ensure_loaded()

        try:
            # 1. Validate and preprocess image
            image = self._validate_and_preprocess_image(image_input)

            # 2. Save image to a temporary file if it's not already a file path
            if isinstance(image_input, (str, Path)):
                image_path = Path(image_input)
            else:
                # For PIL Image or numpy array, we need to save it to a temporary file
                import tempfile
                import os

                # Create a temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                temp_file.close()

                # Save the image
                image.save(temp_file.name, format='JPEG')
                image_path = Path(temp_file.name)

                # We'll need to clean up this file later
                _temp_file_to_cleanup = image_path

            try:
                # 3. Use the existing retrieve_top_k function from multimodal_retrieval
                results = retrieve_top_k(
                    query_image_path=image_path,
                    image_embeddings=self._image_embeddings,
                    image_ids=self._image_ids,
                    knowledge_embeddings=self._knowledge_embeddings,
                    knowledge_ids=self._knowledge_ids,
                    knowledge_objects=self._knowledge_objects,
                    k=k  # Use requested k
                )

                if not results:
                    raise RuntimeError("No retrieval results returned")

                # 4. Build predictions for each of the top-k results
                predictions: List[Prediction] = []
                for result in results:
                    scenario_id = result["scenario_id"]
                    ko = result.get("knowledge_object")
                    if ko is None:
                        ko = {
                            "scenario_id": scenario_id,
                            "concept": "Unknown",
                            "adhigaram": "Unknown",
                            "paal": "Unknown",
                            "english_kural": "",
                            "scenario": "",
                            "question": "",
                            "correct_answer": "",
                            "explanation": "",
                        }

                    # For each candidate, we need to create a prediction object
                    pred = create_prediction_from_result(
                        scenario_id=scenario_id,
                        knowledge_object=ko,
                        image_similarity=self._clip_score(result["image_similarity"]),
                        knowledge_similarity=self._clip_score(result["knowledge_similarity"]),
                        combined_score=self._clip_score(result["combined_score"]),
                        top_matches=[]  # For individual predictions, we don't need to recompute top-matches
                    )
                    predictions.append(pred)

                # Record prediction time
                pred_time = time.time() - start_time
                self._prediction_times.append(pred_time)

                logger.info(f"Top-{k} prediction completed in {pred_time:.3f} seconds.")
                return predictions

            finally:
                # Clean up temporary file if we created one
                if not isinstance(image_input, (str, Path)):
                    try:
                        os.unlink(image_path)
                    except Exception:
                        pass  # Ignore cleanup errors

        except Exception as e:
            logger.error(f"Top-k prediction failed: {e}")
            raise

    def get_average_prediction_time(self) -> float:
        """
        Get the average prediction time based on recent predictions.

        Returns:
            Average prediction time in seconds, or 0.0 if no predictions have been made
        """
        if not self._prediction_times:
            return 0.0
        return sum(self._prediction_times) / len(self._prediction_times)

    def reset_performance_tracking(self) -> None:
        """Reset the prediction time tracking."""
        self._prediction_times = []

    @property
    def is_loaded(self) -> bool:
        """Check if the engine has been loaded."""
        return self._is_loaded

    @property
    def initialization_time(self) -> Optional[float]:
        """Get the initialization time in seconds."""
        return self._init_time