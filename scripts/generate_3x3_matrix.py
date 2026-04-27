"""
Build 3 case studies x 3 VCD pathways -> results/case_runs_3x3.csv and comparison_table_3x3.csv.

Case 1: clips mass from no2-plume-vcd-branches outputs/08_mass (if present).
Case 2 / 3: runs scripts/case23_mass_three_vcd.py (needs GDAL + eaton-vcd-adj for vcd_adj).

From repo root:
  py -3 scripts/generate_3x3_matrix.py
  py -3 scripts/generate_3x3_matrix.py --skip-case1-clip   # only regenerate case 2-3
  py -3 scripts/generate_3x3_matrix.py --skip-case23      # only clip case 1 + analyze
"""
from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RESULTS = REPO / "results"
RUNS_3x3 = RESULTS / "case_runs_3x3.csv"
TABLE_3x3 = RESULTS / "comparison_table_3x3.csv"


# Parent folder for no2-plume-vcd-branches, eaton-2, eaton, eaton-vcd-adj (override with TEMPO_CASE_WORK).
_DEFAULT_CASE_WORK = Path(r"C:\Users\aeaturu\Desktop\WORK April 2026\geometric corrections")


def _work() -> Path:
    e = os.environ.get("TEMPO_CASE_WORK", "")
    return Path(e) if e else _DEFAULT_CASE_WORK


def _plume_mass_paths() -> dict[str, Path]:
    root = _work() / "no2-plume-vcd-branches" / "outputs" / "08_mass"
    return {
        "operational": root / "operational" / "tempo_mass_no2_kg_per_pixel.tif",
        "vcd_check": root / "vcdcheck" / "tempo_mass_no2_kg_per_pixel.tif",
        "vcd_adj": root / "vcdadj" / "tempo_mass_no2_kg_per_pixel.tif",
    }


def _find_nc_july() -> Path | None:
    name = "TEMPO_NO2_L2_V03_20250723T210939Z_S012G09.nc"
    for base in (
        REPO / "casestudy2",
        _work() / "eaton-2" / "casestudy2",
        _work() / "eaton" / "data" / "tempo",
    ):
        p = base / name
        if p.is_file():
            return p
    return None


def _clip_case1(gdalwarp: str, box: Path, src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        gdalwarp,
        "-of",
        "GTiff",
        "-cutline",
        str(box.resolve()),
        "-crop_to_cutline",
        "-dstnodata",
        "-1e+30",
        "-overwrite",
        str(src.resolve()),
        str(dst.resolve()),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return False
    return True


def _run_analysis(py: str, tif: Path, case_id: str) -> bool:
    ta = REPO / "tempo_case_analysis.py"
    cmd = [
        py,
        str(ta),
        str(tif),
        "--case-id",
        case_id,
        "--runs-csv",
        str(RUNS_3x3),
        "--no-map",
    ]
    r = subprocess.run(cmd, cwd=str(REPO))
    return r.returncode == 0


def _write_table_from_runs() -> None:
    if not RUNS_3x3.is_file():
        print(f"No {RUNS_3x3}", file=sys.stderr)
        return
    with RUNS_3x3.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    narrative = {
        "case1_smoke_operational": ("case1_smoke", "operational", "Smoke / Eaton plume"),
        "case1_smoke_vcd_check": ("case1_smoke", "vcd_check", "Smoke / Eaton plume"),
        "case1_smoke_vcd_adj": ("case1_smoke", "vcd_adj", "Smoke / Eaton plume"),
        "case2_plant_operational": ("case2_plant", "operational", "Power plant"),
        "case2_plant_vcd_check": ("case2_plant", "vcd_check", "Power plant"),
        "case2_plant_vcd_adj": ("case2_plant", "vcd_adj", "Power plant"),
        "case3_city_operational": ("case3_city", "operational", "Dense urban"),
        "case3_city_vcd_check": ("case3_city", "vcd_check", "Dense urban"),
        "case3_city_vcd_adj": ("case3_city", "vcd_adj", "Dense urban"),
    }
    out_rows = []
    for r in rows:
        cid = r.get("case_id", "")
        base, vcd, nar = narrative.get(cid, (cid, "", ""))
        out_rows.append(
            {
                "case_id": base,
                "vcd_pathway": vcd,
                "case_id_full": cid,
                "narrative": nar,
                "integrated_tonnes_valid": r.get("integrated_total_tonnes_valid", ""),
                "integrated_tonnes_positive_only": r.get("integrated_total_tonnes_positive_only", ""),
                "n_valid_pixels": r.get("n_valid_pixels", ""),
                "n_positive_pixels": r.get("n_positive_pixels", ""),
                "footprint_area_km2": r.get("footprint_area_km2", ""),
                "positive_min_kg": r.get("positive_min_kg", ""),
                "positive_max_kg": r.get("positive_max_kg", ""),
                "positive_median_kg": r.get("positive_median_kg", ""),
                "min_kg_all_valid": r.get("min_kg_all_valid", ""),
                "max_kg_all_valid": r.get("max_kg_all_valid", ""),
                "median_kg_all_valid": r.get("median_kg_all_valid", ""),
                "sum_kg_all_valid": r.get("sum_kg_all_valid", ""),
                "sum_kg_positive_only": r.get("sum_kg_positive_only", ""),
                "tif": r.get("tif", ""),
            }
        )
    fn = list(out_rows[0].keys()) if out_rows else []
    TABLE_3x3.parent.mkdir(parents=True, exist_ok=True)
    with TABLE_3x3.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {TABLE_3x3}")


def main() -> int:
    import shutil

    py = sys.executable
    gdalwarp = shutil.which("gdalwarp")
    if not gdalwarp:
        print("ERROR: gdalwarp not on PATH", file=sys.stderr)
        return 1

    skip1 = "--skip-case1-clip" in sys.argv
    skip23 = "--skip-case23" in sys.argv

    # fresh runs log
    if RUNS_3x3.is_file():
        RUNS_3x3.unlink()

    box1 = REPO / "casestudy1" / "eaton-study-box.shp"
    if not skip1 and box1.is_file():
        pl = _plume_mass_paths()
        for key, src in pl.items():
            dst = REPO / "casestudy1" / f"massno2-eaton-clipped_{key}.tif"
            if _clip_case1(gdalwarp, box1, src, dst):
                print(f"Clipped case1 {key} -> {dst.name}", flush=True)
            else:
                print(f"Skip case1 {key}: missing {src}", file=sys.stderr)

    nc_july = _find_nc_july()
    if not skip23:
        if nc_july is None:
            print("ERROR: July 2025 TEMPO L2 granule not found for case 2–3.", file=sys.stderr)
            return 1
        c23 = HERE / "case23_mass_three_vcd.py"
        for tag, box, outd in (
            ("plant", REPO / "casestudy2" / "walnut-creek-study-box.shp", REPO / "casestudy2"),
            ("city", REPO / "casestudy3" / "la-study-box.shp", REPO / "casestudy3"),
        ):
            if not box.is_file():
                print(f"ERROR: missing {box}", file=sys.stderr)
                return 1
            r = subprocess.run(
                [
                    py,
                    str(c23),
                    "--nc",
                    str(nc_july),
                    "--box",
                    str(box),
                    "--out-dir",
                    str(outd),
                    "--tag",
                    tag,
                    "--prefix",
                    f"matrix_{tag}",
                ],
                cwd=str(REPO),
            )
            if r.returncode != 0:
                return r.returncode

    # analyze 9 tifs
    jobs: list[tuple[str, Path]] = []
    for k in ("operational", "vcd_check", "vcd_adj"):
        p1 = REPO / "casestudy1" / f"massno2-eaton-clipped_{k}.tif"
        if p1.is_file():
            jobs.append((f"case1_smoke_{k}", p1))
    for k in ("operational", "vcd_check", "vcd_adj"):
        p2 = REPO / "casestudy2" / f"massno2-plant-{k}.tif"
        if p2.is_file():
            jobs.append((f"case2_plant_{k}", p2))
    for k in ("operational", "vcd_check", "vcd_adj"):
        p3 = REPO / "casestudy3" / f"massno2-city-{k}.tif"
        if p3.is_file():
            jobs.append((f"case3_city_{k}", p3))

    if not jobs:
        print("ERROR: no mass GeoTIFFs to analyze. Run with data present.", file=sys.stderr)
        return 1

    for case_id, tif in jobs:
        if not _run_analysis(py, tif, case_id):
            print(f"Failed: {case_id}", file=sys.stderr)
            return 1
        print(f"OK: {case_id}")

    _write_table_from_runs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
