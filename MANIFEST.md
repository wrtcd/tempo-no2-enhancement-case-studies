# Data and code manifest

## GitHub repository

**Remote:** [github.com/wrtcd/tempo-no2-enhancement-case-studies](https://github.com/wrtcd/tempo-no2-enhancement-case-studies)

```text
https://github.com/wrtcd/tempo-no2-enhancement-case-studies.git
```

After renaming the local folder to match (optional), connect and push:

```bash
git remote add origin https://github.com/wrtcd/tempo-no2-enhancement-case-studies.git
git branch -M main
git push -u origin main
```

## TEMPO Level-2 NetCDF (source)

| File | Location | Used for |
|------|----------|----------|
| `TEMPO_NO2_L2_V03_20250109T184504Z_S008G09.nc` | `eaton/data/tempo/` (original path in `case1_metadata`) | Case 1 smoke (processing pipeline upstream of `eaton-2`) |
| `TEMPO_NO2_L2_V03_20250723T210939Z_S012G09.nc` | `eaton-2/casestudy2/` | Cases 2 & 3 (same file) |

## Clipped analysis rasters (`eaton-2`)

| Case | Mass GeoTIFF | Study box |
|------|----------------|-----------|
| 1 | `casestudy1/massno2-eaton-clipped.tif` | `casestudy1/eaton-study-box.shp` |
| 2 | `casestudy2/massno2-plant-clipped.tif` | `casestudy2/walnut-creek-study-box.shp` |
| 3 | `casestudy3/massno2-city-clipped.tif` | `casestudy3/la-study-box.shp` |

## Scripts (reproducibility)

| Script | Role |
|--------|------|
| `casestudy2/preprocess_tempo_walnut.py` | NetCDF → UTM clip → QA/cloud → ΔVCD mass (Cases 2–3; `--box`, `--mass-name`) |
| `tempo_case_analysis.py` | Stats, histogram, map, `case_runs.csv` |
| `refresh_comparison_table.py` | `comparison_table.csv` from metadata + runs |
| `export_results_bundle.py` | Copy figures to `results/figures/` |

## Aggregated outputs

- `results/case_runs.csv` — per-run metrics  
- `results/comparison_table.csv` — three-case summary  
- `results/figures/` — standardized figure copies (after export)

## Version notes

- TEMPO L2 **V03** in filenames; Python deps: `requirements.txt`.
