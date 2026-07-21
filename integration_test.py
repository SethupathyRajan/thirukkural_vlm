#!/usr/bin/env python3
"""
Integration test for the explainability engine with the inference engine.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from inference import InferenceEngine
from explainability import ExplainabilityEngine

def main():
    print("Initializing inference engine...")
    engine = InferenceEngine()
    engine.load()
    print(f"Engine loaded in {engine.initialization_time:.2f} seconds")

    # Use a sample image from the dataset
    image_path = Path(__file__).parent / "dataset" / "images" / "S001.jpg"
    if not image_path.exists():
        print(f"ERROR: Image not found at {image_path}")
        return 1

    print(f"Making prediction for {image_path.name}...")
    prediction = engine.predict(str(image_path))
    print(f"Prediction: {prediction.scenario_id} (confidence: {prediction.confidence:.4f})")

    print("Generating explanation...")
    explainer = ExplainabilityEngine()
    explanation = explainer.generate_explanation(prediction)

    print("\n" + "="*60)
    print("EXPLANATION OUTPUT")
    print("="*60)
    print(explainer.format_explanation(explanation))
    print("="*60)

    # Also test the dict conversion
    exp_dict = explanation.to_dict()
    print("\nExplanation as dict keys:", list(exp_dict.keys()))

    return 0

if __name__ == "__main__":
    sys.exit(main())