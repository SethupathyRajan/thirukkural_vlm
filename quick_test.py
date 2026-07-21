#!/usr/bin/env python3
"""
Quick test for the inference engine.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from inference import InferenceEngine

def main():
    print("Testing inference engine...")

    # Initialize engine
    engine = InferenceEngine()

    # Load resources
    print("Loading engine...")
    engine.load()
    print(f"Engine loaded in {engine.initialization_time:.2f} seconds")

    # Test with a sample image
    image_path = Path(__file__).parent / "dataset" / "images" / "S001.jpg"
    if not image_path.exists():
        print(f"ERROR: Image not found at {image_path}")
        return 1

    print(f"Making prediction for {image_path}...")
    prediction = engine.predict(str(image_path))

    # Print results
    print("\nPrediction Results:")
    print(f"  Scenario ID: {prediction.scenario_id}")
    print(f"  Kural ID: {prediction.kural_id}")
    print(f"  Concept: {prediction.concept}")
    print(f"  Adhigaram: {prediction.adhigaram}")
    print(f"  Paal: {prediction.paal}")
    print(f"  English Kural: {prediction.english_kural}")
    print(f"  Scenario: {prediction.scenario[:100]}..." if len(prediction.scenario) > 100 else f"  Scenario: {prediction.scenario}")
    print(f"  Question: {prediction.question[:100]}..." if len(prediction.question) > 100 else f"  Question: {prediction.question}")
    print(f"  Correct Answer: {prediction.correct_answer}")
    print(f"  Explanation: {prediction.explanation[:100]}..." if len(prediction.explanation) > 100 else f"  Explanation: {prediction.explanation}")
    print(f"  Image Similarity: {prediction.image_similarity:.4f}")
    print(f"  Knowledge Similarity: {prediction.knowledge_similarity:.4f}")
    print(f"  Combined Score: {prediction.combined_score:.4f}")
    print(f"  Confidence: {prediction.confidence:.4f}")
    print(f"  Number of Top Matches: {len(prediction.top_matches)}")

    # Print top 3 matches
    print("\nTop 3 Matches:")
    for i, match in enumerate(prediction.top_matches[:3]):
        print(f"  {i+1}. {match.scenario_id} (score: {match.combined_score:.4f})")

    # Test top-k prediction
    print("\nTesting top-3 prediction...")
    top_k_predictions = engine.predict_top_k(str(image_path), k=3)
    print(f"Top-3 predictions:")
    for i, pred in enumerate(top_k_predictions):
        print(f"  {i+1}. {pred.scenario_id} (score: {pred.combined_score:.4f})")

    # Test performance tracking
    avg_time = engine.get_average_prediction_time()
    print(f"\nAverage prediction time: {avg_time:.4f} seconds")

    print("\n✅ All tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())