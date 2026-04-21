"""Histogram of positive (> 0) NO₂ mass per pixel from tempo_mass_no2_kg_per_pixel.tif.

Zeros are excluded so the y-axis is not dominated by the no-emission pixels.

For clipped study windows, integrated totals, maps, and CSV logging, use
``tempo_case_analysis.py`` (see METHODS_TEMPO.md).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio

HERE = Path(__file__).resolve().parent
TIF = HERE / "tempo_mass_no2_kg_per_pixel.tif"
OUT = HERE / "tempo_mass_no2_kg_per_pixel_histogram.png"


def main() -> None:
    with rasterio.open(TIF) as ds:
        arr = ds.read(1)
        nodata = ds.nodata

    if nodata is not None:
        mask = np.isfinite(arr) & (arr != nodata) & (arr > 0)
    else:
        mask = np.isfinite(arr) & (arr > 0)
    mass_kg = arr[mask]

    fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
    ax.hist(mass_kg, bins=40, color="#2c5282", edgecolor="white", linewidth=0.4)
    ax.set_xlabel("NO₂ mass per pixel (kg)")
    ax.set_ylabel("Number of pixels")
    ax.set_title("Distribution of positive NO₂ mass per pixel (kg)")
    ax.grid(axis="y", alpha=0.35)

    stats = (
        f"pixels (> 0) = {mass_kg.size:,}\n"
        f"min = {mass_kg.min():.4g} kg\n"
        f"max = {mass_kg.max():.4g} kg\n"
        f"mean = {mass_kg.mean():.4g} kg\n"
        f"median = {np.median(mass_kg):.4g} kg"
    )
    ax.text(
        0.98,
        0.97,
        stats,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="wheat", alpha=0.85),
    )

    fig.savefig(OUT, dpi=150)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
