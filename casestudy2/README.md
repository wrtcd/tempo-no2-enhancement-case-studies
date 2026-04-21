# Case 2 — Power plant (Walnut Creek Energy Park)

**Selected site:** **Walnut Creek Energy Park** — City of Industry, Los Angeles County. Approximate stack area (WGS84): **34.0087°N, −117.9449°W** (verify in QGIS before drawing the box).

**Status:** Site chosen; add TEMPO L2 granule + enhancement GeoTIFF clipped to the **same study box size as Case 1** (~9.65 km × ~9.65 km, ~93 km²), **centered on the plant**.

## Steps

1. Download **`TEMPO_NO2_L2` `*.nc`** covering Walnut Creek.
2. Run **[`preprocess_tempo_walnut.py`](preprocess_tempo_walnut.py)** (QA ≤ 0, `eff_cloud_fraction` ≤ 0.3, UTM 11N, clip to **`walnut-creek-study-box.shp`**) → **`massno2-plant-clipped.tif`**. See **[`CASE2_PREPROCESS.md`](CASE2_PREPROCESS.md)** for VCD/AMF notes and commands.
3. Fill [`case2_metadata.csv`](case2_metadata.csv) (granule path, times, QA from NetCDF).
4. Run: `py -3 ../tempo_case_analysis.py massno2-plant-clipped.tif --case-id case2_plant`
5. Run: `py -3 ../refresh_comparison_table.py`

Manual QGIS path: clip/reproject with the same QA/cloud rules as `eaton/scripts/tempo/screen_tempo_pixels.py`.

More context: [`PLANT_SITE_OPTIONS.md`](PLANT_SITE_OPTIONS.md).

## Inventory (optional)

Note EPA NEI / EIA facility ID in metadata or notes for context only.
