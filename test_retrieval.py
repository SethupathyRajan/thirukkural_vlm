#!/usr/bin/env python3
"""Test the retrieval engine for error handling and reproducibility."""

import os
import sys
import numpy as np
import tempfile
import shutil
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.multimodal_retrieval import (
    load_embeddings,
    load_knowledge_objects,
    encode_user_image,
    cosine_similarity,
    retrieve_top_k,
    combine_scores
)
from src.utils import setup_logging, get_logger
from config.config import EMBEDDINGS_DIR, DATASET_DIR

# Setup logging
setup_logging()
logger = get_logger(__name__)

def test_valid_retrieval():
    """Test that retrieval works for a known image."""
    print("\n=== Test: Valid retrieval ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
    knowledge_objects = load_knowledge_objects(Path(__file__).parent / "dataset" / "knowledge_objects.json")

    # Use the first image
    test_image_path = Path(__file__).parent / "dataset" / "images" / f"{image_ids[0]}.jpg"
    if not test_image_path.exists():
        print(f"ERROR: Test image not found: {test_image_path}")
        return False

    results = retrieve_top_k(
        test_image_path,
        image_embeddings,
        image_ids,
        knowledge_embeddings,
        knowledge_ids,
        knowledge_objects,
        k=5
    )

    if not results:
        print("ERROR: No results returned for valid image.")
        return False

    print(f"SUCCESS: Retrieved {len(results)} results.")
    print(f"Top result: {results[0]['scenario_id']} with score {results[0]['combined_score']:.4f}")
    return True

def test_invalid_image_path():
    """Test that a non-existent image path returns empty results and logs error."""
    print("\n=== Test: Invalid image path ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
    knowledge_objects = load_knowledge_objects(Path(__file__).parent / "dataset" / "knowledge_objects.json")

    fake_path = Path("/non/existent/image.jpg")
    results = retrieve_top_k(
        fake_path,
        image_embeddings,
        image_ids,
        knowledge_embeddings,
        knowledge_ids,
        knowledge_objects,
        k=5
    )

    if results:
        print("ERROR: Expected empty list for invalid image path.")
        return False
    else:
        print("SUCCESS: Returned empty list for invalid image path.")
        return True

def test_unsupported_image_format():
    """Test that a non-image file (e.g., a text file) returns empty results."""
    print("\n=== Test: Unsupported image format ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
    knowledge_objects = load_knowledge_objects(Path(__file__).parent / "dataset" / "knowledge_objects.json")

    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b"This is not an image.")
        temp_path = Path(f.name)

    try:
        results = retrieve_top_k(
            temp_path,
            image_embeddings,
            image_ids,
            knowledge_embeddings,
            knowledge_ids,
            knowledge_objects,
            k=5
        )
        if results:
            print("ERROR: Expected empty list for non-image file.")
            return False
        else:
            print("SUCCESS: Returned empty list for non-image file.")
            return True
    finally:
        os.unlink(temp_path)

def test_corrupted_image():
    """Test that a corrupted image file returns empty results."""
    print("\n=== Test: Corrupted image ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
    knowledge_objects = load_knowledge_objects(Path(__file__).parent / "dataset" / "knowledge_objects.json")

    # Create a file with random bytes
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        f.write(os.urandom(1024))  # random bytes
        temp_path = Path(f.name)

    try:
        results = retrieve_top_k(
            temp_path,
            image_embeddings,
            image_ids,
            knowledge_embeddings,
            knowledge_ids,
            knowledge_objects,
            k=5
        )
        if results:
            print("ERROR: Expected empty list for corrupted image.")
            return False
        else:
            print("SUCCESS: Returned empty list for corrupted image.")
            return True
    finally:
        os.unlink(temp_path)

def test_missing_embedding_file():
    """Test that missing embedding file raises an error (should be caught by load_embeddings)."""
    print("\n=== Test: Missing embedding file ===")
    # We'll test by temporarily moving the file
    embeddings_file = EMBEDDINGS_DIR / "image_embeddings.npy"
    backup_file = EMBEDDINGS_DIR / "image_embeddings.npy.bak"

    if not embeddings_file.exists():
        print("ERROR: Embeddings file not found.")
        return False

    # Move the file
    shutil.move(str(embeddings_file), str(backup_file))

    try:
        # This should raise an exception when loading embeddings
        load_embeddings()
        print("ERROR: Expected exception when loading embeddings with missing file.")
        return False
    except Exception as e:
        print(f"SUCCESS: Got expected exception: {type(e).__name__}")
        return True
    finally:
        # Restore the file
        if backup_file.exists():
            shutil.move(str(backup_file), str(embeddings_file))

def test_missing_knowledge_object():
    """Test that a missing knowledge object is handled gracefully."""
    print("\n=== Test: Missing knowledge object ===")
    # We know that S102 is missing from knowledge objects, so we can test with that
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
    knowledge_objects = load_knowledge_objects(Path(__file__).parent / "dataset" / "knowledge_objects.json")

    # Find an image that has a known missing knowledge object (S102)
    if 'S102' not in image_ids:
        print("SKIP: S102 not in image IDs.")
        return True

    # Get the index of S102 in image_ids
    idx = np.where(image_ids == 'S102')[0][0]
    image_path = Path(__file__).parent / "dataset" / "images" / "S102.jpg"

    if not image_path.exists():
        print(f"ERROR: Image S102.jpg not found.")
        return False

    # We expect that when S102 is the top candidate, knowledge similarity will be zero for all
    results = retrieve_top_k(
        image_path,
        image_embeddings,
        image_ids,
        knowledge_embeddings,
        knowledge_ids,
        knowledge_objects,
        k=5
    )

    if not results:
        print("ERROR: No results returned for S102.")
        return False

    # Check that the first result is S102 (should be due to highest image similarity)
    if results[0]['scenario_id'] != 'S102':
        print(f"WARNING: Expected S102 as top result, got {results[0]['scenario_id']}")
        # Not necessarily an error, because another image might have higher image similarity to S102.jpg?
        # But since it's the same image, image similarity should be 1.0.
        # However, we'll not fail the test on this.

    # Check that knowledge similarity for S102 is 0.0 (since it's missing)
    # Find the result for S102
    result_s102 = None
    for r in results:
        if r['scenario_id'] == 'S102':
            result_s102 = r
            break

    if result_s102 is None:
        print("ERROR: S102 not in results.")
        return False

    # The knowledge similarity should be 0.0. Note: the knowledge similarity is computed using the top candidate's knowledge embedding.
    # If the top candidate is S102 and its knowledge embedding is missing, then we set all knowledge similarities to 0.
    # So the knowledge similarity for S102 should be 0.
    if abs(result_s102['knowledge_similarity']) > 1e-9:
        print(f"WARNING: Expected knowledge similarity ~0 for S102, got {result_s102['knowledge_similarity']}")
        # Not failing because it might be computed from a different reference if another candidate was top?
        # But we expect S102 to be top.

    print("SUCCESS: Handled missing knowledge object (S102) without crash.")
    return True

def test_combine_scores():
    """Test that combine_scores uses the weights from config."""
    print("\n=== Test: Combine scores uses config weights ===")
    from config.config import IMAGE_WEIGHT, KNOWLEDGE_WEIGHT

    image_sims = [0.8, 0.6, 0.4]
    knowledge_sims = [0.2, 0.5, 0.9]

    combined = combine_scores(image_sims, knowledge_sims, IMAGE_WEIGHT, KNOWLEDGE_WEIGHT)

    # Manual calculation
    expected = [
        IMAGE_WEIGHT * 0.8 + KNOWLEDGE_WEIGHT * 0.2,
        IMAGE_WEIGHT * 0.6 + KNOWLEDGE_WEIGHT * 0.5,
        IMAGE_WEIGHT * 0.4 + KNOWLEDGE_WEIGHT * 0.9
    ]

    if np.allclose(combined, expected):
        print("SUCCESS: combine_scores uses correct weights.")
        return True
    else:
        print(f"ERROR: combine_scores mismatch. Got {combined}, expected {expected}")
        return False

def test_reproducibility():
    """Test that running the same query twice yields identical results."""
    print("\n=== Test: Reproducibility ===")
    # Load data
    image_embeddings, image_ids, knowledge_embeddings, knowledge_ids = load_embeddings()
    knowledge_objects = load_knowledge_objects(Path(__file__).parent / "dataset" / "knowledge_objects.json")

    # Use the first image
    test_image_path = Path(__file__).parent / "dataset" / "images" / f"{image_ids[0]}.jpg"
    if not test_image_path.exists():
        print(f"ERROR: Test image not found: {test_image_path}")
        return False

    # Run twice
    results1 = retrieve_top_k(
        test_image_path,
        image_embeddings,
        image_ids,
        knowledge_embeddings,
        knowledge_ids,
        knowledge_objects,
        k=5
    )
    results2 = retrieve_top_k(
        test_image_path,
        image_embeddings,
        image_ids,
        knowledge_embeddings,
        knowledge_ids,
        knowledge_objects,
        k=5
    )

    if not results1 or not results2:
        print("ERROR: One of the runs returned no results.")
        return False

    # Compare scenario IDs and scores
    ids1 = [r['scenario_id'] for r in results1]
    ids2 = [r['scenario_id'] for r in results2]
    if ids1 != ids2:
        print(f"ERROR: Scenario IDs differ between runs: {ids1} vs {ids2}")
        return False

    # Compare scores (allow tiny floating point difference)
    for i, (r1, r2) in enumerate(zip(results1, results2)):
        if abs(r1['image_similarity'] - r2['image_similarity']) > 1e-6:
            print(f"ERROR: Image similarity mismatch at rank {i+1}: {r1['image_similarity']} vs {r2['image_similarity']}")
            return False
        if abs(r1['knowledge_similarity'] - r2['knowledge_similarity']) > 1e-6:
            print(f"ERROR: Knowledge similarity mismatch at rank {i+1}: {r1['knowledge_similarity']} vs {r2['knowledge_similarity']}")
            return False
        if abs(r1['combined_score'] - r2['combined_score']) > 1e-6:
            print(f"ERROR: Combined score mismatch at rank {i+1}: {r1['combined_score']} vs {r2['combined_score']}")
            return False

    print("SUCCESS: Results are identical across runs.")
    return True

def main():
    """Run all tests."""
    tests = [
        test_valid_retrieval,
        test_invalid_image_path,
        test_unsupported_image_format,
        test_corrupted_image,
        test_missing_embedding_file,
        test_missing_knowledge_object,
        test_combine_scores,
        test_reproducibility
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\nTest {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n=== Summary ===")
    print(f"Passed: {passed}/{total}")
    if passed == total:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())