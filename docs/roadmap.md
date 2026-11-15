# Limitations and future work

## Current limitations

1. The prototype is topography-only and cannot support a complete geological or astrobiological analog claim.
2. MOLA is a 16 pixels/degree product, while NASADEM is approximately 30 m. The workflow harmonizes feature descriptors but does not create new physical information.
3. The prototype confidence score is not calibrated and has no withheld expert labels.
4. Source lineage is documented at product level but requires a formal dependency graph when CRISM, THEMIS, Landsat, Sentinel-2, and rover products are added.
5. The current spatial cells are non-overlapping in the first implementation; overlapping tiles and halo features are planned for the next version.
6. No causal interpretation is inferred from statistical similarity.

## Next experiments

- Add independent terrain checks with ICESat-2 where spatial intersections are available.
- Add CRISM/THEMIS/HiRISE/CTX and Landsat/Sentinel-2 features with instrument-aware spectral response handling.
- Compare direct weighted similarity, KNN, spatial graph baselines, and the inferential-node architecture.
- Perform missing-data, noise, calibration, cell-size, overlap, and withheld-site sensitivity tests.
- Calibrate confidence with independent labels and report Precision@K, Recall@K, NDCG, Brier score where labels are defensible, calibration error, evidence traceability, and computational cost.
- Implement persistent versioned knowledge storage and incremental updates.
- Add a human-review report containing supporting evidence, contradicting evidence, data lineage, uncertainty, and the decision trace for every candidate.
- Investigate distributed or quantum-assisted optimization only for a clearly defined subproblem and only against strong classical baselines.
