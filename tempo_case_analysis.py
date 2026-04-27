"""Unified metrics + histogram for TEMPO enhancement mass GeoTIFFs (Cases 1–3).

Reads a clipped raster, applies NoData mask, computes footprint area, integrated
mass (kg, tonnes), positive-only stats, writes PNG histogram + optional quick map,
and appends a row to results/case_runs.csv.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.plot import show as rio_show

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RUNS_CSV = RESULTS / "case_runs.csv"


def pixel_area_m2(transform: rasterio.Affine) -> float:
    return abs(transform[0] * transform[4])


def load_mass_array(path: Path) -> tuple[np.ndarray, float | None, rasterio.Affine, rasterio.crs.CRS]:
    with rasterio.open(path) as ds:
        arr = ds.read(1).astype(np.float64)
        nodata = ds.nodata
        transform = ds.transform
        crs = ds.crs
    return arr, nodata, transform, crs


def valid_mask(arr: np.ndarray, nodata: float | None) -> np.ndarray:
    m = np.isfinite(arr)
    if nodata is not None:
        m &= arr != nodata
    return m


def analyze_case(
    tif_path: Path,
    case_id: str,
    out_dir: Path | None = None,
    histogram_bins: int = 40,
    write_map: bool = True,
    append_csv: bool = True,
    runs_csv: Path | None = None,
) -> dict:
    out_dir = out_dir or tif_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    arr, nodata, transform, crs = load_mass_array(tif_path)
    area_m2 = pixel_area_m2(transform)
    vm = valid_mask(arr, nodata)
    positive = vm & (arr > 0)

    integrated_all_kg = float(np.sum(arr[vm]))
    integrated_positive_kg = float(np.sum(arr[positive])) if np.any(positive) else 0.0
    n_valid = int(np.count_nonzero(vm))
    n_positive = int(np.count_nonzero(positive))
    footprint_km2 = n_valid * area_m2 / 1e6
    vdat = arr[vm]

    stats: dict = {
        "case_id": case_id,
        "tif": str(tif_path.resolve()),
        "crs": str(crs) if crs else "",
        "pixel_area_m2": area_m2,
        "rows": arr.shape[0],
        "cols": arr.shape[1],
        "n_valid_pixels": n_valid,
        "n_positive_pixels": n_positive,
        "footprint_area_km2": footprint_km2,
        "min_kg_all_valid": float(np.min(vdat)),
        "max_kg_all_valid": float(np.max(vdat)),
        "median_kg_all_valid": float(np.median(vdat)),
        "sum_kg_all_valid": integrated_all_kg,
        "sum_kg_positive_only": integrated_positive_kg,
        "integrated_total_kg_valid": integrated_all_kg,
        "integrated_total_tonnes_valid": integrated_all_kg / 1000.0,
        "integrated_total_kg_positive_only": integrated_positive_kg,
        "integrated_total_tonnes_positive_only": integrated_positive_kg / 1000.0,
    }

    if n_positive:
        pos = arr[positive]
        stats["positive_min_kg"] = float(np.min(pos))
        stats["positive_max_kg"] = float(np.max(pos))
        stats["positive_mean_kg"] = float(np.mean(pos))
        stats["positive_median_kg"] = float(np.median(pos))
    else:
        stats["positive_min_kg"] = np.nan
        stats["positive_max_kg"] = np.nan
        stats["positive_mean_kg"] = np.nan
        stats["positive_median_kg"] = np.nan

    stem = tif_path.stem
    hist_path = out_dir / f"{stem}_histogram_positive.png"
    fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
    if n_positive:
        ax.hist(arr[positive], bins=histogram_bins, color="#2c5282", edgecolor="white", linewidth=0.4)
    ax.set_xlabel("NO₂ mass per pixel (kg)")
    ax.set_ylabel("Number of pixels")
    ax.set_title(f"{case_id}: distribution of positive NO₂ mass per pixel (kg)")
    ax.grid(axis="y", alpha=0.35)
    txt = (
        f"min (all valid) = {stats['min_kg_all_valid']:.4g} kg\n"
        f"max (all valid) = {stats['max_kg_all_valid']:.4g} kg\n"
        f"median (all valid) = {stats['median_kg_all_valid']:.4g} kg\n"
        f"Σ all valid = {integrated_all_kg:.4g} kg\n"
        f"--- positive only ---\n"
        f"pixels (> 0) = {n_positive:,}\n"
        f"min = {stats['positive_min_kg']:.4g} kg\n"
        f"max = {stats['positive_max_kg']:.4g} kg\n"
        f"mean = {stats['positive_mean_kg']:.4g} kg\n"
        f"median = {stats['positive_median_kg']:.4g} kg\n"
        f"Σ positive = {integrated_positive_kg:.4g} kg\n"
        f"Σ positive = {integrated_positive_kg/1000:.4g} t"
    )
    ax.text(
        0.98, 0.97, txt, transform=ax.transAxes, fontsize=9,
        verticalalignment="top", horizontalalignment="right", family="monospace",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="wheat", alpha=0.85),
    )
    fig.savefig(hist_path, dpi=150)
    plt.close(fig)
    stats["histogram_png"] = str(hist_path.resolve())

    if write_map:
        map_path = out_dir / f"{stem}_map.png"
        fig2, ax2 = plt.subplots(figsize=(6, 5), layout="constrained")
        with rasterio.open(tif_path) as ds:
            arr_plot = np.ma.masked_where(~vm, arr)
            rio_show(arr_plot, ax=ax2, cmap="viridis")
        ax2.set_title(f"{case_id}: enhancement mass (kg per pixel)")
        fig2.savefig(map_path, dpi=150)
        plt.close(fig2)
        stats["map_png"] = str(map_path.resolve())
    else:
        stats["map_png"] = ""

    if append_csv:
        runs_path = (runs_csv or RUNS_CSV).resolve()
        runs_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "run_utc": datetime.now(timezone.utc).isoformat(),
            **{k: stats[k] for k in stats if k not in ("histogram_png", "map_png")},
            "histogram_png": stats["histogram_png"],
            "map_png": stats.get("map_png", ""),
        }
        file_exists = runs_path.is_file()
        fieldnames = list(row.keys())
        with runs_path.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                w.writeheader()
            w.writerow(row)
        stats["runs_csv"] = str(runs_path)

    return stats


def main() -> None:
    p = argparse.ArgumentParser(description="TEMPO enhancement mass: metrics + histogram + optional map")
    p.add_argument("tif", type=Path, help="Path to clipped GeoTIFF")
    p.add_argument("--case-id", default="case", help="Case label (e.g. case1_smoke)")
    p.add_argument("--out-dir", type=Path, default=None, help="Output directory for PNGs")
    p.add_argument("--no-map", action="store_true", help="Skip map PNG")
    p.add_argument("--no-csv", action="store_true", help="Do not append to results/case_runs.csv")
    p.add_argument(
        "--runs-csv",
        type=Path,
        default=None,
        help="Override results CSV (default: results/case_runs.csv)",
    )
    args = p.parse_args()

    s = analyze_case(
        args.tif.resolve(),
        args.case_id,
        out_dir=args.out_dir,
        write_map=not args.no_map,
        append_csv=not args.no_csv,
        runs_csv=args.runs_csv,
    )
    for k in ("integrated_total_tonnes_valid", "footprint_area_km2", "histogram_png", "map_png"):
        print(f"{k}: {s.get(k, '')}")


if __name__ == "__main__":
    main()
