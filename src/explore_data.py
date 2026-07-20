import pandas as pd
import os

def explore_file(filepath):
    print(f"\n=== {filepath} ===")
    if not os.path.exists(filepath):
        print("File not found!")
        return None
    
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            print("Unsupported format")
            return None
            
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Check for nulls
        null_counts = df.isnull().sum()
        if null_counts.any():
            print("\nNull counts:")
            print(null_counts[null_counts > 0])
        
        # Check for duplicates in key columns
        if 'Scenario_ID' in df.columns:
            dup_scenario = df['Scenario_ID'].duplicated().sum()
            print(f"Duplicate Scenario_IDs: {dup_scenario}")
        if 'Question_ID' in df.columns:
            dup_question = df['Question_ID'].duplicated().sum()
            print(f"Duplicate Question_IDs: {dup_question}")
        if 'Kural_ID' in df.columns:
            dup_kural = df['Kural_ID'].duplicated().sum()
            print(f"Duplicate Kural_IDs: {dup_kural}")
        if 'Concept_ID' in df.columns:
            dup_concept = df['Concept_ID'].duplicated().sum()
            print(f"Duplicate Concept_IDs: {dup_concept}")
            
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

# Explore all files
files = [
    'dataset/concept_kural_map.xlsx',
    'dataset/concepts.csv',
    'dataset/image_description.csv',
    'dataset/kural.csv',
    'dataset/questions.xlsx',
    'dataset/scenario.xlsx'
]

dataframes = {}
for f in files:
    dataframes[f] = explore_file(f)

# Check image directory
print("\n=== Dataset Images ===")
image_dir = 'dataset/images'
if os.path.exists(image_dir):
    images = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    print(f"Found {len(images)} JPG images")
    if images:
        print(f"Sample images: {sorted(images)[:5]}")
else:
    print("Image directory not found")

# Check for missing images based on Scenario_ID
if 'dataset/image_description.csv' in dataframes and dataframes['dataset/image_description.csv'] is not None:
    img_desc_df = dataframes['dataset/image_description.csv']
    scenario_ids = set(img_desc_df['Scenario_ID'].astype(str).str.strip())
    print(f"\nUnique Scenario_IDs from image_description: {len(scenario_ids)}")
    
    # Check which scenarios have images
    missing_images = []
    for sid in scenario_ids:
        img_path = os.path.join(image_dir, f"{image_dir}", f"{sid}.jpg")
        if not os.path.exists(img_path):
            missing_images.append(sid)
    
    print(f"Scenarios missing images: {len(missing_images)}")
    if missing_images:
        print(f"First 10 missing: {missing_images[:10]}")
