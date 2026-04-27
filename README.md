# TEMPO NO₂ enhancement case studies

NASA **TEMPO** Level-2 NO₂ **enhancement** analysis for three cases: **smoke plume (Eaton)**, **power plant (Walnut Creek)**, and **dense urban (Los Angeles)** — same study-box size where applicable, QA/cloud screening, and documented metrics.

## Repository

**GitHub:** [wrtcd/tempo-no2-enhancement-case-studies](https://github.com/wrtcd/tempo-no2-enhancement-case-studies)

```bash
git clone https://github.com/wrtcd/tempo-no2-enhancement-case-studies.git
```

## Documentation

| Doc | Content |
|-----|---------|
| [`METHODS_TEMPO.md`](METHODS_TEMPO.md) | Locked workflow, case definitions |
| [`CASE_STUDIES_WRITEUP.md`](CASE_STUDIES_WRITEUP.md) | **Full narrative:** time/date per case, what we did, 3×3 results, reproduction |
| [`results/case_study_time_context.csv`](results/case_study_time_context.csv) | **Year, UTC, Pacific local, granule** (one row per case) |
| [`results/RESULTS_AND_INTERPRETATION.md`](results/RESULTS_AND_INTERPRETATION.md) | Results table and interpretation |
| [`MANIFEST.md`](MANIFEST.md) | Data paths, scripts, **remote URL** |

## Quick start

- Python: `py -3 -m pip install -r requirements.txt`
- Cases 2–3 preprocess: see [`casestudy2/CASE2_PREPROCESS.md`](casestudy2/CASE2_PREPROCESS.md)
- Analysis: `tempo_case_analysis.py`; **3×3 (cases × VCD path):** `py -3 scripts/generate_3x3_matrix.py` → `results/comparison_table_3x3.csv`
- **Default work root** (sibling repos: `no2-plume-vcd-branches`, `eaton-vcd-adj`, etc.): `WORK April 2026\geometric corrections`. Override: `set TEMPO_CASE_WORK=C:\path\to\parent`
- Figures bundle: `export_results_bundle.py`

## Data notice

Large **`.nc`** granules are usually **not** committed; paths are listed in [`MANIFEST.md`](MANIFEST.md). Obtain TEMPO L2 files from NASA Earthdata / LAADS per your access.
