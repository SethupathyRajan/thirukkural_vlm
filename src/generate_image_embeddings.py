"""
Generate image embeddings for all scenarios in the database.
This script is for Phase 2.3: Image Embedding Generation.
"""

import sys
import time
import numpy as np
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import torch

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our infrastructure modules
from config.config import (
    EMBEDDINGS_DIR,
    BATCH_SIZE,
    DEVICE
)
from src.loader import load_all_scenarios
from src.image_encoder import load_model as load_image_encoder_model, preprocess_image, encode_image
from src.utils import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

def main():
    """Generate and save image embeddings for all scenarios."""
    logger.info("=" * 60)
    logger.info("THIRUKKURAL SCENARIO-BASED DECISION-MAKING")
    logger.info("IMAGE EMBEDDING GENERATION - PHASE 2.3")
    logger.info("=" * 60)

    start_time = time.time()

    # Ensure embeddings directory exists
    EMBEDDINGS_DIR.mkdir(exist_ok=True)

    # Load the image encoder model (which loads the OpenCLIP model and preprocess)
    logger.info("Loading image model...")
    try:
        load_image_encoder_model()
        logger.info("Image model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load image model: {e}")
        return

    # Load all scenarios from the database
    logger.info("Loading scenarios from database...")
    scenarios = load_all_scenarios()
    total_scenarios = len(scenarios)
    logger.info(f"Total scenarios to process: {total_scenarios}")

    # Lists to hold embeddings and corresponding Scenario IDs
    embeddings_list = []
    ids_list = []
    skipped_count = 0

    # Process in batches
    logger.info(f"Processing images in batches of size {BATCH_SIZE}...")
    for i in range(0, total_scenarios, BATCH_SIZE):
        batch_scenarios = scenarios[i:i+BATCH_SIZE]
        batch_images = []
        batch_ids = []

        # Prepare the batch: load and validate images
        for scenario in batch_scenarios:
            scenario_id = scenario['scenario_id']
            image_path = scenario['image_path']

            # Check if image file exists
            if not Path(image_path).exists():
                logger.warning(f"Image file not found for scenario {scenario_id}: {image_path}")
                skipped_count += 1
                continue

            # Try to open the image
            try:
                image = Image.open(image_path).convert("RGB")
                batch_images.append(image)
                batch_ids.append(scenario_id)
            except UnidentifiedImageError:
                logger.warning(f"Cannot identify image file for scenario {scenario_id}: {image_path}")
                skipped_count += 1
            except Exception as e:
                logger.warning(f"Error opening image for scenario {scenario_id}: {e}")
                skipped_count += 1

        # If we have images in this batch, process them
        if batch_images:
            try:
                # Preprocess all images in the batch
                logger.debug(f"Preprocessing batch of {len(batch_images)} images...")
                preprocessed_tensors = [preprocess_image(img) for img in batch_images]
                # Concatenate along batch dimension: each tensor is [1, 3, H, W], result is [batch_size, 3, H, W]
                batch_tensor = torch.cat(preprocessed_tensors, dim=0)
                # Move to the same device as the model
                # Get the model's device from the image_encoder module
                from src.image_encoder import _model
                if _model is not None:
                    device = next(_model.parameters()).device
                else:
                    # Fallback to configured device
                    device = torch.device(DEVICE)
                batch_tensor = batch_tensor.to(device)

                # Generate embeddings for the batch
                logger.debug(f"Generating embeddings for batch of {len(batch_images)} images...")
                with torch.no_grad():
                    # For OpenCLIP, we can encode the batch directly
                    # The model's encode_image method expects a batch tensor
                    image_features = _model.encode_image(batch_tensor)

                    # If the model returns a tuple (some models do), take the first element
                    if isinstance(image_features, tuple):
                        image_features = image_features[0]

                    # Convert to numpy array
                    embeddings_batch = image_features.cpu().numpy()

                    # Ensure it's 2D: (batch_size, embedding_dim)
                    if embeddings_batch.ndim == 1:
                        # If only one sample, reshape to (1, embedding_dim)
                        embeddings_batch = embeddings_batch.reshape(1, -1)

                    # Normalize each embedding to unit length (L2 norm)
                    norms = np.linalg.norm(embeddings_batch, axis=1, keepdims=True)
                    # Avoid division by zero
                    norms[norms == 0] = 1
                    embeddings_batch = embeddings_batch / norms

                # Add embeddings and IDs to the lists
                embeddings_list.extend(embeddings_batch.astype(np.float32))
                ids_list.extend(batch_ids)

                logger.info(f"Processed batch {i//BATCH_SIZE + 1}/{(total_scenarios + BATCH_SIZE - 1)//BATCH_SIZE}: "
                            f"{len(batch_images)} images, {len(embeddings_batch)} successful.")
            except Exception as e:
                logger.error(f"Error processing batch starting at index {i}: {e}")
                # Skip the entire batch? We'll skip the batch and count all as skipped.
                skipped_count += len(batch_images)
                continue

    # Convert lists to numpy arrays
    if embeddings_list:
        embeddings_array = np.array(embeddings_list, dtype=np.float32)
        ids_array = np.array(ids_list, dtype=object)  # Store strings as object array
    else:
        embeddings_array = np.array([]).reshape(0, 0)
        ids_array = np.array([])

    # Save the embeddings and IDs
    embeddings_path = EMBEDDINGS_DIR / "image_embeddings.npy"
    ids_path = EMBEDDINGS_DIR / "image_embedding_ids.npy"

    logger.info(f"Saving embeddings to {embeddings_path}...")
    np.save(embeddings_path, embeddings_array)

    logger.info(f"Saving IDs to {ids_path}...")
    np.save(ids_path, ids_array)

    # Validation
    logger.info("--- Validation ---")
    if embeddings_array.size > 0:
        # Check that the number of embeddings matches the number of IDs
        if embeddings_array.shape[0] == ids_array.shape[0]:
            logger.info(f"Number of embeddings ({embeddings_array.shape[0]}) matches number of IDs ({ids_array.shape[0]}).")
        else:
            logger.error(f"Mismatch: embeddings count {embeddings_array.shape[0]} != IDs count {ids_array.shape[0]}")

        # Check that all embeddings have the same dimension
        if embeddings_array.ndim == 2:
            embedding_dim = embeddings_array.shape[1]
            logger.info(f"Embedding dimension: {embedding_dim}")

            # Check for any NaN or Inf values
            if np.any(np.isnan(embeddings_array)) or np.any(np.isinf(embeddings_array)):
                logger.warning("Embeddings contain NaN or Inf values!")
            else:
                logger.info("Embeddings contain no NaN or Inf values.")

            # Check that IDs are unique
            unique_ids = np.unique(ids_array)
            if len(unique_ids) != len(ids_array):
                logger.warning(f"Duplicate IDs found! Total IDs: {len(ids_array)}, Unique IDs: {len(unique_ids)}")
            else:
                logger.info("All IDs are unique.")

            # Check that the number of embeddings matches the number of IDs
            if len(embeddings_array) != len(ids_array):
                logger.error(f"Mismatch: {len(embeddings_array)} embeddings vs {len(ids_array)} IDs")
            else:
                logger.info(f"Number of embeddings matches number of IDs: {len(embeddings_array)}")
        else:
            logger.error(f"Embeddings array has unexpected shape: {embeddings_array.shape}")
    else:
        logger.warning("No embeddings were generated.")

    # Summary
    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info("=" * 60)
    logger.info("IMAGE EMBEDDING GENERATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total scenarios: {total_scenarios}")
    logger.info(f"Images processed: {total_scenarios - skipped_count}")
    logger.info(f"Successful embeddings: {len(embeddings_list)}")
    logger.info(f"Skipped images: {skipped_count}")
    if embeddings_array.size > 0:
        logger.info(f"Embedding dimension: {embeddings_array.shape[1]}")
    logger.info(f"Time taken: {elapsed_time:.2f} seconds")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()