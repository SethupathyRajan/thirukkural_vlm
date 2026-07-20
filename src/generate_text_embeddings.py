"""
Generate text embeddings for all textual information in the database.
This script is for Phase 2.4: Text Embedding Generation.
"""

import sys
import time
import numpy as np
import torch
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our infrastructure modules
from config.config import (
    EMBEDDINGS_DIR,
    BATCH_SIZE,
    DEVICE,
    TEXT_MODEL_NAME
)
from src.loader import (
    load_all_scenarios,
    load_all_questions,
    load_all_kurals,
    load_all_concepts
)
from src.model_manager import load_text_model
from src.utils import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

def preprocess_text(text: str) -> str:
    """Preprocess text: strip, replace multiple spaces with single space.

    Args:
        text: Input text string.

    Returns:
        Preprocessed text string.
    """
    if not isinstance(text, str):
        return ""
    # Strip leading/trailing whitespace
    text = text.strip()
    # Replace multiple spaces with a single space
    import re
    text = re.sub(r'\s+', ' ', text)
    return text

def generate_embeddings(
    texts: List[str],
    ids: List[Any],
    batch_size: int,
    device: str,
    model
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate embeddings for a list of texts using batch processing.

    Args:
        texts: List of preprocessed text strings.
        ids: List of corresponding IDs.
        batch_size: Batch size for encoding.
        device: Device to run the model on.
        model: Loaded SentenceTransformer model.

    Returns:
        Tuple of (embeddings_array, ids_array) where:
        - embeddings_array is a float32 numpy array of shape (n_texts, embedding_dim)
        - ids_array is an object numpy array of IDs
    """
    if not texts:
        return np.array([]).reshape(0, 0), np.array([])

    all_embeddings = []

    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        # Generate embeddings for the batch
        with torch.no_grad():
            batch_embeddings = model.encode(
                batch_texts,
                batch_size=len(batch_texts),  # Already batched
                convert_to_numpy=True,
                normalize_embeddings=True,  # This gives us unit norm
                show_progress_bar=False
            )

        # Ensure float32
        batch_embeddings = batch_embeddings.astype(np.float32)

        all_embeddings.append(batch_embeddings)

        logger.debug(f"Processed batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")

    # Concatenate all batches
    if all_embeddings:
        embeddings_array = np.vstack(all_embeddings)
        ids_array = np.array(ids, dtype=object)
    else:
        embeddings_array = np.array([]).reshape(0, 0)
        ids_array = np.array([])

    return embeddings_array, ids_array

def save_embeddings(
    embeddings: np.ndarray,
    ids: np.ndarray,
    field_name: str
) -> None:
    """Save embeddings and IDs to files.

    Args:
        embeddings: Embeddings array of shape (n, dim).
        ids: IDs array of shape (n,).
        field_name: Name of the field (used for filenames).
    """
    if embeddings.size == 0:
        logger.warning(f"No embeddings to save for {field_name}")
        return

    embeddings_path = EMBEDDINGS_DIR / f"{field_name}_embeddings.npy"
    ids_path = EMBEDDINGS_DIR / f"{field_name}_embedding_ids.npy"

    logger.info(f"Saving {field_name} embeddings to {embeddings_path}...")
    np.save(embeddings_path, embeddings)

    logger.info(f"Saving {field_name} IDs to {ids_path}...")
    np.save(ids_path, ids)

def validate_embeddings(
    embeddings: np.ndarray,
    ids: np.ndarray,
    field_name: str
) -> bool:
    """Validate embeddings and IDs.

    Args:
        embeddings: Embeddings array.
        ids: IDs array.
        field_name: Name of the field for logging.

    Returns:
        True if validation passes, False otherwise.
    """
    if embeddings.size == 0:
        logger.warning(f"No embeddings to validate for {field_name}")
        return True  # Nothing to validate

    # Check that number of embeddings matches number of IDs
    if embeddings.shape[0] != ids.shape[0]:
        logger.error(f"{field_name}: Embedding count ({embeddings.shape[0]}) != ID count ({ids.shape[0]})")
        return False

    # Check embedding dimensions (should be 2D)
    if embeddings.ndim != 2:
        logger.error(f"{field_name}: Embeddings array has unexpected shape: {embeddings.shape}")
        return False

    embedding_dim = embeddings.shape[1]
    logger.info(f"{field_name}: Embedding dimension: {embedding_dim}")

    # Check for NaN or Inf values
    if np.any(np.isnan(embeddings)) or np.any(np.isinf(embeddings)):
        logger.error(f"{field_name}: Embeddings contain NaN or Inf values!")
        return False
    else:
        logger.info(f"{field_name}: Embeddings contain no NaN or Inf values.")

    # Check that IDs are unique
    unique_ids = np.unique(ids)
    if len(unique_ids) != len(ids):
        logger.error(f"{field_name}: Duplicate IDs found! Total IDs: {len(ids)}, Unique IDs: {len(unique_ids)}")
        return False
    else:
        logger.info(f"{field_name}: All IDs are unique.")

    # Check that embeddings are normalized (unit length)
    norms = np.linalg.norm(embeddings, axis=1)
    # Allow small tolerance due to floating point
    if not np.allclose(norms, 1.0, atol=1e-6):
        logger.warning(f"{field_name}: Some embeddings are not normalized (max deviation: {np.max(np.abs(norms - 1.0)):.6f})")
        # We normalize again just in case
        embeddings = embeddings / norms[:, np.newaxis]
        logger.info(f"{field_name}: Renormalized embeddings.")
    else:
        logger.info(f"{field_name}: All embeddings are normalized.")

    return True

def main():
    """Generate and save text embeddings for all specified fields."""
    logger.info("=" * 60)
    logger.info("THIRUKKURAL SCENARIO-BASED DECISION-MAKING")
    logger.info("TEXT EMBEDDING GENERATION - PHASE 2.4")
    logger.info("=" * 60)

    start_time = time.time()

    # Ensure embeddings directory exists
    EMBEDDINGS_DIR.mkdir(exist_ok=True)

    # Load the text model
    logger.info(f"Loading text model: {TEXT_MODEL_NAME}...")
    try:
        model = load_text_model()
        logger.info("Text model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load text model: {e}")
        return

    # Move model to the configured device
    model.to(DEVICE)
    logger.info(f"Text model moved to device: {DEVICE}")

    # Define the fields to process: (loader_function, id_field, text_field, output_name)
    fields_to_process = [
        # Scenario: scenario_text
        (load_all_scenarios, 'scenario_id', 'scenario_text', 'scenario'),
        # Question: question_text
        (load_all_questions, 'question_id', 'question_text', 'question'),
        # Explanation: explanation
        (load_all_questions, 'question_id', 'explanation', 'explanation'),
        # Kural: english_kural
        (load_all_kurals, 'kural_id', 'english_kural', 'kural'),
        # Concept: concept_name
        (load_all_concepts, 'concept_id', 'concept_name', 'concept')
    ]

    # Process each field
    results = {}
    for loader_func, id_field, text_field, output_name in fields_to_process:
        logger.info(f"--- Processing {output_name} ---")

        # Load data
        try:
            data = loader_func()
        except Exception as e:
            logger.error(f"Failed to load {output_name} data: {e}")
            continue

        if not data:
            logger.warning(f"No data found for {output_name}")
            results[output_name] = (0, 0)  # processed, skipped
            continue

        # Extract IDs and texts
        ids = []
        texts = []
        skipped_empty = 0

        for item in data:
            item_id = item.get(id_field)
            text = item.get(text_field, "")

            # Preprocess text
            processed_text = preprocess_text(text)

            if not processed_text:
                skipped_empty += 1
                continue

            ids.append(item_id)
            texts.append(processed_text)

        total_records = len(data)
        processed_count = len(texts)
        skipped_count = skipped_empty

        logger.info(f"{output_name}: Total records: {total_records}, "
                    f"Processed: {processed_count}, Skipped (empty): {skipped_count}")

        # Generate embeddings
        if processed_count > 0:
            embeddings, ids_array = generate_embeddings(
                texts=texts,
                ids=ids,
                batch_size=BATCH_SIZE,
                device=DEVICE,
                model=model
            )

            # Save embeddings
            save_embeddings(embeddings, ids_array, output_name)

            # Validate embeddings
            is_valid = validate_embeddings(embeddings, ids_array, output_name)
            if not is_valid:
                logger.error(f"Validation failed for {output_name}")

            results[output_name] = (processed_count, skipped_count)
        else:
            logger.warning(f"No valid text to process for {output_name}")
            results[output_name] = (0, skipped_count)

    # Summary
    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info("=" * 60)
    logger.info("TEXT EMBEDDING GENERATION SUMMARY")
    logger.info("=" * 60)
    total_processed = 0
    total_skipped = 0
    for field_name, (processed, skipped) in results.items():
        logger.info(f"{field_name.capitalize()} Embeddings: {processed}")
        total_processed += processed
        total_skipped += skipped
    logger.info(f"Total records processed: {total_processed}")
    logger.info(f"Total records skipped: {total_skipped}")
    logger.info(f"Time taken: {elapsed_time:.2f} seconds")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()