"""
Generate embeddings for knowledge objects.
This script is for Phase 2.6: Knowledge Embedding Generation.
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

def load_knowledge_objects(filepath: Path) -> List[Dict[str, Any]]:
    """Load knowledge objects from JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        List of knowledge object dictionaries.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        knowledge_objects = json.load(f)
    return knowledge_objects

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

def semantic_consistency_check(
    embeddings: np.ndarray,
    ids: np.ndarray,
    knowledge_objects: List[Dict[str, Any]],
    num_samples: int = 10,
    top_k: int = 5
) -> None:
    """Perform a semantic consistency check on the embeddings.

    For a random sample of knowledge objects, compute cosine similarity
    against all other embeddings and report the top-k nearest neighbors.

    Args:
        embeddings: Embeddings array of shape (n, dim).
        ids: IDs array of shape (n,).
        knowledge_objects: List of knowledge object dictionaries.
        num_samples: Number of random samples to check.
        top_k: Number of top neighbors to report.
    """
    if embeddings.size == 0:
        logger.warning("No embeddings to perform semantic consistency check.")
        return

    # Create a mapping from scenario_id to index in the embeddings array
    id_to_index = {str(id_val): idx for idx, id_val in enumerate(ids)}

    # Get indices of the knowledge objects that have valid embeddings
    valid_indices = []
    for obj in knowledge_objects:
        scenario_id = str(obj.get('scenario_id'))
        if scenario_id in id_to_index:
            valid_indices.append(id_to_index[scenario_id])

    if not valid_indices:
        logger.warning("No valid knowledge objects with embeddings found for semantic consistency check.")
        return

    # Randomly select samples from the valid indices
    np.random.seed(42)  # For reproducibility
    if len(valid_indices) < num_samples:
        samples = valid_indices
        logger.warning(f"Not enough valid knowledge objects for sampling. Using all {len(samples)}.")
    else:
        samples = np.random.choice(valid_indices, size=num_samples, replace=False)

    logger.info(f"Performing semantic consistency check on {len(samples)} random knowledge objects.")

    # Normalize embeddings (though they should already be normalized from the model)
    # But we do it again to be safe
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    normalized_embeddings = embeddings / norms

    for idx in samples:
        scenario_id = str(ids[idx])
        # Get the embedding vector for this sample
        query_embedding = normalized_embeddings[idx:idx+1]  # Shape (1, dim)

        # Compute cosine similarity with all embeddings
        # Since embeddings are normalized, cosine similarity is just dot product
        similarities = np.dot(normalized_embeddings, query_embedding.T).flatten()

        # Get the top-k+1 indices (including itself)
        top_indices = np.argsort(similarities)[::-1][:top_k+1]

        # Remove the query itself (if present)
        top_indices = [i for i in top_indices if i != idx][:top_k]

        logger.info(f"--- Knowledge Object: {scenario_id} ---")
        for i, neighbor_idx in enumerate(top_indices):
            neighbor_id = str(ids[neighbor_idx])
            similarity_score = similarities[neighbor_idx]
            logger.info(f"  Neighbor {i+1}: {neighbor_id} (similarity: {similarity_score:.4f})")

def main():
    """Generate and save embeddings for knowledge objects."""
    logger.info("=" * 60)
    logger.info("THIRUKKURAL SCENARIO-BASED DECISION-MAKING")
    logger.info("KNOWLEDGE EMBEDDING GENERATION - PHASE 2.6")
    logger.info("=" * 60)

    start_time = time.time()

    # Ensure embeddings directory exists
    EMBEDDINGS_DIR.mkdir(exist_ok=True)

    # Load knowledge objects from the JSON file generated in Phase 2.5
    knowledge_objects_path = Path(__file__).parent.parent / "dataset" / "knowledge_objects.json"
    logger.info(f"Loading knowledge objects from {knowledge_objects_path}...")
    try:
        knowledge_objects = load_knowledge_objects(knowledge_objects_path)
        logger.info(f"Loaded {len(knowledge_objects)} knowledge objects")
    except Exception as e:
        logger.error(f"Failed to load knowledge objects: {e}")
        return

    # Extract IDs and knowledge texts
    ids = []
    texts = []
    skipped_empty = 0

    for obj in knowledge_objects:
        scenario_id = obj.get('scenario_id')
        knowledge_text = obj.get('knowledge_text', "")

        # Preprocess text
        processed_text = preprocess_text(knowledge_text)

        if not processed_text:
            skipped_empty += 1
            continue

        ids.append(scenario_id)
        texts.append(processed_text)

    total_records = len(knowledge_objects)
    processed_count = len(texts)
    skipped_count = skipped_empty

    logger.info(f"Knowledge objects: Total records: {total_records}, "
                f"Processed: {processed_count}, Skipped (empty): {skipped_count}")

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
        save_embeddings(embeddings, ids_array, "knowledge")

        # Validate embeddings
        is_valid = validate_embeddings(embeddings, ids_array, "knowledge")
        if not is_valid:
            logger.error("Validation failed for knowledge embeddings")

        # Perform semantic consistency check
        logger.info("--- Semantic Consistency Check ---")
        semantic_consistency_check(embeddings, ids_array, knowledge_objects, num_samples=10, top_k=5)

        results = {"knowledge": (processed_count, skipped_count)}
    else:
        logger.warning("No valid knowledge text to process")
        results = {"knowledge": (0, skipped_count)}

    # Summary
    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info("=" * 60)
    logger.info("KNOWLEDGE EMBEDDING GENERATION SUMMARY")
    logger.info("=" * 60)
    total_processed = 0
    total_skipped = 0
    for field_name, (processed, skipped) in results.items():
        logger.info(f"{field_name.capitalize()} Embeddings: {processed}")
        total_processed += processed
        total_skipped += skipped
    logger.info(f"Total records processed: {total_processed}")
    logger.info(f"Total records skipped: {total_skipped}")
    if embeddings.size > 0:
        logger.info(f"Embedding dimension: {embeddings.shape[1]}")
    logger.info(f"Time taken: {elapsed_time:.2f} seconds")
    logger.info("=" * 60)

if __name__ == "__main__":
    import json  # Import json here to avoid top-level import if not needed
    main()