import pandas as pd
concept_map = pd.read_excel('dataset/concept_kural_map.xlsx')

# Check if each Kural_ID maps to exactly one Concept_ID
kural_counts = concept_map.groupby('Kural_ID')['Concept_ID'].nunique()
multi_mapped = kural_counts[kural_counts > 1]
print(f'Number of Kurals mapping to multiple Concepts: {len(multi_mapped)}')
if len(multi_mapped) > 0:
    print('Examples of multi-mapped Kurals:')
    print(multi_mapped.head())
else:
    print('All Kurals map to exactly one Concept - good!')
