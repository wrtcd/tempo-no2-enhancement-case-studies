# Results folder

| File | Purpose |
|------|---------|
| `comparison_table_3x3.csv` | 3 case studies × 3 VCD pathways (operational, vcd_check, vcd_adj) — from `py -3 scripts/generate_3x3_matrix.py` |
| `case_runs_3x3.csv` | Per-cell metrics for the 3×3 matrix (same as case_runs but from matrix generator) |
| `case_study_time_context.csv` | **Temporal framing** per case: year, date, UTC range, America/Los_Angeles, granule, season |
| `RESULTS_AND_INTERPRETATION.md` | Write-up: methods contrast, table, interpretation |
| `confounders_template.csv` | Optional ERA5 / notes (fill if used) |
| `figures/` | Run `py -3 export_results_bundle.py` from repo root to populate |
