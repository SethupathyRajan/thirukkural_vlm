import sqlite3
import pandas as pd
from pathlib import Path
from config.config import DATABASE_PATH

def create_connection():
   """Create a database connection."""
   conn = sqlite3.connect(DATABASE_PATH)
   # Enable foreign key constraints
   conn.execute("PRAGMA foreign_keys = ON")
   return conn

def create_tables(conn):
   """Create database tables."""
   cursor = conn.cursor()
   
   # Drop tables if they exist (for clean rebuild)
   cursor.execute("DROP TABLE IF EXISTS question")
   cursor.execute("DROP TABLE IF EXISTS scenario")
   cursor.execute("DROP TABLE IF EXISTS kural")
   cursor.execute("DROP TABLE IF EXISTS concept")
   cursor.execute("DROP TABLE IF EXISTS paal")
   
   # Create paal table
   cursor.execute("""
       CREATE TABLE paal (
           paal_id VARCHAR(20) PRIMARY KEY,
           paal_name VARCHAR(100),
           description TEXT
       )
   """)
   
   # Create concept table
   cursor.execute("""
       CREATE TABLE concept (
           concept_id VARCHAR(10) PRIMARY KEY,
           concept_name VARCHAR(100),
           description TEXT,
           paal_id VARCHAR(20),
           FOREIGN KEY (paal_id) REFERENCES paal(paal_id)
       )
   """)
   
   # Create kural table
   cursor.execute("""
       CREATE TABLE kural (
           kural_id INTEGER PRIMARY KEY,
           tamil_kural TEXT,
           transliteration TEXT,
           english_kural TEXT,
           vilakam TEXT,
           adhigaram_id INTEGER,
           adhigaram VARCHAR(20),
           concept_id VARCHAR(10),
           FOREIGN KEY (concept_id) REFERENCES concept(concept_id)
       )
   """)
   
   # Create scenario table
   cursor.execute("""
       CREATE TABLE scenario (
           scenario_id VARCHAR(10) PRIMARY KEY,
           scenario_text TEXT,
           difficulty VARCHAR(20),
           image_path VARCHAR(255),
           image_description TEXT,
           kural_id INTEGER,
           FOREIGN KEY (kural_id) REFERENCES kural(kural_id)
       )
   """)
   
   # Create question table
   cursor.execute("""
       CREATE TABLE question (
           question_id VARCHAR(10) PRIMARY KEY,
           scenario_id VARCHAR(10),
           kural_id INTEGER,
           question_text TEXT,
           option_a TEXT,
           option_b TEXT,
           option_c TEXT,
           option_d TEXT,
           correct_option VARCHAR(1),
           explanation TEXT,
           FOREIGN KEY (scenario_id) REFERENCES scenario(scenario_id),
           FOREIGN KEY (kural_id) REFERENCES kural(kural_id)
       )
   """)
   
   # Create indexes for better query performance
   cursor.execute("CREATE INDEX idx_scenario_kural ON scenario(kural_id)")
   cursor.execute("CREATE INDEX idx_question_scenario ON question(scenario_id)")
   cursor.execute("CREATE INDEX idx_question_kural ON question(kural_id)")
   cursor.execute("CREATE INDEX idx_kural_concept ON kural(concept_id)")
   cursor.execute("CREATE INDEX idx_concept_paal ON concept(paal_id)")
   
   conn.commit()

def validate_and_insert_paal(conn, df):
   """Validate and insert paal (division) data."""
   cursor = conn.cursor()
   
   # Get unique paal values from concepts
   paal_data = df[['Division']].drop_duplicates()
   paal_data.columns = ['paal_id']
   
   # Add descriptive names
   paal_descriptions = {
       'Aram': 'Virtue - Ethical and moral principles',
       'Porul': 'Wealth - Governance and society',
       'Inbam': 'Love - Personal and romantic relationships'
   }
   
   paal_data['paal_name'] = paal_data['paal_id'].map(paal_descriptions)
   paal_data['description'] = paal_data['paal_id'].map(paal_descriptions)  # Same for now
   
   # Insert data
   paal_data.to_sql('paal', conn, if_exists='append', index=False)
   print(f"Inserted {len(paal_data)} paal records")
   return len(paal_data)

def validate_and_insert_concept(conn, df):
   """Validate and insert concept data."""
   cursor = conn.cursor()
   
   # Ensure required columns exist
   required_columns = ['Concept_ID', 'Concept', 'Description']
   for col in required_columns:
       if col not in df.columns:
           raise ValueError(f"Missing required column: {col}")
   
   # Rename columns to match schema
   concept_df = df.copy()
   concept_df = concept_df.rename(columns={
       'Concept_ID': 'concept_id',
       'Concept': 'concept_name',
       'Description': 'description'
   })
   
   # Keep only required columns
   concept_df = concept_df[['concept_id', 'concept_name', 'description']]
   
   # Remove duplicates
   concept_df = concept_df.drop_duplicates(subset=['concept_id'])
   
   # Insert data
   concept_df.to_sql('concept', conn, if_exists='append', index=False)
   print(f"Inserted {len(concept_df)} concept records")
   return len(concept_df)

def validate_and_insert_kural(conn, kural_df, concept_map_df):
   """Validate and insert kural data."""
   cursor = conn.cursor()
   
   # Ensure required columns exist
   required_columns = ['Kural_Number', 'Tamil_Verse', 'Transliteration', 'Couplet', 'Vilakam']
   for col in required_columns:
       if col not in kural_df.columns:
           raise ValueError(f"Missing required column in kural data: {col}")
   
   # Rename columns
   kural_df = kural_df.rename(columns={
       'Kural_Number': 'kural_id',
       'Tamil_Verse': 'tamil_kural',
       'Transliteration': 'transliteration',
       'Couplet': 'english_kural',
       'Vilakam': 'vilakam'
   })
   
   # Calculate adhigaram (chapter) - each chapter has 10 kurals
   # Kurals 1-10 -> chapter 1, 11-20 -> chapter 2, etc.
   kural_df['adhigaram_id'] = ((kural_df['kural_id'] - 1) // 10) + 1
   kural_df['adhigaram'] = kural_df['adhigaram_id'].apply(lambda x: f"Chapter {x}")
   
   # Merge with concept mapping to get concept_id for each kural
   concept_map_df = concept_map_df.rename(columns={
       'Kural_ID': 'kural_id',
       'Concept_ID': 'concept_id'
   })
   
   kural_with_concept = kural_df.merge(
       concept_map_df[['kural_id', 'concept_id']], 
       on='kural_id', 
       how='left'
   )
   
   # Check for any kurals without concept mapping
   missing_concept = kural_with_concept[kural_with_concept['concept_id'].isna()]
   if len(missing_concept) > 0:
       print(f"Warning: {len(missing_concept)} kurals have no concept mapping")
       # We'll still insert them but they'll have NULL concept_id
       # In a production system, we might want to handle this differently
   
   # Keep only required columns for kural table
   kural_final = kural_with_concept[['kural_id', 'tamil_kural', 'transliteration', 
                                     'english_kural', 'vilakam', 'adhigaram_id', 
                                     'adhigaram', 'concept_id']]
   
   # Insert data (allowing NULL concept_id for now)
   kural_final.to_sql('kural', conn, if_exists='append', index=False)
   print(f"Inserted {len(kural_final)} kural records")
   if len(missing_concept) > 0:
       print(f"Note: {len(missing_concept)} kurals inserted with null concept_id")
   return len(kural_final)

def validate_and_insert_scenario(conn, scenario_df, kural_df, image_desc_df):
    """Validate and insert scenario data."""
    cursor = conn.cursor()

    # Ensure required columns exist
    required_columns = ['Scenario_ID', 'Kural_ID', 'Scenario', 'Difficulty']
    for col in required_columns:
        if col not in scenario_df.columns:
            raise ValueError(f"Missing required column in scenario data: {col}")

    # Create a copy to work with
    scenario_df = scenario_df.copy()

    # Rename columns
    scenario_df = scenario_df.rename(columns={
        'Scenario_ID': 'scenario_id',
        'Kural_ID': 'kural_id',
        'Scenario': 'scenario_text',
        'Difficulty': 'difficulty'
    })

    # Add image path and description
    # Image path: dataset/images/{scenario_id}.jpg
    scenario_df['image_path'] = scenario_df['scenario_id'].apply(
        lambda x: f"dataset/images/{x}.jpg"
    )

    # Merge with image descriptions
    image_df_renamed = image_desc_df.rename(columns={
        'Scenario_ID': 'scenario_id',
        'Image_Description': 'image_description'
    })

    scenario_with_image = scenario_df.merge(
        image_df_renamed[['scenario_id', 'image_description']], 
        on='scenario_id', 
        how='left'
    )

    # Check for missing images
    missing_image = []
    for scenario_id in scenario_with_image['scenario_id']:
        image_path = f"dataset/images/{scenario_id}.jpg"
        if not Path(image_path).exists():
            missing_image.append(scenario_id)

    if missing_image:
        print(f"Warning: {len(missing_image)} scenarios have missing image files")

    # Check for missing image descriptions
    missing_desc = scenario_with_image[scenario_with_image['image_description'].isna()]
    if len(missing_desc) > 0:
        print(f"Warning: {len(missing_desc)} scenarios have missing image descriptions")
        # Fill empty descriptions
        scenario_with_image['image_description'] = scenario_with_image['image_description'].fillna("")

    # Validate that kural_id exists in kural data we're about to insert
    # Get the set of kural_ids we're inserting
    valid_kural_ids = set(kural_df['Kural_Number'])
    invalid_kural_mask = ~scenario_with_image['kural_id'].isin(valid_kural_ids)
    invalid_kural_count = invalid_kural_mask.sum()

    if invalid_kural_count > 0:
        print(f"Warning: {invalid_kural_count} scenarios reference non-existent kurals")
        # Filter out invalid rows
        scenario_valid = scenario_with_image[~invalid_kural_mask].copy()
    else:
        scenario_valid = scenario_with_image.copy()

    # Select final columns
    scenario_final = scenario_valid[['scenario_id', 'scenario_text', 'difficulty', 
                                     'image_path', 'image_description', 'kural_id']]

    # Remove duplicates
    scenario_final = scenario_final.drop_duplicates(subset=['scenario_id'])

    # Insert data
    scenario_final.to_sql('scenario', conn, if_exists='append', index=False)
    print(f"Inserted {len(scenario_final)} scenario records")
    if invalid_kural_count > 0:
        print(f"Skipped {invalid_kural_count} scenarios due to invalid kural references")
    if missing_image:
        print(f"Warning: {len(missing_image)} scenarios have missing image files")
    if len(missing_desc) > 0:
        print(f"Warning: {len(missing_desc)} scenarios had missing image descriptions (filled with empty string)")
    return len(scenario_final)

def validate_and_insert_question(conn, questions_df, scenario_df, kural_df):
    """Validate and insert question data with referential integrity checking."""
    cursor = conn.cursor()
    
    # Ensure required columns exist
    required_columns = ['Question_ID', 'Scenario_ID', 'Kural_ID', 'Question', 
                       'Option_A', 'Option_B', 'Option_C', 'Option_D', 
                       'Correct_Option', 'Explanation']
    for col in required_columns:
        if col not in questions_df.columns:
            raise ValueError(f"Missing required column in questions data: {col}")
    
    # Create a copy to work with
    questions_df = questions_df.copy()
    
    # Rename columns
    questions_df = questions_df.rename(columns={
        'Question_ID': 'question_id',
        'Scenario_ID': 'scenario_id',
        'Kural_ID': 'kural_id',
        'Question': 'question_text',
        'Option_A': 'option_a',
        'Option_B': 'option_b',
        'Option_C': 'option_c',
        'Option_D': 'option_d',
        'Correct_Option': 'correct_option',
        'Explanation': 'explanation'
    })
    
    # Validate correct_option values
    valid_options = ['A', 'B', 'C', 'D']
    invalid_options = questions_df[~questions_df['correct_option'].isin(valid_options)]
    invalid_option_count = len(invalid_options)
    
    if invalid_option_count > 0:
        print(f"Warning: {invalid_option_count} questions have invalid correct_option values")
        # We'll still process them but note the issue
    
    # Get sets of valid IDs from the data we're about to insert
    valid_scenario_ids = set(scenario_df['Scenario_ID'])
    valid_kural_ids = set(kural_df['Kural_Number'])
    
    # Check for invalid references
    invalid_scenario_mask = ~questions_df['scenario_id'].isin(valid_scenario_ids)
    invalid_kural_mask = ~questions_df['kural_id'].isin(valid_kural_ids)
    
    invalid_scenario_count = invalid_scenario_mask.sum()
    invalid_kural_count = invalid_kural_mask.sum()
    
    # Filter out rows with invalid references
    valid_mask = ~(invalid_scenario_mask | invalid_kural_mask)
    questions_valid = questions_df[valid_mask].copy()
    
    skipped_count = len(questions_df) - len(questions_valid)
    
    if skipped_count > 0:
        print(f"Skipping {skipped_count} questions due to referential integrity issues:")
        if invalid_scenario_count > 0:
            print(f"  - {invalid_scenario_count} questions reference non-existent scenarios")
        if invalid_kural_count > 0:
            print(f"  - {invalid_kural_count} questions reference non-existent kurals")
    
    # Select final columns
    questions_final = questions_valid[['question_id', 'scenario_id', 'kural_id',
                                       'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
                                       'correct_option', 'explanation']]
    
    # Remove duplicates
    questions_final = questions_final.drop_duplicates(subset=['question_id'])
    
    # Insert data
    questions_final.to_sql('question', conn, if_exists='append', index=False)
    print(f"Inserted {len(questions_final)} question records")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} questions due to invalid references")
    if invalid_option_count > 0:
        print(f"Note: {invalid_option_count} questions had invalid correct_option values (still inserted)")
    return len(questions_final)

def get_table_counts(conn):
    """Get row counts for all tables."""
    cursor = conn.cursor()
    tables = ['paal', 'concept', 'kural', 'scenario', 'question']
    counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    return counts
