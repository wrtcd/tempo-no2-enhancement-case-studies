"""
TEMPO L2 NetCDF → UTM 11N clip → QA/cloud screen → enhancement mass (kg/pixel).

Used for Case 2 (Walnut) and Case 3 (LA) with different `--box` and `--mass-name`.

Mirrors the Eaton repo rules in scripts/tempo/screen_tempo_pixels.py:
  - main_data_quality_flag <= --qa-main-max (default 0)
  - eff_cloud_fraction <= --cloud-max (default 0.3)
  - finite tropospheric VCD (product fill removed)

Uses the official L2 field /product/vertical_column_troposphere (molecules/cm²). You do **not**
need to recompute tropospheric VCD or AMF for a standard analysis — those are in the retrieval.
Optional SCD/AMF consistency checks live in eaton/scripts/tempo/vcd_check_scd_amf.py if you
want validation later.

Enhancement here: ΔVCD = VCD - VCD_bg, with VCD_bg = median(VCD) over pixels that pass the
screen (simple local background for a compact box). Then mass kg/pixel from ΔVCD (same
conversion as eaton/scripts/tempo/mass_no2_from_plume.py).

Requires: GDAL CLI (gdalwarp), numpy, rasterio
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

try:
    import rasterio
except ImportError:
    print("Install rasterio: py -3 -m pip install rasterio", file=sys.stderr)
    sys.exit(1)

HERE = Path(__file__).resolve().parent
DEFAULT_BOX = HERE / "walnut-creek-study-box.shp"

# TEMPO NO2 L2 subdataset paths (GDAL NETCDF notation)
SD_VCD = "/product/vertical_column_troposphere"
SD_QA = "/product/main_data_quality_flag"
SD_CLOUD = "/support_data/eff_cloud_fraction"

N_A = 6.02214076e23
M_NO2_KG_PER_MOL = 46.0055e-3
NODATA = -1.0e30


def _netcdf_uri(nc: Path, subds: str) -> str:
    p = nc.resolve()
    return f'NETCDF:"{p.as_posix()}":{subds}'


def _run_gdalwarp(
    src: str,
    dst: Path,
    cutline: Path,
    dst_nodata: float,
) -> None:
    gdalwarp = shutil.which("gdalwarp")
    if gdalwarp is None:
        raise RuntimeError("gdalwarp not found on PATH (install GDAL).")
    cmd = [
        gdalwarp,
        "-of",
        "GTiff",
        "-t_srs",
        "EPSG:32611",
        "-cutline",
        str(cutline.resolve()),
        "-crop_to_cutline",
        "-dstnodata",
        str(dst_nodata),
        "-overwrite",
        src,
        str(dst.resolve()),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gdalwarp failed:\n{r.stderr or r.stdout}")


def _pixel_area_m2(transform) -> float:
    return abs(transform.a * transform.e)


def main() -> int:
    ap = argparse.ArgumentParser(description="TEMPO L2 → UTM clip → screen → ΔVCD mass")
    ap.add_argument("--nc", type=Path, required=True, help="Path to TEMPO_NO2_L2 *.nc file")
    ap.add_argument("--box", type=Path, default=DEFAULT_BOX, help="Study box shapefile (EPSG:32611)")
    ap.add_argument("--out-dir", type=Path, default=HERE, help="Output directory")
    ap.add_argument(
        "--mass-name",
        default="massno2-plant-clipped.tif",
        help="Output mass GeoTIFF filename (e.g. massno2-city-clipped.tif for Case 3)",
    )
    ap.add_argument("--qa-main-max", type=int, default=0, help="Keep QA flag <= this (0=normal only)")
    ap.add_argument("--cloud-max", type=float, default=0.3, help="Keep eff_cloud_fraction <= this")
    ap.add_argument(
        "--prefix",
        default="walnut_tempo",
        help="Prefix for intermediate GeoTIFFs (VCD, QA, cloud)",
    )
    args = ap.parse_args()

    if not args.nc.is_file():
        print(f"ERROR: NetCDF not found: {args.nc}", file=sys.stderr)
        return 1
    if not args.box.is_file():
        print(f"ERROR: Cutline not found: {args.box}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        t_vcd = tdir / f"{args.prefix}_vcd_utm.tif"
        t_qa = tdir / f"{args.prefix}_qa_utm.tif"
        t_cl = tdir / f"{args.prefix}_cloud_utm.tif"

        print("Warping VCD, QA, cloud to UTM 11N and clipping to study box …")
        _run_gdalwarp(_netcdf_uri(args.nc, SD_VCD), t_vcd, args.box, NODATA)
        _run_gdalwarp(_netcdf_uri(args.nc, SD_QA), t_qa, args.box, NODATA)
        _run_gdalwarp(_netcdf_uri(args.nc, SD_CLOUD), t_cl, args.box, NODATA)

        # Copy intermediates for debugging (optional)
        for src, name in (
            (t_vcd, f"{args.prefix}_vcd_troposphere_utm11_clipped.tif"),
            (t_qa, f"{args.prefix}_qa_main_utm11_clipped.tif"),
            (t_cl, f"{args.prefix}_eff_cloud_utm11_clipped.tif"),
        ):
            shutil.copy(src, args.out_dir / name)

        with rasterio.open(t_vcd) as ds:
            vcd = ds.read(1).astype(np.float64)
            v_nd = ds.nodata
            prof = ds.profile.copy()
            tr = ds.transform
            crs = ds.crs
        with rasterio.open(t_qa) as ds:
            qa = ds.read(1)
            if ds.shape != vcd.shape or ds.transform != tr:
                print("ERROR: QA grid mismatch vs VCD after clip.", file=sys.stderr)
                return 1
        with rasterio.open(t_cl) as ds:
            cloud = ds.read(1).astype(np.float64)
            if ds.shape != vcd.shape or ds.transform != tr:
                print("ERROR: Cloud grid mismatch vs VCD after clip.", file=sys.stderr)
                return 1

    qa_i = np.rint(qa).astype(np.int32)
    ok_qa = qa_i <= int(args.qa_main_max)
    ok_cloud = np.isfinite(cloud) & (cloud <= float(args.cloud_max))
    ok_vcd = np.isfinite(vcd) & (vcd > -1e20)
    if v_nd is not None and np.isfinite(v_nd):
        ok_vcd &= vcd != v_nd

    screen = ok_qa & ok_cloud & ok_vcd
    n_ok = int(np.count_nonzero(screen))
    if n_ok == 0:
        print("ERROR: No pixels pass QA + cloud + VCD. Relax thresholds or check granule.", file=sys.stderr)
        return 1

    vcd_bg = float(np.median(vcd[screen]))
    dvcd = np.where(screen, vcd - vcd_bg, np.nan)

    area_m2 = _pixel_area_m2(tr)
    area_cm2 = area_m2 * 1.0e4
    mass_kg = np.where(np.isfinite(dvcd), dvcd * area_cm2 / N_A * M_NO2_KG_PER_MOL, NODATA).astype(np.float32)

    prof.update(dtype="float32", nodata=NODATA, count=1)
    out_mass = args.out_dir / args.mass_name
    with rasterio.open(out_mass, "w", **prof) as dst:
        dst.write(mass_kg, 1)

    # uint8 mask
    mprof = prof.copy()
    mprof.update(dtype="uint8", nodata=None)
    out_mask = args.out_dir / f"{args.prefix}_mask_screen.tif"
    with rasterio.open(out_mask, "w", **mprof) as dst:
        dst.write(screen.astype(np.uint8), 1)

    print(f"VCD background (median over screened pixels): {vcd_bg:.6g} molecules/cm²")
    print(f"Screened pixels: {n_ok} / {screen.size}")
    print(f"Wrote {out_mass.name}")
    print(f"Wrote {out_mask.name}")
    print(f"Next: py -3 ../tempo_case_analysis.py {out_mass.name} --case-id case2_plant  # or case3_city")
    return 0


if __name__ == "__main__":
    sys.exit(main())
