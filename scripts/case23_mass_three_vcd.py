"""
Case 2 / Case 3: for one TEMPO L2 granule and study box, write three enhancement mass
GeoTIFFs (kg/pixel) matching the plume / no2-plume-vcd-branches column definitions:

  operational: L2 tropospheric VCD, ΔVCD = VCD - median(VCD) over QA/cloud screen, then mass.
  vcd_check:   VCD_check = SCD / AMF (L2 support_data amf_troposphere), same median (screened), mass.
  vcd_adj:     VCD_adj = SCD / AMF_adj with AMF_adj from eaton-vcd-adj compute_amf_adj (same SCD/AMF
               convention as the adj repo), then same median, mass.

Requires: numpy, rasterio, GDAL (gdalwarp) on PATH; for vcd_adj, eaton-vcd-adj and dependencies.

Usage (from repo root):
  py -3 scripts/case23_mass_three_vcd.py --nc "PATH/TEMPO_...nc" --box casestudy2/walnut-creek-study-box.shp --out-dir casestudy2 --tag plant
  py -3 scripts/case23_mass_three_vcd.py --nc "..." --box casestudy3/la-study-box.shp --out-dir casestudy3 --tag city
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

SD_VCD = "/product/vertical_column_troposphere"
SD_SCD = "/support_data/fitted_slant_column"
SD_QA = "/product/main_data_quality_flag"
SD_CLOUD = "/support_data/eff_cloud_fraction"
SD_AMF = "/support_data/amf_troposphere"

N_A = 6.02214076e23
M_NO2_KG_PER_MOL = 46.0055e-3
NODATA = -1.0e30
EPS = 1e-30


def _work_root() -> Path:
    p = os.environ.get("TEMPO_CASE_WORK", "")
    if p:
        return Path(p)
    return Path(r"C:\Users\aeaturu\Desktop\WORK April 2026")


def _eaton_vcd_adj() -> Path:
    e = os.environ.get("EATON_VCD_ADJ_ROOT", "")
    if e:
        return Path(e)
    return _work_root() / "eaton-vcd-adj"


def _netcdf_uri(nc: Path, subds: str) -> str:
    p = nc.resolve()
    return f'NETCDF:"{p.as_posix()}":{subds}'


def _run_gdalwarp(src: str, dst: Path, cutline: Path, dst_nodata: float) -> None:
    gdalwarp = shutil.which("gdalwarp")
    if gdalwarp is None:
        raise RuntimeError("gdalwarp not found on PATH (install QGIS/GDAL).")
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


def _pixel_area_m2(tr: rasterio.Affine) -> float:
    return abs(tr.a * tr.e)


def _median_bg_mass(
    vcol: np.ndarray,
    screen: np.ndarray,
    tr: rasterio.Affine,
    prof: dict,
    out: Path,
) -> None:
    """ΔVCD = vcol - median(vcol|screen), then kg/pixel; off-screen = NODATA."""
    s = vcol[screen & np.isfinite(vcol) & (vcol > -1e20)]
    if s.size == 0:
        raise RuntimeError("No pixels pass screen for median background.")
    bg = float(np.median(s))
    dvcd = np.where(screen, vcol - bg, np.nan)
    area_cm2 = _pixel_area_m2(tr) * 1.0e4
    mass_kg = np.where(np.isfinite(dvcd), dvcd * area_cm2 / N_A * M_NO2_KG_PER_MOL, NODATA).astype(np.float32)
    prof2 = {**prof, "dtype": "float32", "nodata": NODATA, "count": 1, "compress": "deflate"}
    out.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out, "w", **prof2) as dst:
        dst.write(mass_kg, 1)


def _run_amf_adj(
    py: str, nc: Path, ref_vcd: Path, out_dir: Path, o_name: str = "tempo_amf_trop_adj_case.tif",
) -> Path:
    adj = _eaton_vcd_adj() / "scripts" / "compute_amf_adj.py"
    if not adj.is_file():
        raise FileNotFoundError(
            f"eaton-vcd-adj not found at {adj} (set EATON_VCD_ADJ_ROOT or install eaton-vcd-adj).",
        )
    out_path = out_dir / o_name
    cmd = [
        py,
        str(adj),
        "--nc",
        str(nc.resolve()),
        "--reference",
        str(ref_vcd.resolve()),
        "-o",
        str(out_path),
        "--out-dir",
        str(out_dir.resolve()),
        "--no-screen",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(out_dir))
    if r.returncode != 0:
        raise RuntimeError(f"compute_amf_adj failed:\n{r.stderr or r.stdout}")
    if not out_path.is_file():
        raise FileNotFoundError(f"Expected output missing: {out_path}")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Cases 2–3: three VCD mass rasters (operational, check, adj).")
    ap.add_argument("--nc", type=Path, required=True, help="TEMPO L2 NetCDF")
    ap.add_argument("--box", type=Path, required=True, help="Study box .shp (UTM 11N)")
    ap.add_argument("--out-dir", type=Path, required=True, help="e.g. casestudy2 or casestudy3")
    ap.add_argument("--tag", type=str, required=True, help="name tag: plant | city (used in filenames)")
    ap.add_argument("--prefix", type=str, default="case23", help="intermediate name prefix")
    ap.add_argument("--qa-main-max", type=int, default=0)
    ap.add_argument("--cloud-max", type=float, default=0.3)
    ap.add_argument(
        "--skip-vcd-adj",
        action="store_true",
        help="Skip AMF_adj and vcd_adj if compute_amf_adj cannot run.",
    )
    args = ap.parse_args()

    if not args.nc.is_file():
        print(f"ERROR: NetCDF not found: {args.nc}", file=sys.stderr)
        return 1
    if not args.box.is_file():
        print(f"ERROR: --box not found: {args.box}", file=sys.stderr)
        return 1

    args.out_dir = args.out_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    px = args.prefix

    t_vcd = args.out_dir / f"{px}_vcd_utm.tif"
    t_scd = args.out_dir / f"{px}_scd_utm.tif"
    t_amf = args.out_dir / f"{px}_amf_l2_utm.tif"
    t_qa = args.out_dir / f"{px}_qa_utm.tif"
    t_cl = args.out_dir / f"{px}_cloud_utm.tif"

    print("Warping L2 VCD, SCD, AMF, QA, cloud to UTM 11N and clipping …")
    _run_gdalwarp(_netcdf_uri(args.nc, SD_VCD), t_vcd, args.box, NODATA)
    _run_gdalwarp(_netcdf_uri(args.nc, SD_SCD), t_scd, args.box, NODATA)
    _run_gdalwarp(_netcdf_uri(args.nc, SD_AMF), t_amf, args.box, NODATA)
    _run_gdalwarp(_netcdf_uri(args.nc, SD_QA), t_qa, args.box, NODATA)
    _run_gdalwarp(_netcdf_uri(args.nc, SD_CLOUD), t_cl, args.box, NODATA)

    with rasterio.open(t_vcd) as ds:
        vcd = ds.read(1).astype(np.float64)
        v_nd = ds.nodata
        prof = ds.profile.copy()
        tr = ds.transform
    with rasterio.open(t_scd) as ds:
        scd = ds.read(1).astype(np.float64)
    with rasterio.open(t_amf) as ds:
        amf = ds.read(1).astype(np.float64)
    with rasterio.open(t_qa) as ds:
        qa = ds.read(1)
    with rasterio.open(t_cl) as ds:
        cloud = ds.read(1).astype(np.float64)

    qa_i = np.rint(qa).astype(np.int32)
    ok_qa = qa_i <= int(args.qa_main_max)
    ok_cloud = np.isfinite(cloud) & (cloud <= float(args.cloud_max))
    ok_vcd = np.isfinite(vcd) & (vcd > -1e20)
    if v_nd is not None and np.isfinite(v_nd):
        ok_vcd &= vcd != v_nd
    screen = ok_qa & ok_cloud & ok_vcd

    p2 = {**prof, "height": vcd.shape[0], "width": vcd.shape[1], "count": 1, "transform": tr}
    # --- operational ---
    out_op = args.out_dir / f"massno2-{args.tag}-operational.tif"
    _median_bg_mass(vcd, screen, tr, p2, out_op)
    print(f"Wrote {out_op.name}")

    # --- vcd_check = SCD / L2 amf_troposphere ---
    with np.errstate(invalid="ignore", divide="ignore"):
        vchk = np.where((amf > EPS) & np.isfinite(scd) & np.isfinite(amf), scd / np.maximum(amf, EPS), np.nan)
    vchk = np.where(screen, vchk, np.nan)
    out_ch = args.out_dir / f"massno2-{args.tag}-vcd_check.tif"
    _median_bg_mass(vchk, screen & np.isfinite(vchk), tr, p2, out_ch)
    print(f"Wrote {out_ch.name}")

    out_adj = args.out_dir / f"massno2-{args.tag}-vcd_adj.tif"
    if args.skip_vcd_adj:
        print("Skip vcd_adj (--skip-vcd-adj).", file=sys.stderr)
        return 0
    try:
        py = sys.executable
        amf_adj = _run_amf_adj(py, args.nc, t_vcd, args.out_dir, "tempo_amf_trop_adj_case.tif")
    except Exception as e:
        print(f"ERROR vcd_adj: {e}", file=sys.stderr)
        return 1

    with rasterio.open(amf_adj) as ds:
        aadj = ds.read(1).astype(np.float64)
    if aadj.shape != vcd.shape:
        print("ERROR: amf_adj shape mismatch", file=sys.stderr)
        return 1
    a_nd = -1.0e30
    aadjf = np.where(np.isfinite(aadj) & (aadj != a_nd) & (aadj > 0), aadj, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        vadj = np.where(
            np.isfinite(aadjf) & (aadjf > EPS) & np.isfinite(scd),
            scd / np.maximum(aadjf, EPS),
            np.nan,
        )
    vadj = np.where(screen, vadj, np.nan)
    sc2 = screen & np.isfinite(vadj)
    _median_bg_mass(vadj, sc2, tr, p2, out_adj)
    print(f"Wrote {out_adj.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
