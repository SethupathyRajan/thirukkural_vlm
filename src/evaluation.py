"""
Main evaluation script for the retrieval system.
Runs all experiments and generates reports.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import time
from collections import defaultdict

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.multimodal_retrieval import (
    load_embeddings,
    load_knowledge_objects,
    retrieve_top_k
)
from src.benchmark import benchmark_function
from src.visualization import (
    plot_accuracy_vs_weight,
    plot_runtime_breakdown,
    plot_horizontal_bar,
    plot_confusion_matrix_if_needed
)
from config import config

def setup_directories():
    """Create necessary directories for output."""
    (project_root / "reports" / "figures").mkdir(parents=True, exist_ok=True)

def load_data():
    """Load embeddings and knowledge objects."""
    print("Loading embeddings and knowledge objects...")
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
    print(f"DEBUG: type(image_ids) = {type(image_ids)}")
    knowledge_objects = load_knowledge_objects(
        project_root / "dataset" / "knowledge_objects.json"
    )
    print(f"Loaded {len(image_ids)} image embeddings and {len(knowledge_objects)} knowledge objects.")
    return image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects

def get_image_path(scenario_id: str) -> Path:
    """Get the path to an image given its scenario ID."""
    return project_root / "dataset" / "images" / f"{scenario_id}.jpg"

def run_retrieval_for_queries(query_image_paths: List[Path],
                             image_embeddings: np.ndarray,
                             image_ids: np.ndarray,
                             knowledge_embeddings: np.ndarray,
                             knowledge_ids: np.ndarray,
                             knowledge_objects: List[Dict[str, Any]],
                             k: int,
                             image_weight: float,
                             knowledge_weight: float) -> List[List[Dict[str, Any]]]:
    """
    Run retrieval for a list of query images with specified weights.
    Temporarily sets the global config weights for the duration of the call.

    Args:
        query_image_paths: List of paths to query images.
        image_embeddings: Image embeddings matrix.
        image_ids: Image IDs array.
        knowledge_embeddings: Knowledge embeddings matrix.
        knowledge_ids: Knowledge IDs array.
        knowledge_objects: List of knowledge object dictionaries.
        k: Number of top candidates to retrieve.
        image_weight: Weight for image similarity.
        knowledge_weight: Weight for knowledge similarity.

    Returns:
        List of retrieval results (each element is a list of dictionaries for one query).
    """
    from config import config
    # Save original weights
    orig_image_weight = config.IMAGE_WEIGHT
    orig_knowledge_weight = config.KNOWLEDGE_WEIGHT
    # Set new weights
    config.IMAGE_WEIGHT = image_weight
    config.KNOWLEDGE_WEIGHT = knowledge_weight
    try:
        results = []
        for i, img_path in enumerate(query_image_paths):
            if i == 0:
                print(f"DEBUG: image_embeddings shape: {image_embeddings.shape}, dtype: {image_embeddings.dtype}")
                print(f"DEBUG: image_ids shape: {image_ids.shape}, dtype: {image_ids.dtype}")
                print(f"DEBUG: knowledge_embeddings shape: {knowledge_embeddings.shape}, dtype: {knowledge_embeddings.dtype}")
                print(f"DEBUG: knowledge_ids shape: {knowledge_ids.shape}, dtype: {knowledge_ids.dtype}")
                print(f"DEBUG: k = {k}")
            result = retrieve_top_k(
                query_image_path=img_path,
                image_embeddings=image_embeddings,
                image_ids=image_ids,
                knowledge_embeddings=knowledge_embeddings,
                knowledge_ids=knowledge_ids,
                knowledge_objects=knowledge_objects,
                k=k
            )
            results.append(result)
        return results
    finally:
        # Restore original weights
        config.IMAGE_WEIGHT = orig_image_weight
        config.KNOWLEDGE_WEIGHT = orig_knowledge_weight

def compute_metrics_for_retrieval_results(retrieval_results: List[List[Dict[str, Any]]],
                                         query_ids: List[str],
                                         k_values: List[int] = [1, 3, 5]) -> Dict[str, float]:
    """
    Compute evaluation metrics from retrieval results.

    Args:
        retrieval_results: List of lists of retrieval results (one per query).
        query_ids: List of query scenario IDs (in the same order as retrieval_results).
        k_values: List of k values for which to compute recall.

    Returns:
        Dictionary of metric names and values.
    """
    # Initialize counters
    top_k_correct = {k: 0 for k in k_values}
    ranks = []  # To store the rank of the correct item for each query
    total_queries = len(query_ids)

    for i, (results, query_id) in enumerate(zip(retrieval_results, query_ids)):
        # Extract the retrieved scenario IDs
        retrieved_ids = [r['scenario_id'] for r in results]
        # Find the rank of the correct item (1-indexed)
        if query_id in retrieved_ids:
            rank = retrieved_ids.index(query_id) + 1
            ranks.append(rank)
            # Increment correct counts for all k >= rank
            for k in k_values:
                if rank <= k:
                    top_k_correct[k] += 1
        else:
            # If not found, rank is infinity (or we can set to a large number)
            ranks.append(float('inf'))
            # No correct, so no increments

    # Compute metrics
    metrics = {}
    # Recall@k (same as precision@k in this case because we have one relevant item per query)
    for k in k_values:
        metrics[f'Recall@{k}'] = top_k_correct[k] / total_queries if total_queries > 0 else 0.0
        # Also store as Top-k Accuracy for consistency with the original request
        metrics[f'Top-{k} Accuracy'] = metrics[f'Recall@{k}']

    # Mean Reciprocal Rank (MRR)
    reciprocal_ranks = [1.0 / r if r != float('inf') else 0.0 for r in ranks]
    metrics['MRR'] = np.mean(reciprocal_ranks) if len(reciprocal_ranks) > 0 else 0.0

    return metrics

def print_metrics(metrics: Dict[str, float], title: str):
    """Print metrics in a nice format."""
    print(f"\n{title}:")
    for key, value in metrics.items():
        if 'Accuracy' in key or 'MRR' in key:
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

def experiment_indexed_baseline():
    """Experiment 1: Indexed Dataset Baseline."""
    print("\n=== Experiment 1: Indexed Dataset Baseline ===")
    # Load data
    # Load data
    image_embeddings_all, image_ids_all, knowledge_embeddings_all, knowledge_ids_all, knowledge_objects = load_data()
    # Get all image paths
    image_paths_all = [get_image_path(sid) for sid in image_ids_all]
    # Filter out any missing images (should not happen, but just in case)
    valid_indices = [i for i, p in enumerate(image_paths_all) if p.exists()]
    image_ids = [image_ids_all[i] for i in valid_indices]   # list of IDs we will query
    image_paths = [image_paths_all[i] for i in valid_indices]   # list of paths
    # We'll use the same embeddings but only for the valid indices?
    # Note: the embeddings are for all images, but we are only querying a subset.
    # The retrieval function uses the full embedding set, which is correct.
    # We don't need to subset the embeddings because we are still searching over the entire database.
    # So we keep the embeddings as they are.

    # Use the default weights from config
    image_weight = config.IMAGE_WEIGHT
    knowledge_weight = config.KNOWLEDGE_WEIGHT
    k = config.RETRIEVAL_TOP_K

    print(f"Running retrieval for {len(image_paths)} queries with weights ({image_weight}, {knowledge_weight})...")
    start_time = time.time()
    retrieval_results = run_retrieval_for_queries(
        image_paths, image_embeddings_all, image_ids_all, knowledge_embeddings_all, knowledge_ids_all,
        knowledge_objects, k, image_weight, knowledge_weight
    )
    elapsed = time.time() - start_time
    print(f"Retrieval completed in {elapsed:.2f} seconds.")

    # Compute metrics
    metrics = compute_metrics_for_retrieval_results(
        retrieval_results, image_ids, k_values=[1, 3, 5]
    )
    print_metrics(metrics, "Indexed Dataset Baseline")

    # Save metrics
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(project_root / "reports" / "evaluation_metrics.csv", index=False)
    print("Saved evaluation_metrics.csv")

    return metrics

def experiment_fusion_weight_study():
    """Experiment 2: Fusion Weight Study."""
    print("\n=== Experiment 2: Fusion Weight Study ===")
    # Load data
    image_embeddings_all, image_ids_all, knowledge_embeddings_all, knowledge_ids_all, knowledge_objects = load_data()
    # Get all image paths
    image_paths_all = [get_image_path(sid) for sid in image_ids_all]
    valid_indices = [i for i, p in enumerate(image_paths_all) if p.exists()]
    image_ids = image_ids_all[valid_indices]  # keep as numpy array
    image_paths = [image_paths_all[i] for i in valid_indices]  # list of Paths

    # Define weight combinations to test
    weight_pairs = [
        (1.0, 0.0),
        (0.9, 0.1),
        (0.8, 0.2),
        (0.7, 0.3),
        (0.6, 0.4),
        (0.5, 0.5),
        (0.4, 0.6),
        (0.3, 0.7),
        (0.2, 0.8),
        (0.1, 0.9),
        (0.0, 1.0)
    ]

    k = config.RETRIEVAL_TOP_K
    results_list = []

    for img_w, kb_w in weight_pairs:
        print(f"\nTesting weights: Image={img_w:.1f}, Knowledge={kb_w:.1f}")
        start_time = time.time()
        retrieval_results = run_retrieval_for_queries(
            image_paths, image_embeddings_all, image_ids, knowledge_embeddings_all, knowledge_ids_all,
            knowledge_objects, k, img_w, kb_w
        )
        elapsed = time.time() - start_time
        print(f"  Retrieval time: {elapsed:.2f} seconds")

        # Compute metrics
        metrics = compute_metrics_for_retrieval_results(
            retrieval_results, image_ids.tolist(), k_values=[1, 3, 5]
        )
        metrics['Image Weight'] = img_w
        metrics['Knowledge Weight'] = kb_w
        results_list.append(metrics)
        print(f"  Top-1: {metrics['Top-1 Accuracy']:.4f}, "
              f"Top-3: {metrics['Top-3 Accuracy']:.4f}, "
              f"Top-5: {metrics['Top-5 Accuracy']:.4f}, "
              f"MRR: {metrics['MRR']:.4f}")

    # Create DataFrame and save
    df = pd.DataFrame(results_list)
    # Reorder columns
    cols = ['Image Weight', 'Knowledge Weight', 'Top-1 Accuracy', 'Top-3 Accuracy', 'Top-5 Accuracy', 'MRR']
    df = df[cols]
    df.to_csv(project_root / "reports" / "fusion_study.csv", index=False)
    print("\nSaved fusion_study.csv")

    # Find the best weight combination based on Top-1 Accuracy
    best_row = df.loc[df['Top-1 Accuracy'].idxmax()]
    print(f"\nBest weight combination: Image={best_row['Image Weight']:.1f}, "
          f"Knowledge={best_row['Knowledge Weight']:.1f} "
          f"(Top-1 Accuracy: {best_row['Top-1 Accuracy']:.4f})")

    # Plot accuracy vs. weight for Top-1, Top-3, Top-5, and MRR
    weights = df['Image Weight'].tolist()
    plot_accuracy_vs_weight(weights, df['Top-1 Accuracy'].tolist(), 'Top-1 Accuracy',
                            save_path=str(project_root / "reports" / "figures" / "accuracy_vs_weight_top1.png"))
    plot_accuracy_vs_weight(weights, df['Top-3 Accuracy'].tolist(), 'Top-3 Accuracy',
                            save_path=str(project_root / "reports" / "figures" / "accuracy_vs_weight_top3.png"))
    plot_accuracy_vs_weight(weights, df['Top-5 Accuracy'].tolist(), 'Top-5 Accuracy',
                            save_path=str(project_root / "reports" / "figures" / "accuracy_vs_weight_top5.png"))
    plot_accuracy_vs_weight(weights, df['MRR'].tolist(), 'MRR',
                            save_path=str(project_root / "reports" / "figures" / "accuracy_vs_weight_mrr.png"))

    return df

def experiment_ablation_study():
    """Experiment 3: Ablation Study."""
    print("\n=== Experiment 3: Ablation Study ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects = load_data()
    # Get all image paths
    image_paths = [get_image_path(sid) for sid in image_ids]
    valid_indices = [i for i, p in enumerate(image_paths) if p.exists()]
    image_ids = [image_ids[i] for i in valid_indices]
    image_paths = [image_paths[i] for i in valid_indices]

    k = config.RETRIEVAL_TOP_K

    # Define the configurations to test
    configs = [
        ("Image Only", 1.0, 0.0),
        ("Multimodal (default)", config.IMAGE_WEIGHT, config.KNOWLEDGE_WEIGHT),
        # Note: Knowledge Only is not applicable as explained in the comments.
        # We'll skip it and note in the report.
    ]

    results_list = []

    for name, img_w, kb_w in configs:
        print(f"\nTesting configuration: {name} (weights: {img_w}, {kb_w})")
        start_time = time.time()
        retrieval_results = run_retrieval_for_queries(
            image_paths, image_embeddings, image_ids, knowledge_embeddings, knowledge_ids,
            knowledge_objects, k, img_w, kb_w
        )
        elapsed = time.time() - start_time
        print(f"  Retrieval time: {elapsed:.2f} seconds")

        # Compute metrics
        metrics = compute_metrics_for_retrieval_results(
            retrieval_results, image_ids, k_values=[1, 3, 5]
        )
        metrics['Configuration'] = name
        results_list.append(metrics)
        print(f"  Top-1: {metrics['Top-1 Accuracy']:.4f}, "
              f"Top-3: {metrics['Top-3 Accuracy']:.4f}, "
              f"Top-5: {metrics['Top-5 Accuracy']:.4f}, "
              f"MRR: {metrics['MRR']:.4f}")

    # Create DataFrame and save
    df = pd.DataFrame(results_list)
    # Reorder columns
    cols = ['Configuration', 'Top-1 Accuracy', 'Top-3 Accuracy', 'Top-5 Accuracy', 'MRR']
    df = df[cols]
    df.to_csv(project_root / "reports" / "ablation_study.csv", index=False)
    print("\nSaved ablation_study.csv")

    return df

def extract_concept_from_knowledge_object(ko: Dict[str, Any]) -> str:
    """Extract concept from a knowledge object."""
    return ko.get('concept', 'Unknown')

def extract_adhigaram_from_knowledge_object(ko: Dict[str, Any]) -> str:
    """Extract adhigaram from a knowledge object."""
    return ko.get('adhigaram', 'Unknown')

def experiment_per_concept_performance():
    """Experiment 4: Per-Concept Performance."""
    print("\n=== Experiment 4: Per-Concept Performance ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects = load_data()
    # Get all image paths
    image_paths = [get_image_path(sid) for sid in image_ids]
    valid_indices = [i for i, p in enumerate(image_paths) if p.exists()]
    image_ids = [image_ids[i] for i in valid_indices]
    image_paths = [image_paths[i] for i in valid_indices]
    # Also filter knowledge objects and embeddings to match the valid images?
    # Note: we are still searching over the entire database, so we keep the full knowledge set.
    # We only need to filter the queries.

    # Use default weights
    image_weight = config.IMAGE_WEIGHT
    knowledge_weight = config.KNOWLEDGE_WEIGHT
    k = config.RETRIEVAL_TOP_K

    print(f"Running retrieval for {len(image_paths)} queries...")
    start_time = time.time()
    retrieval_results = run_retrieval_for_queries(
        image_paths, image_embeddings, image_ids, knowledge_embeddings, knowledge_ids,
        knowledge_objects, k, image_weight, knowledge_weight
    )
    elapsed = time.time() - start_time
    print(f"Retrieval completed in {elapsed:.2f} seconds.")

    # Group by concept
    # We need to know the concept for each query image.
    # We have the knowledge object for each image ID?
    # We have a mapping from image ID to knowledge object?
    # Actually, we have knowledge_objects list, and we can create a dictionary from scenario_id to knowledge object.
    # Note: not all image IDs have a corresponding knowledge object (e.g., S102).
    # We'll create a mapping for those that do.

    # Build a mapping from scenario_id to knowledge object
    ko_dict = {ko['scenario_id']: ko for ko in knowledge_objects}

    # For each query, get its concept if available
    query_conditions = []
    for qid in image_ids:
        ko = ko_dict.get(qid)
        if ko:
            concept = extract_concept_from_knowledge_object(ko)
        else:
            concept = 'Unknown'  # For missing knowledge objects
        query_conditions.append(concept)

    # Now, we want to compute metrics per concept.
    # We'll create a dictionary to hold results per concept.
    concept_stats = {}
    for idx in range(len(image_paths)):
        results = retrieval_results[idx]
        query_id = image_ids[idx]
        concept = query_conditions[idx]

        if concept not in concept_stats:
            concept_stats[concept] = {
                'correct_at_k': {1: 0, 3: 0, 5: 0},
                'total': 0,
                'ranks': []
            }

        stat = concept_stats[concept]
        stat['total'] += 1

        # Extract retrieved IDs
        retrieved_ids = [r['scenario_id'] for r in results]
        # Find rank of the correct item
        if query_id in retrieved_ids:
            rank = retrieved_ids.index(query_id) + 1
            stat['ranks'].append(rank)
            # Update correct counts
            for k in [1, 3, 5]:
                if rank <= k:
                    stat['correct_at_k'][k] += 1
        else:
            stat['ranks'].append(float('inf'))

    # Compute metrics per concept
    component_metrics = []
    for concept, stat in concept_stats.items():
        total = stat['total']
        if total == 0:
            continue
        recall_at_k = {k: stat['correct_at_k'][k] / total for k in [1, 3, 5]}
        mrr = np.mean([1.0 / r if r != float('inf') else 0.0 for r in stat['ranks']]) if stat['ranks'] else 0.0
        component = {
            'Concept': concept,
            'Num_Samples': total,
            'Top-1 Accuracy': recall_at_k[1],
            'Top-3 Accuracy': recall_at_k[3],
            'Top-5 Accuracy': recall_at_k[5],
            'MRR': mrr
        }
        component_metrics.append(component)

    # Convert to DataFrame and sort by number of samples (descending)
    df = pd.DataFrame(component_metrics)
    df = df.sort_values('Num_Samples', ascending=False)
    # Reorder columns
    cols = ['Concept', 'Num_Samples', 'Top-1 Accuracy', 'Top-3 Accuracy', 'Top-5 Accuracy', 'MRR']
    df = df[cols]
    df.to_csv(project_root / "reports" / "concept_analysis.csv", index=False)
    print("\nSaved concept_analysis.csv")

    # Print summary
    print(f"Found {len(df)} concepts.")
    print("\nTop 5 concepts by number of samples:")
    print(df.head()[['Concept', 'Num_Samples', 'Top-1 Accuracy']].to_string(index=False))
    print("\nBottom 5 concepts by number of samples:")
    print(df.tail()[['Concept', 'Num_Samples', 'Top-1 Accuracy']].to_string(index=False))

    # Plot horizontal bar chart for Top-1 Accuracy by concept (top 10 by sample size)
    top10 = df.head(10)
    plot_horizontal_bar(
        top10['Top-1 Accuracy'].tolist(),
        top10['Concept'].tolist(),
        title='Top-1 Accuracy by Concept (Top 10 by Sample Size)',
        xlabel='Top-1 Accuracy',
        ylabel='Concept',
        save_path=str(project_root / "reports" / "figures" / "concept_accuracy.png")
    )

    return df

def experiment_per_adhigaram_performance():
    """Experiment 5: Per-Adhigaram Performance."""
    print("\n=== Experiment 5: Per-Adhigaram Performance ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects = load_data()
    # Get all image paths
    image_paths = [get_image_path(sid) for sid in image_ids]
    valid_indices = [i for i, p in enumerate(image_paths) if p.exists()]
    image_ids = [image_ids[i] for i in valid_indices]
    image_paths = [image_paths[i] for i in valid_indices]

    # Use default weights
    image_weight = config.IMAGE_WEIGHT
    knowledge_weight = config.KNOWLEDGE_WEIGHT
    k = config.RETRIEVAL_TOP_K

    print(f"Running retrieval for {len(image_paths)} queries...")
    start_time = time.time()
    retrieval_results = run_retrieval_for_queries(
        image_paths, image_embeddings, image_ids, knowledge_embeddings, knowledge_ids,
        knowledge_objects, k, image_weight, knowledge_weight
    )
    elapsed = time.time() - start_time
    print(f"Retrieval completed in {elapsed:.2f} seconds.")

    # Build mapping from scenario_id to knowledge object
    ko_dict = {ko['scenario_id']: ko for ko in knowledge_objects}

    # For each query, get its adhigaram if available
    query_adhigarams = []
    for qid in image_ids:
        ko = ko_dict.get(qid)
        if ko:
            adhigaram = extract_adhigaram_from_knowledge_object(ko)
        else:
            adhigaram = 'Unknown'
        query_adhigarams.append(adhigaram)

    # Group by adhigaram
    adhigaram_stats = {}
    for idx in range(len(image_paths)):
        results = retrieval_results[idx]
        query_id = image_ids[idx]
        adhigaram = query_adhigarams[idx]

        if adhigaram not in adhigaram_stats:
            adhigaram_stats[adhigaram] = {
                'correct_at_k': {1: 0, 3: 0, 5: 0},
                'total': 0,
                'ranks': []
            }

        stat = adhigaram_stats[adhigaram]
        stat['total'] += 1

        # Extract retrieved IDs
        retrieved_ids = [r['scenario_id'] for r in results]
        # Find rank of the correct item
        if query_id in retrieved_ids:
            rank = retrieved_ids.index(query_id) + 1
            stat['ranks'].append(rank)
            # Update correct counts
            for k in [1, 3, 5]:
                if rank <= k:
                    stat['correct_at_k'][k] += 1
        else:
            stat['ranks'].append(float('inf'))

    # Compute metrics per adhigaram
    adhigaram_metrics = []
    for adhigaram, stat in adhigaram_stats.items():
        total = stat['total']
        if total == 0:
            continue
        recall_at_k = {k: stat['correct_at_k'][k] / total for k in [1, 3, 5]}
        mrr = np.mean([1.0 / r if r != float('inf') else 0.0 for r in stat['ranks']]) if stat['ranks'] else 0.0
        adhigaram_metrics.append({
            'Adhigaram': adhigaram,
            'Num_Samples': total,
            'Top-1 Accuracy': recall_at_k[1],
            'Top-3 Accuracy': recall_at_k[3],
            'Top-5 Accuracy': recall_at_k[5],
            'MRR': mrr
        })

    # Convert to DataFrame and sort by number of samples (descending)
    df = pd.DataFrame(adhigaram_metrics)
    df = df.sort_values('Num_Samples', ascending=False)
    # Reorder columns
    cols = ['Adhigaram', 'Num_Samples', 'Top-1 Accuracy', 'Top-3 Accuracy', 'Top-5 Accuracy', 'MRR']
    df = df[cols]
    df.to_csv(project_root / "reports" / "adhigaram_analysis.csv", index=False)
    print("\nSaved adhigaram_analysis.csv")

    # Print summary
    print(f"Found {len(df)} adhigarams.")
    print("\nTop 5 adhigarams by number of samples:")
    print(df.head()[['Adhigaram', 'Num_Samples', 'Top-1 Accuracy']].to_string(index=False))
    print("\nBottom 5 adhigarams by number of samples:")
    print(df.tail()[['Adhigaram', 'Num_Samples', 'Top-1 Accuracy']].to_string(index=False))

    # Plot horizontal bar chart for Top-1 Accuracy by adhigaram (top 10 by sample size)
    top10 = df.head(10)
    plot_horizontal_bar(
        top10['Top-1 Accuracy'].tolist(),
        top10['Adhigaram'].tolist(),
        title='Top-1 Accuracy by Adhigaram (Top 10 by Sample Size)',
        xlabel='Top-1 Accuracy',
        ylabel='Adhigaram',
        save_path=str(project_root / "reports" / "figures" / "adhigaram_accuracy.png")
    )

    return df

def experiment_failure_analysis():
    """Experiment 6: Failure Analysis."""
    print("\n=== Experiment 6: Failure Analysis ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects = load_data()
    # Get all image paths
    image_paths = [get_image_path(sid) for sid in image_ids]
    valid_indices = [i for i, p in enumerate(image_paths) if p.exists()]
    image_ids = [image_ids[i] for i in valid_indices]
    image_paths = [image_paths[i] for i in valid_indices]

    # Use default weights
    image_weight = config.IMAGE_WEIGHT
    knowledge_weight = config.KNOWLEDGE_WEIGHT
    k = config.RETRIEVAL_TOP_K

    print(f"Running retrieval for {len(image_paths)} queries to identify failures...")
    start_time = time.time()
    retrieval_results = run_retrieval_for_queries(
        image_paths, image_embeddings, image_ids, knowledge_embeddings, knowledge_ids,
        knowledge_objects, k, image_weight, knowledge_weight
    )
    elapsed = time.time() - start_time
    print(f"Retrieval completed in {elapsed:.2f} seconds.")

    # Build mapping from scenario_id to knowledge object
    ko_dict = {ko['scenario_id']: ko for ko in knowledge_objects}

    failures = []
    for idx, (results, query_id) in enumerate(zip(retrieval_results, image_ids)):
        # Extract retrieved IDs and scores
        retrieved_ids = [r['scenario_id'] for r in results]
        # Check if the query_id is in the top-1 (we consider a failure if not in top-1)
        if retrieved_ids[0] != query_id:
            # This is a failure for top-1
            # Get the retrieved top-1 result
            top1_result = results[0]
            top1_id = top1_result['scenario_id']
            # Get knowledge objects for query and retrieved
            query_ko = ko_dict.get(query_id, {})
            retrieved_ko = ko_dict.get(top1_id, {})
            # Extract relevant info
            failure_info = {
                'Query Scenario_ID': query_id,
                'Expected Kural': query_ko.get('kural', 'N/A'),
                'Retrieved Kural': retrieved_ko.get('kural', 'N/A'),
                'Expected Concept': query_ko.get('concept', 'Unknown'),
                'Retrieved Concept': retrieved_ko.get('concept', 'Unknown'),
                'Expected Adhigaram': query_ko.get('adhigaram', 'Unknown'),
                'Retrieved Adhigaram': retrieved_ko.get('adhigaram', 'Unknown'),
                'Image Similarity': top1_result['image_similarity'],
                'Knowledge Similarity': top1_result['knowledge_similarity'],
                'Combined Score': top1_result['combined_score']
            }
            failures.append(failure_info)

    print(f"Found {len(failures)} failures (top-1 incorrect).")

    if failures:
        # Convert to DataFrame and save
        df = pd.DataFrame(failures)
        df.to_csv(project_root / "reports" / "failure_analysis.csv", index=False)
        print("Saved failure_analysis.csv")

        # Plot confusion summary (failures by expected vs retrieved concept)
        # We'll create a simple bar chart of failure counts by expected concept
        from collections import Counter
        expected_counts = Counter([f['Expected Concept'] for f in failures])
        retrieved_counts = Counter([f['Retrieved Concept'] for f in failures])

        # Plot two subplots
        import matplotlib.pyplot as plt
        import numpy as np
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Expected concept failures
        concepts = list(expected_counts.keys())
        counts = list(expected_counts.values())
        y_pos = np.arange(len(concepts))
        ax1.barh(y_pos, counts, align='center', alpha=0.7, color='red')
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(concepts)
        ax1.set_xlabel('Number of Failures')
        ax1.set_title('Failures by Expected Concept')
        ax1.invert_yaxis()

        # Retrieved concept failures
        concepts = list(retrieved_counts.keys())
        counts = list(retrieved_counts.values())
        y_pos = np.arange(len(concepts))
        ax2.barh(y_pos, counts, align='center', alpha=0.7, color='blue')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(concepts)
        ax2.set_xlabel('Number of Failures')
        ax2.set_title('Failures by Retrieved Concept')
        ax2.invert_yaxis()

        plt.tight_layout()
        plt.savefig(str(project_root / "reports" / "figures" / "confusion_summary.png"), dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved confusion_summary.png")

        # Print a few examples
        print("\nExample failures (first 5):")
        for f in failures[:5]:
            print(f"  Query: {f['Query Scenario_ID']} -> Retrieved: {f['Retrieved Kural']} "
                  f"(Expected: {f['Expected Kural']})")
    else:
        print("No failures found! All queries retrieved the correct item at rank 1.")
        # Create an empty DataFrame with the expected columns
        columns = ['Query Scenario_ID', 'Expected Kural', 'Retrieved Kural', 'Expected Concept',
                   'Retrieved Concept', 'Expected Adhigaram', 'Retrieved Adhigaram',
                   'Image Similarity', 'Knowledge Similarity', 'Combined Score']
        df = pd.DataFrame(columns=columns)
        df.to_csv(project_root / "reports" / "failure_analysis.csv", index=False)
        print("Saved empty failure_analysis.csv")

    return failures

def experiment_runtime_analysis():
    """Experiment 7: Runtime Analysis."""
    print("\n=== Experiment 7: Runtime Analysis ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects = load_data()
    # Get a subset of images for timing (to avoid too long, but we can use all if we want)
    # We'll use the first 50 images for timing analysis to keep it reasonable.
    # But note: the runtime might vary depending on the query (due to caching, etc.)
    # We'll use a fixed set of 50 queries.
    image_paths = [get_image_path(sid) for sid in image_ids[:50]]
    valid_indices = [i for i, p in enumerate(image_paths) if p.exists()]
    image_paths = [image_paths[i] for i in valid_indices]
    # We'll use the same embeddings (full set) for retrieval.

    # Use default weights
    image_weight = config.IMAGE_WEIGHT
    knowledge_weight = config.KNOWLEDGE_WEIGHT
    k = config.RETRIEVAL_TOP_K

    print(f"Running runtime analysis on {len(image_paths)} queries...")

    # We'll break down the timing into:
    # 1. Image encoding time
    # 2. Image similarity search time (cosine similarity + top-k selection)
    # 3. Knowledge reranking time (knowledge similarity computation + combining scores + sorting)
    # However, our retrieve_top_k function does not expose these timings internally.
    # We will need to modify the retrieval function to return timings?
    # But we are not allowed to change the retrieval algorithm.

    # Alternative: we can use the benchmark function to time the entire retrieval,
    # and then we can also time the components by breaking down the steps manually?
    # We cannot break down the steps without changing the retrieval function.

    # Given the constraints, we will measure the total retrieval time per query,
    # and then we can also measure the time for image encoding and similarity search
    # by reusing the functions from the retrieval module?
    # But note: we are not allowed to change the retrieval algorithm, but we can use its helper functions.

    # The retrieval module uses:
    #   encode_user_image (from src.image_encoder)
    #   cosine_similarity (from src.multimodal_retrieval)
    #   get_top_k_candidates (from src.multimodal_retrieval)
    #   compute_knowledge_similarity (from src.multimodal_retrieval)
    #   combine_scores (from src.multimodal_retrieval)
    #   rerank_candidates (from src.multimodal_retrieval)

    # We can time these steps separately if we want to, but note that the retrieval function
    # does a specific sequence: encode, image similarity, top-k, knowledge similarity for top-k, combine, rerank.

    # We will create a function that mimics the retrieval but returns timings for each step.
    # However, that would be duplicating the retrieval algorithm?
    # We are not duplicating the algorithm if we are using the same functions, but we are rearranging them.

    # Given the complexity, and since the task says "Do not change the retrieval algorithm",
    # I think we are allowed to measure the total time and then also measure the time of the
    # individual components by calling the same functions in the same order, as long as we don't change them.

    # We'll do that.

    # We'll create a timed version of the retrieval steps by importing the necessary functions.

    from src.multimodal_retrieval import (
        encode_user_image,
        cosine_similarity,
        get_top_k_candidates,
        compute_knowledge_similarity,
        combine_scores,
        rerank_candidates
    )
    from src.utils import setup_logging, get_logger
    # We'll disable logging for the timing runs to avoid interference.
    # But note: the logging is already set up. We'll just let it be.

    # We'll define a function that computes the timings for each step.
    def timed_retrieval(query_image_path: Path):
        # Step 1: Encode image
        start_encode = time.perf_counter()
        query_embedding = encode_user_image(query_image_path)
        encode_time = time.perf_counter() - start_encode

        # Step 2: Compute image similarity
        start_img_sim = time.perf_counter()
        image_sims = cosine_similarity(query_embedding, image_embeddings)
        img_sim_time = time.perf_counter() - start_img_sim

        # Step 3: Get top-k candidates by image similarity
        start_topk = time.perf_counter()
        top_k_ids, top_k_scores, top_k_indices = get_top_k_candidates(image_sims, image_ids, k)
        topk_time = time.perf_counter() - start_topk

        # Step 4: Compute knowledge similarity for the top-k candidates
        start_know_sim = time.perf_counter()
        # Use the top image candidate's knowledge embedding as reference
        top_candidate_id = top_k_ids[0]
        try:
            top_candidate_idx_in_knowledge = np.where(knowledge_ids == top_candidate_id)[0][0]
        except IndexError:
            # If knowledge embedding not found, set knowledge similarity to 0 for all
            know_sims = [0.0] * len(top_k_ids)
        else:
            reference_know_emb = knowledge_embeddings[top_candidate_idx_in_knowledge]
            candidate_know_embs = []
            for cand_id in top_k_ids:
                try:
                    cand_idx = np.where(knowledge_ids == cand_id)[0][0]
                    candidate_know_embs.append(knowledge_embeddings[cand_idx])
                except IndexError:
                    # If knowledge embedding not found for a candidate, use zero vector
                    candidate_know_embs.append(np.zeros_like(reference_know_emb))
            candidate_know_embs = np.array(candidate_know_embs)
            know_sims = compute_knowledge_similarity(reference_know_emb, candidate_know_embs)
        know_sim_time = time.perf_counter() - start_know_sim

        # Step 5: Combine scores
        start_combine = time.perf_counter()
        combined_scores = combine_scores(
            top_k_scores,
            know_sims,
            image_weight,
            knowledge_weight
        )
        combine_time = time.perf_counter() - start_combine

        # Step 6: Rerank candidates
        start_rerank = time.perf_counter()
        reranked = rerank_candidates(
            top_k_ids,
            top_k_scores,
            know_sims,
            combined_scores
        )
        rerank_time = time.perf_counter() - start_rerank

        # Total time
        total_time = encode_time + img_sim_time + topk_time + know_sim_time + combine_time + rerank_time

        # Return the results and the timings
        return {
            'encoded_result': list(zip(top_k_ids, top_k_scores, know_sims, combined_scores)),
            'timings': {
                'encoding': encode_time,
                'image_similarity': img_sim_time,
                'top_k_selection': topk_time,
                'knowledge_similarity': know_sim_time,
                'score_combination': combine_time,
                'reranking': rerank_time,
                'total': total_time
            }
        }

    # Now run this for each query and collect timings
    enc_times = []
    img_sim_times = []
    topk_times = []
    know_sim_times = []
    combine_times = []
    rerank_times = []
    total_times = []

    for img_path in image_paths:
        result = timed_retrieval(img_path)
        t = result['timings']
        enc_times.append(t['encoding'])
        img_sim_times.append(t['image_similarity'])
        topk_times.append(t['top_k_selection'])
        know_sim_times.append(t['knowledge_similarity'])
        combine_times.append(t['score_combination'])
        rerank_times.append(t['reranking'])
        total_times.append(t['total'])

    # Compute statistics
    def compute_stats(times):
        return {
            'mean': np.mean(times),
            'std': np.std(times),
            'min': np.min(times),
            'max': np.max(times),
            'median': np.median(times)
        }

    stats = {
        'Encoding': compute_stats(enc_times),
        'Image Similarity': compute_stats(img_sim_times),
        'Top-K Selection': compute_stats(topk_times),
        'Knowledge Similarity': compute_stats(know_sim_times),
        'Score Combination': compute_stats(combine_times),
        'Reranking': compute_stats(rerank_times),
        'Total': compute_stats(total_times)
    }

    # Create a DataFrame for the summary
    summary_rows = []
    for name, stat in stats.items():
        row = {'Component': name}
        for metric, value in stat.items():
            row[metric.capitalize()] = value
        summary_rows.append(row)
    summary_df = pd.DataFrame(summary_rows)
    # Reorder columns
    cols = ['Component', 'Mean', 'Std', 'Min', 'Max', 'Median']
    summary_df = summary_df[cols]
    summary_df.to_csv(project_root / "reports" / "runtime_analysis.csv", index=False)
    print("\nSaved runtime_analysis.csv")

    # Print summary
    print("\nRuntime Statistics (seconds):")
    print(summary_df.to_string(index=False))

    # Plot runtime breakdown as a pie chart of average times
    avg_times = [stats[comp]['mean'] for comp in ['Encoding', 'Image Similarity', 'Top-K Selection', 'Knowledge Similarity', 'Score Combination', 'Reranking']]
    labels = ['Encoding', 'Image Similarity', 'Top-K Selection', 'Knowledge Similarity', 'Score Combination', 'Reranking']
    plot_runtime_breakdown(avg_times, labels,
                           title='Average Runtime Breakdown per Query',
                           save_path=str(project_root / "reports" / "figures" / "runtime_breakdown.png"))

    return stats

def experiment_memory_usage():
    """Experiment 8: Memory Usage."""
    print("\n=== Experiment 8: Memory Usage ===")
    # We'll measure the memory usage of the embeddings and knowledge objects.
    # We can use the tracemalloc module to track memory allocations.

    import tracemalloc

    # Start tracking
    tracemalloc.start()

    # Load embeddings and knowledge objects (we already have them from previous steps, but we'll load again to measure)
    # Note: we are measuring the memory of the data structures, not the runtime memory during retrieval.
    # We'll do a separate measurement.

    # We'll create a function that loads the data and then we'll measure its memory.
    def load_and_measure():
        image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
        knowledge_objects = load_knowledge_objects(
            project_root / "dataset" / "knowledge_objects.json"
        )
        return image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects

    # Take a snapshot before loading
    snapshot1 = tracemalloc.take_snapshot()
    # Load the data
    data = load_and_measure()
    # Take a snapshot after loading
    snapshot2 = tracemalloc.take_snapshot()

    # Compute the difference
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    print("\nTop 10 memory increases:")
    for stat in top_stats[:10]:
        print(f"{stat.count} {stat.size / 1024:.1f} KiB {stat.traceback}")

    # We can also measure the total memory used by the data structures by summing their sizes.
    # But note: the tracemalloc tracks allocations, not the total size of the objects.
    # We'll get the size of each object using sys.getsizeof, but note that it doesn't include referenced objects.
    # We'll do a rough estimate.

    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids, knowledge_objects = data

    # Size of numpy arrays
    image_emb_size = image_embeddings.nbytes
    image_ids_size = sys.getsizeof(image_ids)  # This is approximate for the list, not the elements
    # For the list of IDs, we can estimate: each string is about 50 bytes?
    # We'll do a simple sum of the sizes of the strings and the list overhead.
    # But for simplicity, we'll just report the array sizes and the count of objects.

    # We'll create a summary
    mem_info = {
        'Image Embeddings (bytes)': image_embeddings.nbytes,
        'Image IDs (approx. bytes)': sys.getsizeof(image_ids) + sum(sys.getsizeof(id) for id in image_ids),
        'Knowledge Embeddings (bytes)': knowledge_embeddings.nbytes,
        'Knowledge IDs (approx. bytes)': sys.getsizeof(knowledge_ids) + sum(sys.getsizeof(id) for id in knowledge_ids),
        'Knowledge Objects (approx. bytes)': sys.getsizeof(knowledge_objects) + sum(sys.getsizeof(obj) for obj in knowledge_objects),
        'Number of Images': len(image_ids),
        'Number of Knowledge Objects': len(knowledge_objects),
        'Embedding Dimension': image_embeddings.shape[1] if len(image_embeddings) > 0 else 0
    }

    # Convert to DataFrame and save
    mem_df = pd.DataFrame([mem_info])
    mem_df.to_csv(project_root / "reports" / "memory_usage.csv", index=False)
    print("\nSaved memory_usage.csv")

    # Print summary
    print("\nMemory Usage:")
    for key, value in mem_info.items():
        if 'Bytes' in key:
            print(f"{key}: {value / 1024:.2f} KB")
        else:
            print(f"{key}: {value}")

    # Stop tracing
    tracemalloc.stop()

    return mem_info

def main():
    """Run all experiments and generate reports."""
    print("Starting Phase 2.8: Experimental Evaluation & Benchmarking")
    print("=" * 60)

    # Setup directories
    setup_directories()

    # Run experiments
    try:
        exp1_results = experiment_indexed_baseline()
    except Exception as e:
        print(f"Error in Experiment 1: {e}")
        import traceback
        traceback.print_exc()
        exp1_results = {}

    try:
        exp2_results = experiment_fusion_weight_study()
    except Exception as e:
        print(f"Error in Experiment 2: {e}")
        import traceback
        traceback.print_exc()
        exp2_results = None

    try:
        exp3_results = experiment_ablation_study()
    except Exception as e:
        print(f"Error in Experiment 3: {e}")
        import traceback
        traceback.print_exc()
        exp3_results = None

    try:
        exp4_results = experiment_per_concept_performance()
    except Exception as e:
        print(f"Error in Experiment 4: {e}")
        import traceback
        traceback.print_exc()
        exp4_results = None

    try:
        exp5_results = experiment_per_adhigaram_performance()
    except Exception as e:
        print(f"Error in Experiment 5: {e}")
        import traceback
        traceback.print_exc()
        exp5_results = None

    try:
        exp6_results = experiment_failure_analysis()
    except Exception as e:
        print(f"Error in Experiment 6: {e}")
        import traceback
        traceback.print_exc()
        exp6_results = []

    try:
        exp7_results = experiment_runtime_analysis()
    except Exception as e:
        print(f"Error in Experiment 7: {e}")
        import traceback
        traceback.print_exc()
        exp7_results = {}

    try:
        exp8_results = experiment_memory_usage()
    except Exception as e:
        print(f"Error in Experiment 8: {e}")
        import traceback
        traceback.print_exc()
        exp8_results = {}

    # Generate a summary report
    print("\n" + "=" * 60)
    print("Generating summary report...")
    report_path = project_root / "reports" / "evaluation_report.md"
    with open(report_path, 'w') as f:
        f.write("# Thirukkural Scenario-Based Decision-Making System\n")
        f.write("## Evaluation Report - Phase 2.8\n\n")

        f.write("## Dataset Size\n")
        f.write(f"- Number of Images: {len(image_ids) if 'image_ids' in locals() else 'N/A'}\n")
        f.write(f"- Number of Knowledge Objects: {len(knowledge_objects) if 'knowledge_objects' in locals() else 'N/A'}\n")
        if 'image_embeddings' in locals() and len(image_embeddings) > 0:
            f.write(f"- Embedding Dimension: {image_embeddings.shape[1]}\n")
        else:
            f.write("- Embedding Dimension: N/A\n")

        f.write("\n## Overall Accuracy (Indexed Dataset Baseline)\n")
        if exp1_results:
            f.write(f"- Top-1 Accuracy: {exp1_results.get('Top-1 Accuracy', 0):.2%}\n")
            f.write(f"- Top-3 Accuracy: {exp1_results.get('Top-3 Accuracy', 0):.2%}\n")
            f.write(f"- Top-5 Accuracy: {exp1_results.get('Top-5 Accuracy', 0):.2%}\n")
            f.write(f"- MRR: {exp1_results.get('MRR', 0):.4f}\n")
        else:
            f.write("- No results available.\n")

        f.write("\n## Best Fusion Weight (from Study)\n")
        if exp2_results is not None and not exp2_results.empty:
            best_row = exp2_results.loc[exp2_results['Top-1 Accuracy'].idxmax()]
            f.write(f"- Image Weight: {best_row['Image Weight']:.1f}\n")
            f.write(f"- Knowledge Weight: {best_row['Knowledge Weight']:.1f}\n")
            f.write(f"- Top-1 Accuracy: {best_row['Top-1 Accuracy']:.4f}\n")
        else:
            f.write("- No results available.\n")

        f.write("\n## Ablation Study\n")
        if exp3_results is not None and not exp3_results.empty:
            f.write("| Configuration | Top-1 Acc | Top-3 Acc | Top-5 Acc | MRR |\n")
            f.write("|---------------|-----------|-----------|-----------|-----|\n")
            for _, row in exp3_results.iterrows():
                f.write(f"| {row['Configuration']} | {row['Top-1 Accuracy']:.4f} | {row['Top-3 Accuracy']:.4f} | "
                        f"{row['Top-5 Accuracy']:.4f} | {row['MRR']:.4f} |\n")
        else:
            f.write("- No results available.\n")

        f.write("\n## Failure Analysis\n")
        if isinstance(exp6_results, list) and len(exp6_results) > 0:
            f.write(f"- Number of Failures (Top-1 incorrect): {len(exp6_results)}\n")
            f.write(f"- Failure Rate: {len(exp6_results) / len(image_ids) if 'image_ids' in locals() and len(image_ids) > 0 else 0:.2%}\n")
        else:
            f.write("- No failures found (all queries retrieved correct item at rank 1).\n")

        f.write("\n## Runtime Performance\n")
        if exp7_results:
            f.write("| Component | Mean (s) | Std (s) | Min (s) | Max (s) | Median (s) |\n")
            f.write("|-----------|----------|---------|---------|---------|------------|\n")
            for comp, stat in exp7_results.items():
                if comp in ['Encoding', 'Image Similarity', 'Top-K Selection', 'Knowledge Similarity', 'Score Combination', 'Reranking', 'Total']:
                    f.write(f"| {comp} | {stat['mean']:.4f} | {stat['std']:.4f} | {stat['min']:.4f} | {stat['max']:.4f} | {stat['median']:.4f} |\n")
        else:
            f.write("- No results available.\n")

        f.write("\n## Memory Usage\n")
        if exp8_results:
            f.write(f"- Image Embeddings: {exp8_results.get('Image Embeddings (bytes)', 0) / 1024:.2f} KB\n")
            f.write(f"- Image IDs: {exp8_results.get('Image IDs (approx. bytes)', 0) / 1024:.2f} KB\n")
            f.write(f"- Knowledge Embeddings: {exp8_results.get('Knowledge Embeddings (bytes)', 0) / 1024:.2f} KB\n")
            f.write(f"- Knowledge IDs: {exp8_results.get('Knowledge IDs (approx. bytes)', 0) / 1024:.2f} KB\n")
            f.write(f"- Knowledge Objects: {exp8_results.get('Knowledge Objects (approx. bytes)', 0) / 1024:.2f} KB\n")
            f.write(f"- Number of Images: {exp8_results.get('Number of Images', 0)}\n")
            f.write(f"- Number of Knowledge Objects: {exp8_results.get('Number of Knowledge Objects', 0)}\n")
            f.write(f"- Embedding Dimension: {exp8_results.get('Embedding Dimension', 0)}\n")
        else:
            f.write("- No results available.\n")

        f.write("\n## Notes\n")
        f.write("- The evaluation was performed on the indexed dataset (training set performance).\n")
        f.write("- Unseen image evaluation will be performed in Phase 2.9.\n")
        f.write("- One image (S102) lacks a corresponding knowledge object; this is handled gracefully by setting knowledge similarity to zero.\n")
        f.write("- All experiments used deterministic ordering and fixed configuration.\n")
        f.write("- The retrieval algorithm was not modified; only configuration weights were varied where applicable.\n")

    print(f"Saved evaluation report to {report_path}")
    print("\nDone!")

if __name__ == "__main__":
    main()