"""
Metrics computation for retrieval evaluation.
"""

import numpy as np
from typing import List, Dict, Any

def calculate_accuracy_at_k(retrieved_ids: List[str], correct_id: str, k: int) -> float:
    """
    Calculate accuracy at k (whether the correct ID is in the top-k retrieved results).

    Args:
        retrieved_ids: List of retrieved scenario IDs in order.
        correct_id: The correct scenario ID for the query.
        k: The number of top results to consider.

    Returns:
        1.0 if correct_id is in top-k, else 0.0.
    """
    if correct_id in retrieved_ids[:k]:
        return 1.0
    return 0.0

def calculate_reciprocal_rank(retrieved_ids: List[str], correct_id: str) -> float:
    """
    Calculate reciprocal rank for a single query.

    Args:
        retrieved_ids: List of retrieved scenario IDs in order.
        correct_id: The correct scenario ID for the query.

    Returns:
        1 / rank if correct_id is in retrieved_ids, else 0.0.
    """
    try:
        rank = retrieved_ids.index(correct_id) + 1
        return 1.0 / rank
    except ValueError:
        return 0.0

def calculate_metrics_for_query(retrieved_ids: List[str], correct_id: str, ks: List[int] = [1, 3, 5]) -> Dict[str, float]:
    """
    Calculate accuracy@k and reciprocal rank for a single query.

    Args:
        retrieved_ids: List of retrieved scenario IDs in order.
        correct_id: The correct scenario ID for the query.
        ks: List of k values for which to calculate accuracy.

    Returns:
        Dictionary containing accuracy@k for each k and MRR.
    """
    metrics = {}
    for k in ks:
        metrics[f'accuracy@{k}'] = calculate_accuracy_at_k(retrieved_ids, correct_id, k)
    metrics['mrr'] = calculate_reciprocal_rank(retrieved_ids, correct_id)
    return metrics

def calculate_average_metrics(all_metrics: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Calculate average metrics across multiple queries.

    Args:
        all_metrics: List of metric dictionaries for each query.

    Returns:
        Dictionary containing average accuracy@k and MRR.
    """
    if not all_metrics:
        return {}

    # Get all keys from the first metric dict
    keys = all_metrics[0].keys()
    avg_metrics = {}
    for key in keys:
        avg_metrics[key] = np.mean([m[key] for m in all_metrics])

    return avg_metrics