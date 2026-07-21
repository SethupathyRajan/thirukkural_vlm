# Retrieval Engine Report

## Overview
This document describes the multimodal retrieval engine (Baseline) for Phase 2.7 of the Thirukkural Scenario-Based Decision-Making project. The engine combines visual similarity (via OpenCLIP) and semantic similarity (via Sentence-BERT) to retrieve relevant Thirukkural scenarios given a query image.

## Retrieval Architecture
The retrieval pipeline follows a two-stage process:
1. **Visual Retrieval**: Compute image similarity between the query image and all indexed images using cosine similarity on OpenCLIP embeddings.
2. **Semantic Re-ranking**: Use the top visual match to retrieve its associated knowledge embedding, then compute knowledge similarity between this reference and all candidate knowledge embeddings. Finally, fuse the visual and knowledge similarity scores using a weighted sum.

This design decouples the visual and semantic components, allowing each to be optimized independently. The visual stage provides an initial candidate set, while the semantic stage refines the ranking based on textual knowledge alignment.

## Embedding Sources
- **Image Embeddings**: Precomputed using OpenCLIP ViT-B-32 model (laion2b_s34b_b79k) on the dataset images. Stored in `embeddings/image_embeddings.npy`.
- **Knowledge Embeddings**: Precomputed using Sentence-BERT (`sentence-transformers/all-MiniLM-L6-v2`) on the `knowledge_text` field of each knowledge object. Stored in `embeddings/knowledge_embeddings.npy`.
- **ID Mapping**: 
  - Image IDs: `embeddings/image_embedding_ids.npy` (284 entries)
  - Knowledge IDs: `embeddings/knowledge_embedding_ids.npy` (283 entries)
  - Knowledge Objects: `dataset/knowledge_objects.json` (283 entries)

*Note*: There is a known mismatch: one image (S102.jpg) lacks a corresponding knowledge object. This is handled gracefully by setting knowledge similarity to zero when the knowledge embedding is missing.

## Score Fusion Formula
The final similarity score is a weighted linear combination:
```
Final Score = (Image Weight × Image Similarity) + (Knowledge Weight × Knowledge Similarity)
```
where:
- `Image Similarity`: Cosine similarity between query image embedding and candidate image embedding.
- `Knowledge Similarity`: Cosine similarity between the knowledge embedding of the top visual match and the knowledge embedding of each candidate.
- `Image Weight` and `Knowledge Weight`: Configurable parameters summing to 1.0 (default: 0.7 and 0.3).

This formulation ensures that both modalities contribute to the final ranking, with weights reflecting their relative importance.

## Configuration Parameters
All retrieval parameters are configurable via `config/config.py`:
- `RETRIEVAL_TOP_K` (int): Number of top candidates to retrieve (default: 10)
- `IMAGE_WEIGHT` (float): Weight for image similarity in fusion (default: 0.7)
- `KNOWLEDGE_WEIGHT` (float): Weight for knowledge similarity in fusion (default: 0.3)
- `LOG_LEVEL` (str): Logging level (default: "INFO"; set to "DEBUG" for verbose output)
- `DEVICE` (str): Computation device (`cuda`, `cpu`, or `mps`; auto-detected)
- `BATCH_SIZE` (int): Batch size for embedding generation (used in other phases)
- `IMAGE_SIZE` (int): Input image size for the OpenCLIP model (default: 224)

No retrieval parameters are hardcoded; all are sourced from the configuration system.

## Pipeline Flow
1. **Load Embeddings and Knowledge Objects**: 
   - Load precomputed image embeddings and IDs.
   - Load precomputed knowledge embeddings and IDs.
   - Load knowledge objects from JSON.
2. **Encode Query Image**: 
   - Load and preprocess the query image using the OpenCLIP preprocessing function.
   - Encode the image to obtain a 512-dimensional embedding (L2-normalized).
3. **Compute Visual Similarity**: 
   - Calculate cosine similarity between the query embedding and all image embeddings.
   - Select the top-K candidates based on visual similarity.
4. **Compute Knowledge Similarity**: 
   - Retrieve the knowledge embedding of the top visual candidate.
   - Compute cosine similarity between this reference and all candidate knowledge embeddings.
   - If the knowledge embedding for the top candidate is missing, set all knowledge similarities to zero.
5. **Fuse Scores**: 
   - Combine visual and knowledge similarity scores using the weighted sum formula.
6. **Re-rank Candidates**: 
   - Sort candidates by the combined score in descending order.
7. **Attach Knowledge Objects**: 
   - Enrich each result with its corresponding knowledge object (if available).
8. **Return Results**: 
   - Return the ranked list of candidates with scores and associated knowledge objects.

## Validation Results
The retrieval engine was evaluated on the indexed dataset (284 images) using leave-one-out evaluation (each image serves as a query once). Results:

- **Top-1 Accuracy**: 100.00% (284/284 correct)
- **Top-3 Accuracy**: 100.00%
- **Top-5 Accuracy**: 100.00%

**Example Query (S001.jpg)**:
```
Rank 1: S001 | Image Sim: 1.0000 | Knowledge Sim: 1.0000 | Combined: 1.0000 
        Scenario: Student practicing Tamil letter 'அ' on slate before school...
Rank 2: S004 | Image Sim: 0.7987 | Knowledge Sim: 0.4047 | Combined: 0.6805
Rank 3: S065 | Image Sim: 0.7324 | Knowledge Sim: 0.4718 | Combined: 0.6542
```

## Error Handling Summary
The system gracefully handles various error conditions:
- **Invalid Image Path**: Returns empty result list and logs error.
- **Unsupported Image Format**: Returns empty result list and logs error.
- **Corrupted Image**: Returns empty result list and logs error.
- **Missing Embedding File**: Propagates `FileNotFoundError` (caught by calling code).
- **Missing Knowledge Object**: Sets knowledge similarity to zero for all candidates and logs warning.
- **Inconsistent IDs**: Logs warnings when knowledge embeddings are missing for specific candidates; processing continues with zero similarity for those cases.

All errors are logged with contextual information to aid debugging.

## Limitations
1. **Dataset-Dependent Evaluation**: The reported 100% accuracy is based on the indexed dataset (training set performance). Performance on unseen images will be evaluated in Phase 2.8.
2. **Brute-Force Similarity Search**: The current implementation uses exhaustive linear scan for similarity search, which is O(N) in the dataset size. For larger datasets, approximate nearest neighbor (ANN) libraries (e.g., FAISS) would be more efficient, but are intentionally omitted in this baseline to ensure simplicity and reproducibility.
3. **Single-Knowledge Reference**: Knowledge similarity is computed using only the top visual candidate's knowledge embedding as a reference. Alternative strategies (e.g., averaging multiple candidates) were explored but not adopted in this baseline.
4. **Modality Weighting**: The fixed weighting scheme may not be optimal for all queries; adaptive weighting could be explored in future work.
5. **Missing Knowledge Data**: As noted, one image (S102) lacks a corresponding knowledge object. While handled gracefully, this represents a data gap that should be addressed in future data collection cycles.

## Conclusion
The multimodal retrieval engine successfully integrates visual and semantic information to retrieve relevant Thirukkural scenarios. Its modular design, configurable parameters, and robust error handling make it suitable for further experimentation and extension in subsequent phases.