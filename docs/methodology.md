# Methodology

## Research question

Can an evidence-aware, multi-scale, incremental inferential-node architecture improve the screening and scientific interpretation of terrestrial planetary analog candidates compared with direct comparison of area averages?

## Study design

The reference region is Gale Crater on Mars. The initial Earth search domain is the Atacama Desert, including the Maria Elena South and Yungay research areas. The current reproducible prototype deliberately begins with topography so that the effect of provenance-aware harmonization can be inspected before adding spectral, thermal, and geological products.

## Data model

An evidence node is represented conceptually as:

\[
E_i=(x_i,s_i,m_i,q_i,u_i,t_i,p_i)
\]

where \(x_i\) is the measured or extracted value, \(s_i\) is its source, \(m_i\) is the measurement method/instrument, \(q_i\) is quality, \(u_i\) is uncertainty, \(t_i\) is time, and \(p_i\) is spatial position and scale.

A relationship is represented as:

\[
R_{ij}=(type,w_{ij},e_{ij},q_{ij})
\]

where `type` describes the relationship, \(w_{ij}\) is its strength, \(e_{ij}\) stores supporting or contradicting evidence, and \(q_{ij}\) stores relationship quality.

The spatial representation is a graph \(G=(V,E)\). Nodes are sites or spatial cells. Edges may represent adjacency, overlap, continuation across a boundary, or a scientifically interpretable relationship.

## Harmonization

MOLA MEGDR is read from its ENVI header as a big-endian signed 16-bit meter grid. The Gale crop is selected by geographic coordinates using the documented equirectangular Mars grid. NASADEM COG tiles are mosaicked in their geographic coordinate system. No raw value is claimed to be directly interchangeable across instruments.

For each elevation array, the pipeline computes:

- elevation mean and standard deviation;
- local slope from metric-aware gradients;
- local roughness relative to a neighborhood mean;
- valid-data fraction;
- robust normalized rasters using the 2nd and 98th percentiles for visualization and comparable feature ranges.

Robust normalization is:

\[
z' = clip\left(\frac{z-Q_{0.02}}{Q_{0.98}-Q_{0.02}},0,1\right)
\]

It is used for visualization and feature conditioning, not to erase the original units or uncertainty.

## Candidate scoring

For an Earth cell \(c\) and a Martian target vector \(r\), the prototype uses a robust feature distance:

\[
d(c,r)=\sqrt{\frac{1}{K}\sum_{k=1}^{K}\left(\frac{c_k-r_k}{IQR_k}\right)^2}
\]

and a similarity transform:

\[
s(c,r)=e^{-d(c,r)}.
\]

The prototype confidence score is:

\[
C(c)=0.65s(c,r)+0.20\,Coverage(c)+0.15\,Quality(c).
\]

The output classes are screening labels only:

- `high` if \(C\geq0.7\);
- `neutral` if \(0.3\leq C<0.7\);
- `low` if \(C<0.3\).

The score is not a calibrated posterior probability. Calibration, source dependence, and independent validation must be added before scientific decision-making.

## Evidence conflict and neutral nodes

When measurement principles, calibration, scale, or provenance disagree, the system should preserve the conflict. A neutral node with design value \(T=0.5\) can represent an unresolved hypothesis. This value is a convention, not a probability. Dependent products must not be counted as independent confirmation; the data-lineage graph is therefore part of the evidence model.

## Reproducibility checks

The figures under `figures/processing` check raw distributions, normalized maps, and data coverage. The figures under `figures/algorithm` inspect ranking stability, confidence classes, and candidate feature space. A proper next experiment should vary cell size, overlap/halo width, missingness, source dependence, and withheld validation sites.
