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
| [`results/RESULTS_AND_INTERPRETATION.md`](results/RESULTS_AND_INTERPRETATION.md) | Results table and interpretation |
| [`MANIFEST.md`](MANIFEST.md) | Data paths, scripts, **remote URL** |

## Quick start

- Python: `py -3 -m pip install -r requirements.txt`
- Cases 2–3 preprocess: see [`casestudy2/CASE2_PREPROCESS.md`](casestudy2/CASE2_PREPROCESS.md)
- Analysis: `tempo_case_analysis.py`; figures bundle: `export_results_bundle.py`

## Data notice

Large **`.nc`** granules are usually **not** committed; paths are listed in [`MANIFEST.md`](MANIFEST.md). Obtain TEMPO L2 files from NASA Earthdata / LAADS per your access.
