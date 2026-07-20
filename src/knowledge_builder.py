"""
Knowledge representation construction for scenarios.
This script is for Phase 2.5: Knowledge Representation Construction.
"""

import sys
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our infrastructure modules
from config.config import DATASET_DIR
from src.loader import (
    load_all_scenarios,
    load_all_questions,
    load_all_kurals
)
from src.utils import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

def preprocess_text(text: str) -> str:
    """Preprocess text: strip, replace multiple spaces with single space.

    Args:
        text: Input text string.

    Returns:
        Preprocessed text string.
    """
    if not isinstance(text, str):
        return ""
    # Strip leading/trailing whitespace
    text = text.strip()
    # Replace multiple spaces with a single space
    import re
    text = re.sub(r'\s+', ' ', text)
    return text

def build_knowledge_text(scenario: Dict[str, Any],
                         question: Dict[str, Any],
                         kural_adhigaram: Dict[str, Any],
                         paal: Optional[str] = None) -> str:
    """Build a standardized knowledge text from scenario, question, and kural data.

    Args:
        scenario: Dictionary containing scenario data.
        question: Dictionary containing question data.
        kural_adhigaram: Dictionary containing kural data (with adhigaram).
        paal: Optional precomputed paal string. If not provided, will be derived from scenario.

    Returns:
        A formatted knowledge text string.
    """
    # Extract fields with fallback to empty string
    scenario_text = preprocess_text(scenario.get('scenario_text', ''))
    question_text = preprocess_text(question.get('question_text', ''))
    option_a = preprocess_text(question.get('option_a', ''))
    option_b = preprocess_text(question.get('option_b', ''))
    option_c = preprocess_text(question.get('option_c', ''))
    option_d = preprocess_text(question.get('option_d', ''))
    correct_option = question.get('correct_option', '').strip().upper()
    explanation = preprocess_text(question.get('explanation', ''))
    english_kural = preprocess_text(scenario.get('english_kural', ''))
    concept_name = preprocess_text(scenario.get('concept_name', ''))
    adhigaram = preprocess_text(kural_adhigaram.get('adhigaram', ''))

    # Map correct option letter to the actual option text
    correct_answer_text = ""
    if correct_option == 'A':
        correct_answer_text = option_a
    elif correct_option == 'B':
        correct_answer_text = option_b
    elif correct_option == 'C':
        correct_answer_text = option_c
    elif correct_option == 'D':
        correct_answer_text = option_d

    # If paal is not provided, try to get it from scenario (for backward compatibility)
    if paal is None:
        paal = scenario.get('paal_name')

    # Build the knowledge text following the template
    knowledge_text = f"""Scenario:
{scenario_text}

Question:
{question_text}

Correct Answer:
{correct_answer_text}

Explanation:
{explanation}

Thirukkural:
{english_kural}

Concept:
{concept_name}

Adhigaram:
{adhigaram}

Paal:
{paal}"""

    return knowledge_text

def build_knowledge_object(scenario: Dict[str, Any],
                           question: Dict[str, Any],
                           kural_adhigaram: Dict[str, Any],
                           paal: Optional[str] = None) -> Dict[str, Any]:
    """Build a complete knowledge object for a scenario.

    Args:
        scenario: Dictionary containing scenario data.
        question: Dictionary containing question data.
        kural_adhigaram: Dictionary containing kural data (with adhigaram).
        paal: Optional precomputed paal string. If not provided, will be derived from scenario.

    Returns:
        A dictionary representing the knowledge object.
    """
    # If paal is not provided, get it from scenario (for backward compatibility)
    if paal is None:
        paal = scenario.get('paal_name')

    knowledge_text = build_knowledge_text(scenario, question, kural_adhigaram, paal=paal)

    knowledge_object = {
        "scenario_id": scenario.get('scenario_id'),
        "image_path": scenario.get('image_path'),
        "scenario": scenario.get('scenario_text'),
        "question": question.get('question_text'),
        "option_a": question.get('option_a'),
        "option_b": question.get('option_b'),
        "option_c": question.get('option_c'),
        "option_d": question.get('option_d'),
        "correct_answer": question.get('correct_option'),
        "explanation": question.get('explanation'),
        "english_kural": scenario.get('english_kural'),
        "concept": scenario.get('concept_name'),
        "adhigaram": kural_adhigaram.get('adhigaram'),
        "paal": paal,
        "knowledge_text": knowledge_text
    }

    return knowledge_object

def build_all_knowledge_objects() -> List[Dict[str, Any]]:
    """Build knowledge objects for all scenarios.

    Returns:
        A list of knowledge object dictionaries.
    """
    logger.info("Loading scenarios...")
    scenarios = load_all_scenarios()
    logger.info(f"Loaded {len(scenarios)} scenarios")

    logger.info("Loading questions...")
    questions = load_all_questions()
    logger.info(f"Loaded {len(questions)} questions")

    logger.info("Loading kurals (for adhigaram)...")
    kurals = load_all_kurals()
    logger.info(f"Loaded {len(kurals)} kurals")

    # Create a map from scenario_id to question (assuming one question per scenario)
    question_map = {}
    for q in questions:
        scenario_id = q.get('scenario_id')
        if scenario_id in question_map:
            logger.warning(f"Duplicate question found for scenario_id: {scenario_id}. Using the first one.")
        else:
            question_map[scenario_id] = q

    # Create a map from kural_id to kural data (for adhigaram)
    kural_map = {}
    for k in kurals:
        kural_id = k.get('kural_id')
        if kural_id in kural_map:
            logger.warning(f"Duplicate kural found for kural_id: {kural_id}. Using the first one.")
        else:
            kural_map[kural_id] = k

    knowledge_objects = []
    skipped_count = 0
    missing_question_count = 0
    missing_kural_count = 0
    missing_scenario_field_count = 0
    missing_paal_count = 0

    # Define required fields from scenario data (after joining)
    # Note: paal_name is not required because we compute it from adhigaram_id
    required_scenario_fields = [
        'scenario_id', 'image_path', 'scenario_text', 'english_kural',
        'concept_name'
    ]

    # Helper function to compute paal from adhigaram_id
    def get_paal_from_adhigaram(adhigaram_id: int) -> str:
        if adhigaram_id is None:
            return None
        if 1 <= adhigaram_id <= 38:
            return 'Aram'
        elif 39 <= adhigaram_id <= 108:
            return 'Porul'
        elif 109 <= adhigaram_id <= 133:
            return 'Inbam'
        else:
            return None

    for scenario in scenarios:
        scenario_id = scenario.get('scenario_id')
        kural_id = scenario.get('kural_id')

        # Check for missing scenario fields
        missing_fields = [f for f in required_scenario_fields if scenario.get(f) is None]
        if missing_fields:
            logger.warning(f"Scenario {scenario_id} missing required fields: {missing_fields}")
            missing_scenario_field_count += 1
            skipped_count += 1
            continue

        # Get question for this scenario
        question = question_map.get(scenario_id)
        if question is None:
            logger.warning(f"No question found for scenario_id: {scenario_id}")
            missing_question_count += 1
            skipped_count += 1
            continue

        # Get kural data for this scenario's kural_id
        kural_adhigaram = kural_map.get(kural_id)
        if kural_adhigaram is None:
            logger.warning(f"No kural data found for kural_id: {kural_id} (from scenario_id: {scenario_id})")
            missing_kural_count += 1
            skipped_count += 1
            continue

        # Compute paal from kural's adhigaram_id
        adhigaram_id = kural_adhigaram.get('adhigaram_id')
        computed_paal = get_paal_from_adhigaram(adhigaram_id)
        if computed_paal is None:
            logger.warning(f"Could not compute paal for adhigaram_id: {adhigaram_id} (from scenario_id: {scenario_id})")
            missing_paal_count += 1
            # We still continue to build the knowledge object, but paal will be None

        # Build the knowledge object
        try:
            knowledge_obj = build_knowledge_object(scenario, question, kural_adhigaram, paal=computed_paal)
            knowledge_objects.append(knowledge_obj)
        except Exception as e:
            logger.error(f"Failed to build knowledge object for scenario_id: {scenario_id}: {e}")
            skipped_count += 1
            continue

    logger.info(f"Built {len(knowledge_objects)} knowledge objects")
    if skipped_count > 0:
        logger.info(f"Skipped {skipped_count} scenarios: "
                    f"{missing_scenario_field_count} missing scenario fields, "
                    f"{missing_question_count} missing questions, {missing_kural_count} missing kurals")
    if missing_paal_count > 0:
        logger.info(f"Could not compute paal for {missing_paal_count} scenarios (adhigaram_id out of range or None)")

    return knowledge_objects

def save_knowledge_objects(knowledge_objects: List[Dict[str, Any]],
                           filepath: Path) -> None:
    """Save knowledge objects to a JSON file.

    Args:
        knowledge_objects: List of knowledge object dictionaries.
        filepath: Path to the JSON file.
    """
    # Ensure the directory exists
    filepath.parent.mkdir(exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(knowledge_objects, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(knowledge_objects)} knowledge objects to {filepath}")

def validate_knowledge_objects(knowledge_objects: List[Dict[str, Any]]) -> bool:
    """Validate the knowledge objects.

    Args:
        knowledge_objects: List of knowledge object dictionaries.

    Returns:
        True if validation passes, False otherwise.
    """
    if not knowledge_objects:
        logger.error("No knowledge objects to validate")
        return False

    # Check for duplicate scenario_ids
    scenario_ids = [obj.get('scenario_id') for obj in knowledge_objects]
    unique_scenario_ids = set(scenario_ids)
    if len(scenario_ids) != len(unique_scenario_ids):
        logger.error(f"Duplicate scenario_ids found! Total: {len(scenario_ids)}, Unique: {len(unique_scenario_ids)}")
        return False
    else:
        logger.info("All scenario_ids are unique.")

    # Check that all required fields are present and non-empty (where expected)
    required_fields = [
        'scenario_id', 'image_path', 'scenario', 'question',
        'option_a', 'option_b', 'option_c', 'option_d',
        'correct_answer', 'explanation', 'english_kural',
        'concept', 'adhigaram', 'paal', 'knowledge_text'
    ]

    missing_fields_count = 0
    empty_knowledge_text_count = 0

    for obj in knowledge_objects:
        for field in required_fields:
            value = obj.get(field)
            if value is None:
                # Allow paal to be None (since we might not be able to compute it from adhigaram_id)
                if field == 'paal':
                    logger.warning(f"Field '{field}' is None in scenario_id: {obj.get('scenario_id')}")
                else:
                    logger.warning(f"Missing field '{field}' in scenario_id: {obj.get('scenario_id')}")
                    missing_fields_count += 1
            elif field == 'knowledge_text' and not isinstance(value, str):
                logger.warning(f"Field 'knowledge_text' is not a string in scenario_id: {obj.get('scenario_id')}")
                missing_fields_count += 1
            elif field == 'knowledge_text' and not value.strip():
                logger.warning(f"Empty knowledge_text for scenario_id: {obj.get('scenario_id')}")
                empty_knowledge_text_count += 1

    if missing_fields_count > 0:
        logger.error(f"Found {missing_fields_count} missing fields in knowledge objects")
        return False

    if empty_knowledge_text_count > 0:
        logger.error(f"Found {empty_knowledge_text_count} empty knowledge texts")
        return False

    # Check that knowledge_text is not empty after preprocessing
    for obj in knowledge_objects:
        knowledge_text = obj.get('knowledge_text', '')
        if not knowledge_text.strip():
            logger.error(f"Knowledge text is empty or only whitespace for scenario_id: {obj.get('scenario_id')}")
            return False

    logger.info("All knowledge objects have required fields and non-empty knowledge text")
    return True

def main():
    """Main function to construct knowledge representations."""
    logger.info("=" * 60)
    logger.info("THIRUKKURAL SCENARIO-BASED DECISION-MAKING")
    logger.info("KNOWLEDGE REPRESENTATION CONSTRUCTION - PHASE 2.5")
    logger.info("=" * 60)

    start_time = time.time()

    # Build all knowledge objects
    knowledge_objects = build_all_knowledge_objects()

    # Validate knowledge objects
    is_valid = validate_knowledge_objects(knowledge_objects)
    if not is_valid:
        logger.error("Validation failed for knowledge objects")
        # We still save them for inspection, but note the validation failure

    # Save knowledge objects to dataset/knowledge_objects.json
    output_path = DATASET_DIR / "knowledge_objects.json"
    save_knowledge_objects(knowledge_objects, output_path)

    # Summary
    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info("=" * 60)
    logger.info("KNOWLEDGE REPRESENTATION CONSTRUCTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Knowledge Objects Created: {len(knowledge_objects)}")
    logger.info(f"Validation Passed: {is_valid}")
    logger.info(f"Time taken: {elapsed_time:.2f} seconds")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()