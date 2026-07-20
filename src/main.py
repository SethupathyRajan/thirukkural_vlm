import pandas as pd
import os
from pathlib import Path
import sys

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import *
from src.database import (
    create_connection, 
    create_tables, 
    validate_and_insert_paal,
    validate_and_insert_concept,
    validate_and_insert_kural,
    validate_and_insert_scenario,
    validate_and_insert_question,
    get_table_counts
)

def load_and_validate_data():
    """Load all data files."""
    print("Loading data files...")
    
    # Load CSV files
    kural_df = pd.read_csv(KURAL_CSV)
    concepts_df = pd.read_csv(CONCEPTS_CSV)
    image_desc_df = pd.read_csv(IMAGE_DESCRIPTION_CSV)
    
    # Load Excel files
    concept_map_df = pd.read_excel(CONCEPT_KURAL_MAP_XLSX)
    questions_df = pd.read_excel(QUESTIONS_XLSX)
    scenario_df = pd.read_excel(SCENARIO_XLSX)
    
    print(f"Loaded {len(kural_df)} kural records")
    print(f"Loaded {len(concepts_df)} concept records")
    print(f"Loaded {len(image_desc_df)} image description records")
    print(f"Loaded {len(questions_df)} question records")
    print(f"Loaded {len(scenario_df)} scenario records")
    
    return kural_df, concepts_df, image_desc_df, concept_map_df, questions_df, scenario_df

def validate_data(kural_df, concepts_df, image_desc_df, concept_map_df, questions_df, scenario_df):
    """Perform validation checks and return validation results."""
    validation_stats = {
        'scenarios_with_questions': 0,
        'scenarios_without_questions': 0,
        'missing_images': 0,
        'missing_image_descriptions': 0,
        'invalid_question_options': 0,
        'kurals_without_concept': 0
    }
    
    # Check for scenarios without questions
    scenario_ids = set(scenario_df['Scenario_ID'])
    question_scenario_ids = set(questions_df['Scenario_ID'])
    validation_stats['scenarios_without_questions'] = len(scenario_ids - question_scenario_ids)
    validation_stats['scenarios_with_questions'] = len(scenario_ids & question_scenario_ids)
    
    # Check for missing images
    missing_images = []
    for scenario_id in scenario_df['Scenario_ID']:
        image_path = f"dataset/images/{scenario_id}.jpg"
        if not os.path.exists(image_path):
            missing_images.append(scenario_id)
    validation_stats['missing_images'] = len(missing_images)
    
    # Check for missing image descriptions
    desc_scenario_ids = set(image_desc_df['Scenario_ID'])
    missing_desc = scenario_ids - desc_scenario_ids
    validation_stats['missing_image_descriptions'] = len(missing_desc)
    
    # Check for invalid question options
    valid_options = ['A', 'B', 'C', 'D']
    invalid_options = questions_df[~questions_df['Correct_Option'].isin(valid_options)]
    validation_stats['invalid_question_options'] = len(invalid_options)
    
    # Check for kurals without concept mapping
    mapped_kurals = set(concept_map_df['Kural_ID'])
    all_kurals = set(kural_df['Kural_Number'])
    validation_stats['kurals_without_concept'] = len(all_kurals - mapped_kurals)
    
    return validation_stats

def main():
    """Main function to orchestrate the dataset unification process."""
    print("=" * 60)
    print("THIRUKKURAL SCENARIO-BASED DECISION-MAKING")
    print("DATASET UNIFICATION - PHASE 2.1")
    print("=" * 60)
    
    try:
        # Ensure database directory exists
        DATABASE_DIR.mkdir(exist_ok=True)
        
        # Remove existing database file for clean start
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
            print(f"Removed existing database: {DATABASE_PATH}")
        
        # Load data
        kural_df, concepts_df, image_desc_df, concept_map_df, questions_df, scenario_df = load_and_validate_data()
        
        # Validate data and get stats
        validation_stats = validate_data(kural_df, concepts_df, image_desc_df, concept_map_df, questions_df, scenario_df)
        
        # Create database connection
        print("\nCreating database connection...")
        conn = create_connection()
        
        # Create tables
        print("Creating database tables...")
        create_tables(conn)
        
        # Insert data in dependency order
        print("\nInserting data...")
        
        # 1. Paal (from concepts data)
        paal_count = validate_and_insert_paal(conn, concepts_df)
        
        # 2. Concepts
        concept_count = validate_and_insert_concept(conn, concepts_df)
        
        # 3. Kurals (with concept mapping)
        kural_count = validate_and_insert_kural(conn, kural_df, concept_map_df)
        
        # 4. Scenarios (with image data)
        scenario_count = validate_and_insert_scenario(conn, scenario_df, kural_df, image_desc_df)
        
        # 5. Questions
        question_count = validate_and_insert_question(conn, questions_df, scenario_df, kural_df)
        
        # Get final counts
        counts = get_table_counts(conn)
        
        # Close connection
        conn.close()
        
        # Print summary
        print("\n" + "=" * 60)
        print("DATASET UNIFICATION COMPLETE")
        print("=" * 60)
        print(f"Database created: {DATABASE_PATH}")
        print("\nRecord counts:")
        print(f"  Paal (Sections)     : {counts.get('paal', 0)}")
        print(f"  Concepts            : {counts.get('concept', 0)}")
        print(f"  Kurals              : {counts.get('kural', 0)}")
        print(f"  Scenarios           : {counts.get('scenario', 0)}")
        print(f"  Questions           : {counts.get('question', 0)}")
        
        print("\nValidation Summary:")
        print(f"  Scenarios with questions      : {validation_stats['scenarios_with_questions']}")
        print(f"  Scenarios without questions   : {validation_stats['scenarios_without_questions']}")
        print(f"  Missing image files           : {validation_stats['missing_images']}")
        print(f"  Missing image descriptions    : {validation_stats['missing_image_descriptions']}")
        print(f"  Invalid question options      : {validation_stats['invalid_question_options']}")
        print(f"  Kurals without concept map    : {validation_stats['kurals_without_concept']}")
        
        total_errors = (
            validation_stats['missing_images'] +
            validation_stats['missing_image_descriptions'] +
            validation_stats['invalid_question_options'] +
            validation_stats['kurals_without_concept']
        )
        
        if total_errors == 0:
            print("\n✓ All validations passed - no critical errors found")
        else:
            print(f"\n⚠  {total_errors} validation issues found (see details above)")
            print("  Note: Processing continued despite these issues as per requirements")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()
