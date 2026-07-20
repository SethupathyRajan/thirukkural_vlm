import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import *

# Load data
print("Loading data...")
questions_df = pd.read_excel(QUESTIONS_XLSX)
scenario_df = pd.read_excel(SCENARIO_XLSX)
kural_df = pd.read_csv(KURAL_CSV)

print(f"Questions: {len(questions_df)}")
print(f"Scenarios: {len(scenario_df)}")
print(f"Kurals: {len(kural_df)}")

# Check unique IDs
q_scenario_ids = set(questions_df['Scenario_ID'])
s_scenario_ids = set(scenario_df['Scenario_ID'])
q_kural_ids = set(questions_df['Kural_ID'])
k_kural_ids = set(kural_df['Kural_Number'])

print(f"\nUnique scenario IDs in questions: {len(q_scenario_ids)}")
print(f"Unique scenario IDs in scenarios: {len(s_scenario_ids)}")
print(f"Unique kural IDs in questions: {len(q_kural_ids)}")
print(f"Unique kural IDs in kurals: {len(k_kural_ids)}")

# Find missing references
missing_scenarios = q_scenario_ids - s_scenario_ids
missing_kurals = q_kural_ids - k_kural_ids

print(f"\nQuestions referencing non-existent scenarios: {len(missing_scenarios)}")
if missing_scenarios:
    print(f"  Examples: {list(missing_scenarios)[:5]}")

print(f"Questions referencing non-existent kurals: {len(missing_kurals)}")
if missing_kurals:
    print(f"  Examples: {list(missing_kurals)[:5]}")

# Show a few questions with problematic IDs
if missing_scenarios:
    print("\nSample questions with missing scenario refs:")
    bad_questions = questions_df[questions_df['Scenario_ID'].isin(list(missing_scenarios)[:3])]
    print(bad_questions[['Question_ID', 'Scenario_ID', 'Kural_ID']].head())

if missing_kurals:
    print("\nSample questions with missing kural refs:")
    bad_questions = questions_df[questions_df['Kural_ID'].isin(list(missing_kurals)[:3])]
    print(bad_questions[['Question_ID', 'Scenario_ID', 'Kural_ID']].head())
