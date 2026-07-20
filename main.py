"""
Main entry point for the Thirukkural Scenario-Based Decision-Making project.
This script demonstrates the infrastructure built in Phase 2.2.
It does not generate embeddings or perform inference.
"""
import logging
from pathlib import Path

# Import our infrastructure modules
from config.config import setup_logging, DATABASE_PATH, DEVICE, TEXT_MODEL_NAME, IMAGE_MODEL_NAME
from src.loader import (
    load_all_scenarios,
    load_scenario_by_id,
    load_all_questions,
    load_all_kurals,
    load_all_concepts
)
from src.model_manager import load_image_model, load_text_model
from src.utils import setup_logging as setup_app_logging, get_logger

# Set up logging
setup_app_logging()
logger = get_logger(__name__)

def main():
    """Demonstrate the infrastructure without performing embedding generation."""
    logger.info("=" * 60)
    logger.info("THIRUKKURAL SCENARIO-BASED DECISION-MAKING")
    logger.info("INFRASTRUCTURE DEMONSTRATION - PHASE 2.2")
    logger.info("=" * 60)
    
    # Show configuration
    logger.info(f"Database path: {DATABASE_PATH}")
    logger.info(f"Device: {DEVICE}")
    logger.info(f"Text model: {TEXT_MODEL_NAME}")
    logger.info(f"Image model: {IMAGE_MODEL_NAME}")
    
    # Demonstrate data loading
    logger.info("\n--- Loading data from database ---")
    scenarios = load_all_scenarios()
    logger.info(f"Loaded {len(scenarios)} scenarios.")
    
    questions = load_all_questions()
    logger.info(f"Loaded {len(questions)} questions.")
    
    kurals = load_all_kurals()
    logger.info(f"Loaded {len(kurals)} kurals.")
    
    concepts = load_all_concepts()
    logger.info(f"Loaded {len(concepts)} concepts.")
    
    # Show a sample
    if scenarios:
        sample = scenarios[0]
        logger.info(f"\nSample scenario (ID: {sample['scenario_id']}):")
        logger.info(f"  Text: {sample['scenario_text'][:100]}...")
        logger.info(f"  Associated Kural: {sample.get('tamil_kural', 'N/A')[:50]}...")
    
    # Demonstrate model loading (without inference)
    logger.info("\n--- Loading models ---")
    try:
        # Load image model (returns model and preprocess function)
        image_model, image_preprocess = load_image_model()
        logger.info(f"Image model loaded: {type(image_model).__name__}")
        logger.info(f"Image preprocess function: {type(image_preprocess).__name__}")
    except Exception as e:
        logger.error(f"Failed to load image model: {e}")
    
    try:
        # Load text model
        text_model = load_text_model()
        logger.info(f"Text model loaded: {type(text_model).__name__}")
    except Exception as e:
        logger.error(f"Failed to load text model: {e}")
    
    # Demonstrate embedding manager (placeholder functions)
    logger.info("\n--- Embedding manager (placeholders) ---")
    # These functions would be used in the next phase to generate embeddings
    # For now, they just return the data with None placeholders
    from src.embedding_manager import embed_all_scenarios, embed_questions, embed_kurals
    
    scenarios_with_placeholders = embed_all_scenarios()
    logger.info(f"Prepared {len(scenarios_with_placeholders)} scenarios for embedding (placeholders).")
    
    questions_with_placeholders = embed_questions()
    logger.info(f"Prepared {len(questions_with_placeholders)} questions for embedding (placeholders).")
    
    kurals_with_placeholders = embed_kurals()
    logger.info(f"Prepared {len(kurals_with_placeholders)} korals for embedding (placeholders).")
    
    logger.info("\n" + "=" * 60)
    logger.info("Infrastructure demonstration complete.")
    logger.info("No embeddings were generated in this phase.")
    logger.info("The system is ready for Phase 2.3 (embedding generation).")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
