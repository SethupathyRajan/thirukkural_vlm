#!/usr/bin/env python3
"""
Debug script to inspect knowledge objects.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from loader import load_all_scenarios

def main():
    print("Loading knowledge objects...")
    knowledge_objects = load_all_scenarios()

    print(f"Loaded {len(knowledge_objects)} knowledge objects")

    # Look at the first few objects
    for i, obj in enumerate(knowledge_objects[:5]):
        print(f"\nObject {i}:")
        for key, value in obj.items():
            print(f"  {key}: {value}")

        # Also check if this is S001
        if obj.get('scenario_id') == 'S001':
            print(f"  >>> This is S001!")

if __name__ == "__main__":
    main()