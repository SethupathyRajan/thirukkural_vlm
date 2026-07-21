"""
Multimodal Retrieval Engine (Baseline) for Phase 2.7.
This script implements a retrieval engine that combines image similarity and semantic knowledge similarity.
"""

import sys
import time
import logging
import numpy as np
import torch
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our infrastructure modules
from config.config import (
    EMBEDDINGS_DIR,
    DEVICE,
    RETRIEVAL_TOP_K,
    IMAGE_WEIGHT,
    KNOWLEDGE_WEIGHT
)
from src.loader import load_all_scenarios
from src.image_encoder import load_model as load_image_encoder_model, preprocess_image, encode_image
from src.model_manager import load_text_model
from src.utils import setup_logging, get_logger
import json

# Set up logging
setup_logging()
logger = get_logger(__name__)

def load_embeddings() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load precomputed embeddings and IDs.

    Returns:
        Tuple of (image_embeddings, image_ids, knowledge_embeddings, knowledge_ids)
    """
    image_embeddings_path = EMBEDDINGS_DIR / "image_embeddings.npy"
    image_ids_path = EMBEDDINGS_DIR / "image_embedding_ids.npy"
    knowledge_embeddings_path = EMBEDDINGS_DIR / "knowledge_embeddings.npy"
    knowledge_ids_path = EMBEDDINGS_DIR / "knowledge_embedding_ids.npy"

    logger.info(f"Loading image embeddings from {image_embeddings_path}...")
    image_embeddings = np.load(image_embeddings_path)
    image_ids = np.load(image_ids_path, allow_pickle=True)

    logger.info(f"Loading knowledge embeddings from {knowledge_embeddings_path}...")
    knowledge_embeddings = np.load(knowledge_embeddings_path)
    knowledge_ids = np.load(knowledge_ids_path, allow_pickle=True)

    logger.info(f"Loaded {len(image_ids)} image embeddings and {len(knowledge_ids)} knowledge embeddings.")
    return image_embeddings, image_ids, knowledge_embeddings, knowledge_ids

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

def _load_image_model():
    """Load the image encoder model (sets globals in image_encoder module)."""
    try:
        load_image_encoder_model()
        logger.info("Image encoder model loaded.")
    except Exception as e:
        logger.error(f"Failed to load image encoder model: {e}")
        raise

def encode_user_image(image_path: Path) -> np.ndarray:
    """Encode a user image using the OpenCLIP model.

    Args:
        image_path: Path to the image file.

    Returns:
        Image embedding as a numpy array.
    """
    # Load the image encoder model (sets globals in image_encoder module)
    try:
        load_image_encoder_model()
    except Exception as e:
        logger.error(f"Failed to load image encoder model: {e}")
        raise

    # Load and preprocess the image
    from PIL import Image, UnidentifiedImageError
    try:
        image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}")
        raise
    except UnidentifiedImageError:
        logger.error(f"Cannot identify image file: {image_path}")
        raise
    except Exception as e:
        logger.error(f"Error opening image: {e}")
        raise

    # Encode the image using the image_encoder module's function
    try:
        from src.image_encoder import encode_image
        encoder_output = encode_image(image)
        if encoder_output is None:
            raise RuntimeError("Image encoding returned None")
        return encoder_output
    except Exception as e:
        logger.error(f"Failed to encode image: {e}")
        raise

def cosine_similarity(query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between a query vector and a matrix of embeddings.

    Args:
        query: Query vector of shape (dim,).
        embeddings: Embeddings matrix of shape (n, dim).

    Returns:
        Similarity scores of shape (n,).
    """
    # Ensure query is 2D for dot product
    if query.ndim == 1:
        query = query.reshape(1, -1)
    # Since embeddings are normalized, we can just do dot product
    similarities = np.dot(embeddings, query.T).flatten()
    return similarities

def get_top_k_candidates(
    similarities: np.ndarray,
    ids: np.ndarray,
    k: int
) -> Tuple[List[str], List[float], List[int]]:
    """Get top-k candidates based on similarity scores.

    Args:
        similarities: Similarity scores of shape (n,).
        ids: Corresponding IDs of shape (n,).
        k: Number of top candidates to retrieve.

    Returns:
        Tuple of (candidate_ids, candidate_scores, candidate_indices)
    """
    # Get indices of top-k similarities (descending order)
    top_indices = np.argsort(similarities)[::-1][:k]
    candidate_ids = [str(id_val) for id_val in ids[top_indices]]
    candidate_scores = similarities[top_indices].tolist()
    candidate_indices = top_indices.tolist()
    return candidate_ids, candidate_scores, candidate_indices

def compute_knowledge_similarity(
    reference_embedding: np.ndarray,
    candidate_embeddings: np.ndarray
) -> np.ndarray:
    """Compute cosine similarity between a reference embedding and candidate embeddings.

    Args:
        reference_embedding: Reference vector of shape (dim,).
        candidate_embeddings: Candidates matrix of shape (n, dim).

    Returns:
        Similarity scores of shape (n,).
    """
    return cosine_similarity(reference_embedding, candidate_embeddings)

def combine_scores(
    image_sims: List[float],
    knowledge_sims: List[float],
    image_weight: float,
    knowledge_weight: float
) -> List[float]:
    """Combine image and knowledge similarities using weighted fusion.

    Args:
        image_sims: List of image similarity scores.
        knowledge_sims: List of knowledge similarity scores.
        image_weight: Weight for image similarity.
        knowledge_weight: Weight for knowledge similarity.

    Returns:
        List of combined scores.
    """
    combined = [
        image_weight * img_sim + knowledge_weight * know_sim
        for img_sim, know_sim in zip(image_sims, knowledge_sims)
    ]
    return combined

def rerank_candidates(
    candidate_ids: List[str],
    image_sims: List[float],
    knowledge_sims: List[float],
    combined_scores: List[float]
) -> List[Dict[str, Any]]:
    """Rerank candidates based on combined scores.

    Args:
        candidate_ids: List of candidate scenario IDs.
        image_sims: List of image similarity scores.
        knowledge_sims: List of knowledge similarity scores.
        combined_scores: List of combined scores.

    Returns:
        List of dictionaries with candidate info, sorted by combined score descending.
    """
    candidates = []
    for i, cid in enumerate(candidate_ids):
        candidates.append({
            "scenario_id": cid,
            "image_similarity": image_sims[i],
            "knowledge_similarity": knowledge_sims[i],
            "combined_score": combined_scores[i]
        })
    # Sort by combined score descending
    candidates.sort(key=lambda x: x["combined_score"], reverse=True)
    return candidates

def get_knowledge_object(
    scenario_id: str,
    knowledge_objects: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Retrieve the knowledge object for a given scenario ID.

    Args:
        scenario_id: Scenario ID to look up.
        knowledge_objects: List of all knowledge objects.

    Returns:
        Knowledge object dictionary or None if not found.
    """
    for obj in knowledge_objects:
        if obj.get("scenario_id") == scenario_id:
            return obj
    return None

def retrieve_top_k(
    query_image_path: Path,
    image_embeddings: np.ndarray,
    image_ids: np.ndarray,
    knowledge_embeddings: np.ndarray,
    knowledge_ids: np.ndarray,
    knowledge_objects: List[Dict[str, Any]],
    k: int = 10
) -> List[Dict[str, Any]]:
    """Retrieve top-k candidates for a given query image.

    Args:
        query_image_path: Path to the query image.
        image_embeddings: Image embeddings matrix.
        image_ids: Image IDs array.
        knowledge_embeddings: Knowledge embeddings matrix.
        knowledge_ids: Knowledge IDs array.
        knowledge_objects: List of knowledge objects.
        k: Number of top candidates to retrieve.

    Returns:
        List of dictionaries containing the top-k candidates with their scores and knowledge objects.
    """
    start_time = time.time()
    logger.info(f"Encoding query image: {query_image_path}")
    try:
        query_embedding = encode_user_image(query_image_path)
    except Exception as e:
        logger.error(f"Failed to encode query image: {e}")
        return []

    logger.info("Computing image similarity...")
    image_sims = cosine_similarity(query_embedding, image_embeddings)  # Shape (n,)

    logger.info(f"Getting top-{k} candidates by image similarity...")
    top_k_ids, top_k_scores, top_k_indices = get_top_k_candidates(image_sims, image_ids, k)

    if not top_k_ids:
        logger.warning("No candidates found.")
        return []

    # Use the top image candidate's knowledge embedding as reference for knowledge similarity
    top_candidate_id = top_k_ids[0]
    try:
        top_candidate_idx_in_knowledge = np.where(knowledge_ids == top_candidate_id)[0][0]
    except IndexError:
        logger.warning(f"Knowledge embedding not found for top candidate {top_candidate_id}")
        # If we don't have the knowledge embedding for the top candidate, we cannot compute knowledge similarity.
        # In this case, we set knowledge similarity to 0 for all candidates.
        know_sims = [0.0] * len(top_k_ids)
    else:
        reference_know_emb = knowledge_embeddings[top_candidate_idx_in_knowledge]
        # Get knowledge embeddings for the top-k candidates
        candidate_know_embs = []
        for cand_id in top_k_ids:
            try:
                cand_idx = np.where(knowledge_ids == cand_id)[0][0]
                candidate_know_embs.append(knowledge_embeddings[cand_idx])
            except IndexError:
                logger.warning(f"Knowledge embedding not found for candidate {cand_id}")
                candidate_know_embs.append(np.zeros_like(reference_know_emb))  # Use zero vector if missing
        candidate_know_embs = np.array(candidate_know_embs)
        # Compute knowledge similarity
        know_sims = compute_knowledge_similarity(reference_know_emb, candidate_know_embs)

    # Combine scores
    combined_scores = combine_scores(
        top_k_scores,
        know_sims,
        IMAGE_WEIGHT,
        KNOWLEDGE_WEIGHT
    )

    # Log details for each candidate (debug level)
    logger.debug("Candidate details after score combination:")
    for i, cid in enumerate(top_k_ids):
        logger.debug(
            f"  Candidate {cid}: "
            f"Image Sim: {top_k_scores[i]:.4f}, "
            f"Knowledge Sim: {know_sims[i]:.4f}, "
            f"Image Weight: {IMAGE_WEIGHT}, "
            f"Knowledge Weight: {KNOWLEDGE_WEIGHT}, "
            f"Combined: {combined_scores[i]:.4f}"
        )

    # Rerank candidates
    reranked = rerank_candidates(
        top_k_ids,
        top_k_scores,
        know_sims,
        combined_scores
    )

    # Attach knowledge objects to each candidate
    for candidate in reranked:
        ko = get_knowledge_object(candidate["scenario_id"], knowledge_objects)
        candidate["knowledge_object"] = ko

    elapsed = time.time() - start_time
    logger.info(f"Retrieval completed in {elapsed:.2f} seconds.")
    return reranked

def evaluate_retrieval(
    image_embeddings: np.ndarray,
    image_ids: np.ndarray,
    knowledge_embeddings: np.ndarray,
    knowledge_ids: np.ndarray,
    knowledge_objects: List[Dict[str, Any]],
    k: int = 10
) -> Dict[str, float]:
    """Evaluate the retrieval system on the internal dataset.

    Args:
        image_embeddings: Image embeddings matrix.
        image_ids: Image IDs array.
        knowledge_embeddings: Knowledge embeddings matrix.
        knowledge_ids: Knowledge IDs array.
        knowledge_objects: List of knowledge objects.
        k: Number of top candidates to consider for evaluation.

    Returns:
        Dictionary with top-1, top-3, top-5 accuracies.
    """
    top1_correct = 0
    top3_correct = 0
    top5_correct = 0
    total_queries = len(image_ids)

    logger.info(f"Starting evaluation on {total_queries} images...")

    for idx, query_id in enumerate(image_ids):
        # Get the image path for this scenario ID
        image_path = Path(__file__).parent.parent / "dataset" / "images" / f"{query_id}.jpg"
        if not image_path.exists():
            logger.warning(f"Image not found for {query_id}: {image_path}")
            continue

        # Retrieve top-k candidates for this query image
        results = retrieve_top_k(
            image_path,
            image_embeddings,
            image_ids,
            knowledge_embeddings,
            knowledge_ids,
            knowledge_objects,
            k=k
        )

        if not results:
            continue

        # Extract the scenario IDs from the results
        retrieved_ids = [r["scenario_id"] for r in results]

        # Check if the correct scenario (query_id) is in the top-1, top-3, top-5
        if query_id == retrieved_ids[0]:
            top1_correct += 1
        if query_id in retrieved_ids[:3]:
            top3_correct += 1
        if query_id in retrieved_ids[:5]:
            top5_correct += 1

        # Progress logging
        if (idx + 1) % 50 == 0:
            logger.info(f"Processed {idx + 1}/{total_queries} queries...")

    top1_acc = top1_correct / total_queries if total_queries > 0 else 0.0
    top3_acc = top3_correct / total_queries if total_queries > 0 else 0.0
    top5_acc = top5_correct / total_queries if total_queries > 0 else 0.0

    return {
        "top1": top1_acc,
        "top3": top3_acc,
        "top5": top5_acc
    }

def main():
    """Main function to run the multimodal retrieval engine."""
    logger.info("=" * 60)
    logger.info("THIRUKKURAL SCENARIO-BASED DECISION-MAKING")
    logger.info("MULTIMODAL RETRIEVAL ENGINE (BASELINE) - PHASE 2.7")
    logger.info("=" * 60)

    start_time = time.time()

    # Load embeddings and knowledge objects
    try:
        image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
        knowledge_objects_path = Path(__file__).parent.parent / "dataset" / "knowledge_objects.json"
        knowledge_objects = load_knowledge_objects(knowledge_objects_path)
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return

    logger.info(f"Loaded {len(image_ids)} image embeddings and {len(knowledge_objects)} knowledge objects.")

    # Run evaluation on the internal dataset
    logger.info("--- Starting Retrieval Evaluation ---")
    accuracies = evaluate_retrieval(
        image_embeddings,
        image_ids,
        knowledge_embeddings,
        knowledge_ids,
        knowledge_objects,
        k=RETRIEVAL_TOP_K
    )

    logger.info("--- Evaluation Results ---")
    logger.info(f"Top-1 Accuracy: {accuracies['top1']:.2%}")
    logger.info(f"Top-3 Accuracy: {accuracies['top3']:.2%}")
    logger.info(f"Top-5 Accuracy: {accuracies['top5']:.2%}")

    # Example retrieval with the first image in the dataset
    logger.info("--- Example Retrieval ---")
    if len(image_ids) > 0:
        example_image_id = image_ids[0]
        example_image_path = Path(__file__).parent.parent / "dataset" / "images" / f"{example_image_id}.jpg"
        if example_image_path.exists():
            logger.info(f"Running example retrieval for image: {example_image_path}")
            results = retrieve_top_k(
                example_image_path,
                image_embeddings,
                image_ids,
                knowledge_embeddings,
                knowledge_ids,
                knowledge_objects,
                k=RETRIEVAL_TOP_K
            )
            if results:
                logger.info(f"Top-5 results for {example_image_id}:")
                for i, result in enumerate(results[:5]):
                    ko = result.get("knowledge_object")
                    ko_str = ko.get("scenario") if ko else "N/A"
                    logger.info(
                        f"  Rank {i+1}: {result['scenario_id']} | "
                        f"Image Sim: {result['image_similarity']:.4f} | "
                        f"Knowledge Sim: {result['knowledge_similarity']:.4f} | "
                        f"Combined: {result['combined_score']:.4f} | "
                        f"Scenario: {ko_str[:50]}..."
                    )
            else:
                logger.warning("No results returned for example image.")
        else:
            logger.warning(f"Example image not found: {example_image_path}")
    else:
        logger.warning("No images in dataset for example retrieval.")

    elapsed_time = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()