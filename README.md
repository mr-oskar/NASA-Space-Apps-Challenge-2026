# Inferential-Node Planetary Analog Discovery

## NASA Space Apps Challenge 2026 — Gale Crater / Atacama prototype

This repository contains a reproducible data-analysis prototype for an **Inferential-Node Algorithm for Planetary Analog Discovery**. The system represents sites, spatial cells, features, observations, data sources, and hypotheses as linked evidence nodes. It then harmonizes heterogeneous elevation products, preserves spatial context, scores candidate Earth cells against a Martian reference region, and records the evidence coverage and uncertainty behind each ranking.

The initial experiment uses:

- **Mars reference:** Gale Crater, represented by the NASA Mars Orbiter Laser Altimeter (MOLA) MEGDR 16 pixels/degree topography product.
- **Earth search domain:** the Atacama Desert, represented by NASADEM HGT v001 COG tiles around Maria Elena South and Yungay.
- **Prototype feature set:** elevation distribution, local slope, slope variability, and data-validity coverage.

The project is intentionally honest about scope: this is a topography-only prototype. It does not claim that a high score proves a complete geological, mineralogical, thermal, or biological analog. Spectral, thermal, geological, and independent validation layers are future extensions.

## Repository layout

```text
data/raw/                 downloaded source products and acquisition metadata
data/processed/           harmonized rasters and normalization summaries
data/reference_region/    cropped Gale and Atacama arrays used by the prototype
data/algorithm_outputs/   candidate cells, target summaries, and rankings
figures/processing/       raw-vs-harmonized QC plots
figures/algorithm/        ranking, confidence, and feature-space plots
notebooks/                Google Colab/Jupyter workflow
src/                      download, processing, and visualization code
docs/                     methods, data dictionary, limitations, and roadmap
references/               citation and provenance files
configs/                  study-region and threshold configuration
```

## Quick start

```bash
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -q numpy\<2 pandas seaborn scipy scikit-learn jupyter nbformat
sudo apt-get install -y python3-rasterio gdal-bin
.venv/bin/python src/download_data.py
.venv/bin/python -c "import sys; sys.path.insert(0, 'src'); from pipeline import run; run()"
.venv/bin/python src/visualize.py
```

Google Colab users can open `notebooks/01_end_to_end_colab.ipynb`. The notebook installs dependencies, acquires the inputs, executes the pipeline, and displays the QC and ranking figures.

## Scientific design

The algorithm separates four quantities that must not be conflated:

1. **Similarity:** how close two feature vectors are after harmonization.
2. **Evidence quality:** how complete and reliable the measurements are.
3. **Evidence independence:** whether multiple products contain duplicated or inherited information.
4. **Confidence score:** a prototype ranking score that combines the previous quantities. It is not a calibrated probability.

The prototype uses robust percentile normalization, metric-aware slope computation, overlapping-ready spatial cell abstractions, and an evidence-aware ranking rule. The complete proposed architecture is documented in [`docs/methodology.md`](docs/methodology.md).

## Current results

The current run produced 96 Earth candidate cells. The highest-ranked cells are retained in `data/algorithm_outputs/candidate_rankings.csv` and visualized in `figures/algorithm/01_candidate_ranking.png`. In this topography-only run, candidates remain mostly in the neutral class; this is expected because a complete planetary analog decision requires additional independent evidence. The result should therefore be interpreted as a reproducible screening output, not a final analog designation.

## Provenance and data access

MOLA source files come from the NASA PDS Geosciences Node. NASADEM product identity, resolution, processing level, provenance, and citation are recorded in the Earthdata catalog metadata. The local COG downloads were accessed through the public Microsoft Planetary Computer STAC collection for NASADEM HGT v001; the acquisition manifest records the unsigned asset URLs and collection identity.

## Limitations

The prototype currently uses a single topographic family on each planet and does not yet include CRISM, THEMIS, HiRISE, CTX, Landsat, Sentinel-2, or rover observations. The MOLA crop is a 16 pixels/degree product, while NASADEM is approximately 30 m. The pipeline harmonizes descriptors rather than pretending that the raw grids have identical physical resolution. Further work is required for independent calibration, cross-instrument uncertainty propagation, source-lineage de-duplication, spatial cross-validation, and expert geological review.

## License and data notice

Code and documentation are released under the MIT License. Third-party datasets remain subject to their original NASA/PDS, Earthdata, and Planetary Computer terms. The repository stores manifests, scripts, metadata, processed summaries, and figures; large raw source products are kept locally and reproducibly downloadable rather than redistributed in Git history.
