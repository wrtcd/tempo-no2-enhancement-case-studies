"""Side-by-side NO₂ enhancement mass maps (kg per pixel) for Cases 1–3.

Reads the three clipped GeoTIFFs in-repo (see MANIFEST.md), applies the same
valid-pixel mask as tempo_case_analysis.py, and writes one figure with
independent color scales per panel (Case 1 is often orders of magnitude larger).

Usage:
  py -3 plot_three_case_maps.py
  py -3 plot_three_case_maps.py --out results/figures/three_case_maps_kg.png
  py -3 plot_three_case_maps.py --tif1 path/to/a.tif --tif2 ... --tif3 ...
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.plot import show as rio_show

from tempo_case_analysis import valid_mask

HERE = Path(__file__).resolve().parent

DEFAULT_TIFS = (
    HERE / "casestudy1" / "massno2-eaton-clipped.tif",
    HERE / "casestudy2" / "massno2-plant-clipped.tif",
    HERE / "casestudy3" / "massno2-city-clipped.tif",
)

LABELS = (
    "Case 1 — smoke / Eaton plume",
    "Case 2 — plant (Walnut Creek)",
    "Case 3 — dense urban (LA core)",
)


def plot_panel(ax, tif_path: Path, title: str) -> None:
    with rasterio.open(tif_path) as ds:
        arr = ds.read(1).astype(np.float64)
        vm = valid_mask(arr, ds.nodata)
        arr_plot = np.ma.masked_where(~vm, arr)
        vc = arr_plot.compressed()
        vmin = float(np.min(vc)) if vc.size else 0.0
        vmax = float(np.max(vc)) if vc.size else 1.0
        if vmin == vmax:
            vmax = vmin + 1e-9
        rio_show(
            arr_plot,
            ax=ax,
            transform=ds.transform,
            cmap="viridis",
            vmin=vmin,
            vmax=vmax,
        )
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    im = ax.images[0]
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("kg NO₂ per pixel")


def main() -> None:
    p = argparse.ArgumentParser(description="1×3 map of enhancement mass (kg/pixel)")
    p.add_argument(
        "--tif1",
        type=Path,
        default=DEFAULT_TIFS[0],
        help="Case 1 mass GeoTIFF",
    )
    p.add_argument(
        "--tif2",
        type=Path,
        default=DEFAULT_TIFS[1],
        help="Case 2 mass GeoTIFF",
    )
    p.add_argument(
        "--tif3",
        type=Path,
        default=DEFAULT_TIFS[2],
        help="Case 3 mass GeoTIFF",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=HERE / "results" / "figures" / "three_case_maps_kg.png",
        help="Output PNG path",
    )
    args = p.parse_args()

    tifs = (args.tif1.resolve(), args.tif2.resolve(), args.tif3.resolve())
    for t in tifs:
        if not t.is_file():
            raise SystemExit(
                f"Missing GeoTIFF: {t}\n"
                "Place the three clipped mass rasters under casestudy1/ … casestudy3/ "
                "(see MANIFEST.md) or pass --tif1/--tif2/--tif3."
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), layout="constrained")
    for ax, path, lbl in zip(axes, tifs, LABELS, strict=True):
        plot_panel(ax, path, lbl)
    fig.suptitle("TEMPO NO₂ enhancement mass (kg per pixel)", fontsize=13, fontweight="bold")
    fig.savefig(args.out, dpi=180)
    plt.close(fig)
    print(f"Wrote {args.out.resolve()}")


if __name__ == "__main__":
    main()
