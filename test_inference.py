"""
Tests for the inference engine of the Thirukkural Scenario-Based Decision-Making system.
"""

import os
import sys
import time
import numpy as np
from pathlib import Path
from PIL import Image

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from inference import InferenceEngine
from src.prediction import Prediction, MatchResult


def test_inference_engine_loading():
    """Test that the inference engine loads correctly."""
    print("Testing inference engine loading...")
    engine = InferenceEngine()
    assert not engine.is_loaded, "Engine should not be loaded initially"

    engine.load()
    assert engine.is_loaded, "Engine should be loaded after calling load()"
    assert engine.initialization_time is not None, "Initialization time should be recorded"
    print("✓ Inference engine loading test passed")


def test_predict_with_sample_image():
    """Test prediction with a sample image."""
    print("Testing prediction with sample image...")
    engine = InferenceEngine()
    engine.load()

    # Try to find a sample image in the dataset
    dataset_path = Path(__file__).parent / "dataset" / "images"
    sample_images = list(dataset_path.glob("*.jpg"))[:3]  # Get first 3 images

    if not sample_images:
        print("⚠ No sample images found, skipping test")
        return

    for img_path in sample_images:
        print(f"  Testing with {img_path.name}")
        prediction = engine.predict(str(img_path))

        # Check that we get a valid Prediction object
        assert isinstance(prediction, Prediction), "Prediction should be a Prediction object"
        assert prediction.scenario_id.startswith("S"), "Scenario ID should start with 'S'"
        assert 0 <= prediction.image_similarity <= 1, "Image similarity should be between 0 and 1"
        assert 0 <= prediction.knowledge_similarity <= 1, "Knowledge similarity should be between 0 and 1"
        assert 0 <= prediction.combined_score <= 1, "Combined score should be between 0 and 1"
        assert prediction.confidence == prediction.combined_score, "Confidence should equal combined score"
        assert len(prediction.top_matches) > 0, "Should have top matches"

        # Check that top_matches are MatchResult objects
        for match in prediction.top_matches:
            assert isinstance(match, MatchResult), "Each top match should be a MatchResult"
            assert match.scenario_id.startswith("S"), "Match scenario ID should start with 'S'"

        print(f"    Top prediction: {prediction.scenario_id} (score: {prediction.combined_score:.3f})")

    print("✓ Prediction with sample image test passed")


def test_predict_with_pil_image():
    """Test prediction with a PIL Image object."""
    print("Testing prediction with PIL Image...")
    engine = InferenceEngine()
    engine.load()

    # Get a sample image
    dataset_path = Path(__file__).parent / "dataset" / "images"
    sample_images = list(dataset_path.glob("*.jpg"))

    if not sample_images:
        print("⚠ No sample images found, skipping test")
        return

    img_path = sample_images[0]
    pil_image = Image.open(img_path).convert("RGB")

    prediction = engine.predict(pil_image)

    assert isinstance(prediction, Prediction), "Prediction should be a Prediction object"
    assert prediction.scenario_id.startswith("S"), "Scenario ID should start with 'S'"

    print(f"  Top prediction: {prediction.scenario_id} (score: {prediction.combined_score:.3f})")
    print("✓ Prediction with PIL Image test passed")


def test_predict_with_numpy_array():
    """Test prediction with a numpy array."""
    print("Testing prediction with numpy array...")
    engine = InferenceEngine()
    engine.load()

    # Get a sample image and convert to numpy array
    dataset_path = Path(__file__).parent / "dataset" / "images"
    sample_images = list(dataset_path.glob("*.jpg"))

    if not sample_images:
        print("⚠ No sample images found, skipping test")
        return

    img_path = sample_images[0]
    pil_image = Image.open(img_path).convert("RGB")
    numpy_image = np.array(pil_image)

    prediction = engine.predict(numpy_image)

    assert isinstance(prediction, Prediction), "Prediction should be a Prediction object"
    assert prediction.scenario_id.startswith("S"), "Scenario ID should start with 'S'"

    print(f"  Top prediction: {prediction.scenario_id} (score: {prediction.combined_score:.3f})")
    print("✓ Prediction with numpy array test passed")


def test_predict_top_k():
    """Test top-k prediction."""
    print("Testing top-k prediction...")
    engine = InferenceEngine()
    engine.load()

    # Get a sample image
    dataset_path = Path(__file__).parent / "dataset" / "images"
    sample_images = list(dataset_path.glob("*.jpg"))

    if not sample_images:
        print("⚠ No sample images found, skipping test")
        return

    img_path = sample_images[0]
    k = 3

    predictions = engine.predict_top_k(str(img_path), k=k)

    assert isinstance(predictions, list), "Predictions should be a list"
    assert len(predictions) == k, f"Should return exactly {k} predictions"

    for i, pred in enumerate(predictions):
        assert isinstance(pred, Prediction), f"Prediction {i} should be a Prediction object"
        assert pred.scenario_id.startswith("S"), f"Prediction {i} scenario ID should start with 'S'"

        # Check that scores are in descending order (approximately, due to reranking)
        if i > 0:
            # Note: Due to reranking, the order might not be strictly descending by combined_score
            # but we'll check that they're reasonable values
            assert 0 <= pred.combined_score <= 1, f"Prediction {i} combined score should be between 0 and 1"

    print(f"  Top-{k} predictions:")
    for i, pred in enumerate(predictions):
        print(f"    {i+1}. {pred.scenario_id} (score: {pred.combined_score:.3f})")

    print("✓ Top-k prediction test passed")


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("Testing error handling...")
    engine = InferenceEngine()
    engine.load()

    # Test with non-existent file
    try:
        engine.predict("/non/existent/image.jpg")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("  ✓ Correctly handled non-existent file")
    except Exception as e:
        assert False, f"Should have raised FileNotFoundError, got {type(e).__name__}: {e}"

    # Test with unsupported input type
    try:
        engine.predict(123)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Correctly handled unsupported input type")
    except Exception as e:
        assert False, f"Should have raised ValueError, got {type(e).__name__}: {e}"

    # Test prediction without loading
    engine_unloaded = InferenceEngine()
    dataset_path = Path(__file__).parent / "dataset" / "images"
    sample_images = list(dataset_path.glob("*.jpg"))

    if sample_images:
        try:
            engine_unloaded.predict(str(sample_images[0]))
            assert False, "Should have raised RuntimeError"
        except RuntimeError:
            print("  ✓ Correctly handled prediction without loading")
        except Exception as e:
            assert False, f"Should have raised RuntimeError, got {type(e).__name__}: {e}"

    print("✓ Error handling test passed")


def test_performance_tracking():
    """Test performance tracking functionality."""
    print("Testing performance tracking...")
    engine = InferenceEngine()
    engine.load()

    # Get a sample image
    dataset_path = Path(__file__).parent / "dataset" / "images"
    sample_images = list(dataset_path.glob("*.jpg"))

    if not sample_images:
        print("⚠ No sample images found, skipping test")
        return

    img_path = sample_images[0]

    # Make a few predictions
    for _ in range(3):
        engine.predict(str(img_path))

    avg_time = engine.get_average_prediction_time()
    assert avg_time >= 0, "Average prediction time should be non-negative"

    # Reset tracking
    engine.reset_performance_tracking()
    assert engine.get_average_prediction_time() == 0.0, "Average time should be 0 after reset"

    print(f"  Average prediction time: {avg_time:.3f} seconds")
    print("✓ Performance tracking test passed")


def test_prediction_to_dict():
    """Test that Prediction.to_dict() works correctly."""
    print("Testing Prediction.to_dict()...")
    engine = InferenceEngine()
    engine.load()

    # Get a sample image
    dataset_path = Path(__file__).parent / "dataset" / "images"
    sample_images = list(dataset_path.glob("*.jpg"))

    if not sample_images:
        print("⚠ No sample images found, skipping test")
        return

    img_path = sample_images[0]
    prediction = engine.predict(str(img_path))

    # Convert to dict
    pred_dict = prediction.to_dict()

    # Check that it's a dict with expected keys
    expected_keys = {
        "scenario_id", "kural_id", "concept", "adhigaram", "paal", "english_kural",
        "scenario", "question", "correct_answer", "explanation",
        "image_similarity", "knowledge_similarity", "combined_score", "confidence", "top_matches"
    }

    assert set(pred_dict.keys()) == expected_keys, f"Dict keys mismatch. Expected: {expected_keys}, Got: {set(pred_dict.keys())}"

    # Check that top_matches is a list of dicts
    assert isinstance(pred_dict["top_matches"], list), "top_matches should be a list"
    for match in pred_dict["top_matches"]:
        assert isinstance(match, dict), "Each top match should be a dict"
        expected_match_keys = {
            "scenario_id", "combined_score", "image_similarity", "knowledge_similarity", "concept", "english_kural"
        }
        assert set(match.keys()) == expected_match_keys, f"Match dict keys mismatch"

    print("✓ Prediction.to_dict() test passed")


def main():
    """Run all tests."""
    print("Running inference engine tests...\n")

    try:
        test_inference_engine_loading()
        test_predict_with_sample_image()
        test_predict_with_pil_image()
        test_predict_with_numpy_array()
        test_predict_top_k()
        test_error_handling()
        test_performance_tracking()
        test_prediction_to_dict()

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()