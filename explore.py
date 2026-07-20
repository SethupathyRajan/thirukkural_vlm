import pandas as pd
import os

print("Exploring dataset files...")

# List of files
files = [
    'dataset/concept_kural_map.xlsx',
    'dataset/concepts.csv',
    'dataset/image_description.csv',
    'dataset/kural.csv',
    'dataset/questions.xlsx',
    'dataset/scenario.xlsx'
]

for f in files:
    print(f"\n--- {f} ---")
    if not os.path.exists(f):
        print("File not found!")
        continue
    try:
        if f.endswith('.csv'):
            df = pd.read_csv(f)
        else:
            df = pd.read_excel(f)
        print(f"Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print("First 2 rows:")
        print(df.head(2))
    except Exception as e:
        print(f"Error reading {f}: {e}")
