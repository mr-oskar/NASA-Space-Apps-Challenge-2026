# Data dictionary and provenance

## Raw products

| Product | Role | Resolution / format | Provenance |
|---|---|---|---|
| MOLA MEGDR `megt90n000eb.img` | Mars topography reference | 16 pixels/degree, PDS binary signed big-endian int16 | NASA PDS Geosciences Node |
| MOLA `.xml` and `.hdr` | Product and grid metadata | PDS4 XML and ENVI header | NASA PDS Geosciences Node |
| NASADEM HGT v001 COG tiles | Earth elevation search domain | about 30 m, GeoTIFF COG | NASA Earthdata product mirrored through Planetary Computer STAC |

## Processed variables

- `elevation_m`: source elevation in meters; missing values are NaN in NumPy arrays and `-32767` in GeoTIFF output.
- `slope_deg`: local slope computed from metric-aware gradients.
- `roughness_m`: absolute deviation from a local mean filter.
- `valid_fraction`: fraction of valid pixels in a candidate cell.
- `similarity_score`: exponential transform of robust feature distance.
- `evidence_coverage`: fraction of required prototype features available.
- `confidence_score`: screening score combining similarity, coverage, and valid-data quality.

## Important interpretation notes

NASADEM is a derived product based primarily on SRTM data and additional control/reprocessing inputs. It is not an independent observation from MOLA, and MOLA and NASADEM are not treated as identical measurement systems. The Earth and Mars grids have different native resolution and reference surfaces; the pipeline compares derived descriptors rather than raw pixel values.
