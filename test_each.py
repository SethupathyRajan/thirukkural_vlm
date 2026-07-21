#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))
from inference import InferenceEngine
from prediction import Prediction

engine = InferenceEngine()
engine.load()

dataset_path = Path(__file__).parent / "dataset" / "images"
sample_images = list(dataset_path.glob("*.jpg"))[:3]

for img_path in sample_images:
    print(f"Testing with {img_path.name}")
    prediction = engine.predict(str(img_path))
    print(f"  Type: {type(prediction)}")
    print(f"  Is Prediction? {isinstance(prediction, Prediction)}")
    if not isinstance(prediction, Prediction):
        print(f"  Actual value: {prediction}")