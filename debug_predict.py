#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))
from inference import InferenceEngine

engine = InferenceEngine()
engine.load()
print("Engine loaded")

dataset_path = Path(__file__).parent / "dataset" / "images"
sample_images = list(dataset_path.glob("*.jpg"))
if sample_images:
    img_path = sample_images[0]
    print(f"Predicting on {img_path}")
    prediction = engine.predict(str(img_path))
    print(f"Type of prediction: {type(prediction)}")
    print(f"Prediction: {prediction}")
else:
    print("No images")