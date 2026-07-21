"""
Visualization utilities for retrieval evaluation.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

def plot_accuracy_vs_weight(weights: List[float], accuracies: List[float],
                           metric_name: str = 'Accuracy',
                           save_path: Optional[str] = None) -> None:
    """
    Plot accuracy vs. weight.

    Args:
        weights: List of weight values (e.g., image weights).
        accuracies: List of accuracy values corresponding to each weight.
        metric_name: Name of the metric (e.g., 'Top-1 Accuracy').
        save_path: Path to save the figure. If None, display the plot.
    """
    plt.figure(figsize=(8, 6))
    plt.plot(weights, accuracies, marker='o', linewidth=2, markersize=8)
    plt.xlabel('Image Weight', fontsize=12)
    plt.ylabel(metric_name, fontsize=12)
    plt.title(f'{metric_name} vs. Image Weight', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(weights)
    plt.yticks(np.arange(0, 1.05, 0.1))
    plt.ylim(0, 1.05)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_runtime_breakdown(times: List[float], labels: List[str],
                          title: str = 'Runtime Breakdown',
                          save_path: Optional[str] = None) -> None:
    """
    Plot a pie chart of runtime breakdown.

    Args:
        times: List of times for each component.
        labels: List of labels for each component.
        title: Title of the plot.
        save_path: Path to save the figure. If None, display the plot.
    """
    plt.figure(figsize=(8, 8))
    plt.pie(times, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=plt.cm.Pastel1(range(len(labels))))
    plt.title(title, fontsize=14)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_horizontal_bar(values: List[float], labels: List[str],
                       title: str = 'Horizontal Bar Chart',
                       xlabel: str = 'Value',
                       ylabel: str = 'Category',
                       save_path: Optional[str] = None) -> None:
    """
    Plot a horizontal bar chart.

    Args:
        values: List of values for each bar.
        labels: List of labels for each bar.
        title: Title of the plot.
        xlabel: Label for x-axis.
        ylabel: Label for y-axis.
        save_path: Path to save the figure. If None, display the plot.
    """
    plt.figure(figsize=(10, 6))
    y_pos = np.arange(len(labels))
    plt.barh(y_pos, values, align='center', alpha=0.7)
    plt.yticks(y_pos, labels)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # Invert y-axis to have the first label at the top
    plt.gca().invert_yaxis()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_confusion_matrix_if_needed(failure_data: List[Dict[str, Any]],
                                   save_path: Optional[str] = None) -> None:
    """
    Plot a confusion matrix for failure analysis if there are failures.

    Args:
        failure_data: List of dictionaries containing failure information.
        save_path: Path to save the figure. If None, display the plot.
    """
    if not failure_data:
        print("No failures to plot.")
        return

    # We'll create a confusion matrix between expected and retrieved concepts
    # For simplicity, we'll just note that this is a placeholder.
    # In a real scenario, we would compute a confusion matrix.
    # Since the task says "if failures exist", we'll create a simple bar chart of failure counts by concept.

    # Count failures by expected concept
    from collections import Counter
    expected_counts = Counter([f['expected_concept'] for f in failure_data])
    retrieved_counts = Counter([f['retrieved_concept'] for f in failure_data])

    # We'll create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot expected concept failures
    concepts = list(expected_counts.keys())
    counts = list(expected_counts.values())
    y_pos = np.arange(len(concepts))
    ax1.barh(y_pos, counts, align='center', alpha=0.7, color='red')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(concepts)
    ax1.set_xlabel('Number of Failures')
    ax1.set_title('Failures by Expected Concept')
    ax1.invert_yaxis()

    # Plot retrieved concept failures
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

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()