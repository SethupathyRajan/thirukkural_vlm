import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Dataset directory
DATASET_DIR = BASE_DIR / "dataset"

# Database directory
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "metadata.db"

# Dataset files
KURAL_CSV = DATASET_DIR / "kural.csv"
CONCEPTS_CSV = DATASET_DIR / "concepts.csv"
CONCEPT_KURAL_MAP_XLSX = DATASET_DIR / "concept_kural_map.xlsx"
IMAGE_DESCRIPTION_CSV = DATASET_DIR / "image_description.csv"
QUESTIONS_XLSX = DATASET_DIR / "questions.xlsx"
SCENARIO_XLSX = DATASET_DIR / "scenario.xlsx"

# Images directory
IMAGES_DIR = DATASET_DIR / "images"

# Ensure directories exist
DATABASE_DIR.mkdir(exist_ok=True)
