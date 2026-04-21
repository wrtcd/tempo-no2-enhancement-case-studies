"""Copy key PNG outputs into results/figures/ for submission or thesis appendices.

Run from repo root: py -3 export_results_bundle.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "figures"

MAPPING: list[tuple[Path, str]] = [
    (HERE / "casestudy1" / "massno2-eaton-clipped_histogram_positive.png", "case1_smoke_histogram.png"),
    (HERE / "casestudy1" / "massno2-eaton-clipped_map.png", "case1_smoke_map.png"),
    (HERE / "casestudy2" / "massno2-plant-clipped_histogram_positive.png", "case2_plant_histogram.png"),
    (HERE / "casestudy2" / "massno2-plant-clipped_map.png", "case2_plant_map.png"),
    (HERE / "casestudy3" / "massno2-city-clipped_histogram_positive.png", "case3_city_histogram.png"),
    (HERE / "casestudy3" / "massno2-city-clipped_map.png", "case3_city_map.png"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for src, name in MAPPING:
        dst = OUT / name
        if not src.is_file():
            print(f"Skip (missing): {src}")
            continue
        shutil.copy2(src, dst)
        print(f"Copied -> {dst.relative_to(HERE)}")
        n += 1
    shutil.copy2(HERE / "results" / "comparison_table.csv", OUT / "comparison_table.csv")
    print(f"Copied -> {OUT / 'comparison_table.csv'}")
    print(f"Done ({n} figures + comparison_table).")


if __name__ == "__main__":
    main()
