#!/usr/bin/env python3
"""Verify ID consistency between embeddings and knowledge objects."""

import numpy as np
import json
from pathlib import Path
from config.config import EMBEDDINGS_DIR

def main():
    # Load ID arrays
    image_ids = np.load(EMBEDDINGS_DIR / "image_embedding_ids.npy", allow_pickle=True)
    knowledge_ids = np.load(EMBEDDINGS_DIR / "knowledge_embedding_ids.npy", allow_pickle=True)

    # Load knowledge objects
    knowledge_objects_path = Path(__file__).parent / "dataset" / "knowledge_objects.json"
    with open(knowledge_objects_path, 'r') as f:
        knowledge_objects = json.load(f)

    # Extract scenario IDs from knowledge objects
    kb_scenario_ids = [obj.get('scenario_id') for obj in knowledge_objects]
    kb_scenario_ids = np.array(kb_scenario_ids)

    print(f"Number of image IDs: {len(image_ids)}")
    print(f"Number of knowledge IDs: {len(knowledge_ids)}")
    print(f"Number of knowledge objects: {len(kb_scenario_ids)}")

    # Check for duplicates
    def check_duplicates(arr, name):
        unique, counts = np.unique(arr, return_counts=True)
        duplicates = unique[counts > 1]
        if len(duplicates) > 0:
            print(f"ERROR: {name} has duplicate IDs: {duplicates}")
        else:
            print(f"OK: {name} has no duplicate IDs.")

    check_duplicates(image_ids, "image IDs")
    check_duplicates(knowledge_ids, "knowledge IDs")
    check_duplicates(kb_scenario_ids, "knowledge object scenario IDs")

    # Check set equality
    set_image = set(image_ids)
    set_knowledge = set(knowledge_ids)
    set_kb = set(kb_scenario_ids)

    if set_image == set_knowledge == set_kb:
        print("OK: All ID sets are equal.")
    else:
        print("ERROR: ID sets differ.")
        print(f"  Image IDs - Knowledge IDs: {set_image.symmetric_difference(set_knowledge)}")
        print(f"  Image IDs - KB IDs: {set_image.symmetric_difference(set_kb)}")
        print(f"  Knowledge IDs - KB IDs: {set_knowledge.symmetric_difference(set_kb)}")

    # Check that the number of IDs matches the number of embeddings
    image_embeddings = np.load(EMBEDDINGS_DIR / "image_embeddings.npy")
    knowledge_embeddings = np.load(EMBEDDINGS_DIR / "knowledge_embeddings.npy")

    if len(image_ids) == image_embeddings.shape[0]:
        print("OK: Number of image IDs matches number of image embeddings.")
    else:
        print(f"ERROR: Image IDs count ({len(image_ids)}) != image embeddings count ({image_embeddings.shape[0]})")

    if len(knowledge_ids) == knowledge_embeddings.shape[0]:
        print("OK: Number of knowledge IDs matches number of knowledge embeddings.")
    else:
        print(f"ERROR: Knowledge IDs count ({len(knowledge_ids)}) != knowledge embeddings count ({knowledge_embeddings.shape[0]})")

    # Check that all IDs are strings (or at least print type)
    if len(image_ids) > 0:
        print(f"ID type example: image_ids[0] is {type(image_ids[0])}, knowledge_ids[0] is {type(knowledge_ids[0])}")

if __name__ == "__main__":
    main()