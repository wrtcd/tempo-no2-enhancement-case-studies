"""Rebuild results/comparison_table.csv from the latest run per case_id in results/case_runs.csv."""
from __future__ import annotations

import csv
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "results" / "case_runs.csv"
OUT = HERE / "results" / "comparison_table.csv"
CASE1_META = HERE / "casestudy1" / "case1_metadata.csv"
CASE2_META = HERE / "casestudy2" / "case2_metadata.csv"
CASE3_META = HERE / "casestudy3" / "case3_metadata.csv"


def _one_row_csv(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        row = next(r, None)
    return dict(row) if row else {}


def main() -> None:
    meta1 = _one_row_csv(CASE1_META)
    meta2 = _one_row_csv(CASE2_META)
    meta3 = _one_row_csv(CASE3_META)
    study_km2_common = meta1.get("study_box_area_km2", "")
    if not RUNS.is_file():
        print(f"No {RUNS}; run tempo_case_analysis.py first.")
        return
    with RUNS.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_case: OrderedDict[str, dict] = OrderedDict()
    for r in rows:
        cid = r.get("case_id", "")
        by_case[cid] = r

    fieldnames = [
        "case_id",
        "narrative",
        "study_box_km2",
        "clipped_footprint_km2",
        "integrated_tonnes_valid",
        "integrated_tonnes_positive_only",
        "n_valid_pixels",
        "n_positive_pixels",
        "positive_min_kg",
        "positive_max_kg",
        "positive_median_kg",
        "granule_file",
        "time_start_utc",
        "status",
    ]
    narrative_map = {
        "case1_smoke": "Smoke / Eaton plume enhancement",
        "case2_plant": "Power plant (SoCal / near LA)",
        "case3_city": "Dense urban (e.g. LA core)",
    }
    pending = {
        "case2_plant": {
            "study_box_km2": "match_case1_~93km2",
            "clipped_footprint_km2": "TBD",
            "integrated_tonnes_valid": "TBD",
            "integrated_tonnes_positive_only": "TBD",
            "n_valid_pixels": "TBD",
            "n_positive_pixels": "TBD",
            "positive_min_kg": "TBD",
            "positive_max_kg": "TBD",
            "positive_median_kg": "TBD",
            "granule_file": "TBD",
            "time_start_utc": "TBD",
            "status": "pending_raster",
        },
        "case3_city": {
            "study_box_km2": "match_case1_~93km2",
            "clipped_footprint_km2": "TBD",
            "integrated_tonnes_valid": "TBD",
            "integrated_tonnes_positive_only": "TBD",
            "n_valid_pixels": "TBD",
            "n_positive_pixels": "TBD",
            "positive_min_kg": "TBD",
            "positive_max_kg": "TBD",
            "positive_median_kg": "TBD",
            "granule_file": "TBD",
            "time_start_utc": "TBD",
            "status": "pending_raster",
        },
    }

    out_rows = []
    for cid in ("case1_smoke", "case2_plant", "case3_city"):
        if cid in by_case:
            r = by_case[cid]
            if cid == "case1_smoke":
                granule = meta1.get("tempo_l2_granule_file", "")
                tstart = meta1.get("tempo_time_start_utc", "")
            elif cid == "case2_plant":
                granule = meta2.get("tempo_l2_granule_file", "")
                tstart = meta2.get("tempo_time_start_utc", "")
            elif cid == "case3_city":
                granule = meta3.get("tempo_l2_granule_file", "")
                tstart = meta3.get("tempo_time_start_utc", "")
            else:
                granule, tstart = "", ""
            out_rows.append(
                {
                    "case_id": cid,
                    "narrative": narrative_map.get(cid, ""),
                    "study_box_km2": study_km2_common,
                    "clipped_footprint_km2": r.get("footprint_area_km2", ""),
                    "integrated_tonnes_valid": r.get("integrated_total_tonnes_valid", ""),
                    "integrated_tonnes_positive_only": r.get("integrated_total_tonnes_positive_only", ""),
                    "n_valid_pixels": r.get("n_valid_pixels", ""),
                    "n_positive_pixels": r.get("n_positive_pixels", ""),
                    "positive_min_kg": r.get("positive_min_kg", ""),
                    "positive_max_kg": r.get("positive_max_kg", ""),
                    "positive_median_kg": r.get("positive_median_kg", ""),
                    "granule_file": granule,
                    "time_start_utc": tstart,
                    "status": "complete",
                }
            )
        else:
            out_rows.append(
                {
                    "case_id": cid,
                    "narrative": narrative_map.get(cid, ""),
                    **pending[cid],
                }
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in out_rows:
            w.writerow(row)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
