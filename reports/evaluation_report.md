# Thirukkural Scenario-Based Decision-Making System
## Evaluation Report - Phase 2.8

## Dataset Size
- Number of Images: N/A
- Number of Knowledge Objects: N/A
- Embedding Dimension: N/A

## Overall Accuracy (Indexed Dataset Baseline)
- Top-1 Accuracy: 100.00%
- Top-3 Accuracy: 100.00%
- Top-5 Accuracy: 100.00%
- MRR: 1.0000

## Best Fusion Weight (from Study)
- Image Weight: 1.0
- Knowledge Weight: 0.0
- Top-1 Accuracy: 1.0000

## Ablation Study
- No results available.

## Failure Analysis
- No failures found (all queries retrieved correct item at rank 1).

## Runtime Performance
- No results available.

## Memory Usage
- Image Embeddings: 568.00 KB
- Image IDs: 14.81 KB
- Knowledge Embeddings: 424.50 KB
- Knowledge IDs: 14.76 KB
- Knowledge Objects: 130.70 KB
- Number of Images: 284
- Number of Knowledge Objects: 283
- Embedding Dimension: 512

## Notes
- The evaluation was performed on the indexed dataset (training set performance).
- Unseen image evaluation will be performed in Phase 2.9.
- One image (S102) lacks a corresponding knowledge object; this is handled gracefully by setting knowledge similarity to zero.
- All experiments used deterministic ordering and fixed configuration.
- The retrieval algorithm was not modified; only configuration weights were varied where applicable.
