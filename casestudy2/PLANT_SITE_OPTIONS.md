# Case 2 — choosing a Southern California power plant

**Selected for this project: [Walnut Creek Energy Park](#1-walnut-creek-energy-park-strong-nox-signal-inland)** — see [`README.md`](README.md) and [`case2_metadata.csv`](case2_metadata.csv).

Use the **same box size** as Case 1 (~**9.65 km** sides, ~**93 km²**); center the box on the plant. Document the final choice in `case2_metadata.csv`.

## Recommended options (LA Basin / nearby)

### 1. Walnut Creek Energy Park (strong NOₓ signal, inland)

- **Location:** City of Industry, Los Angeles County  
- **Approx. coordinates (WGS84):** **34.0087°N, −117.9449°W** (GEM / stack area)  
- **Why:** Frequently highlighted in advocacy / inventory work for **high NOₓ** among California gas plants; 500 MW simple-cycle peakers. Good if you want a **clear “large point source”** story in the basin (verify emissions context in NEI/EIA for your year).  
- **Caveats:** Industrial corridor — **other** NOₓ sources (freeways, warehouses) inside the ~10 km box may mix with the plant signal; note in discussion.

### 2. AES Alamitos (Long Beach, coastal)

- **Location:** Long Beach  
- **Approx. coordinates:** search **“AES Alamitos Energy Center”** in maps (~**33.771°N, −118.101°W** — confirm before drawing the box).  
- **Why:** Large, well-known coastal station; often visible in regional NO₂ imagery.  
- **Caveats:** **Marine layer**, sea breeze, and **port/shipping** NO₂ nearby can complicate interpretation.

### 3. El Segundo Energy Center (coastal, dense urban edge)

- **Location:** El Segundo, LA County (coast)  
- **Approx. address:** 301 Vista Del Mar Blvd. — confirm lat/lon in QGIS.  
- **Why:** Big combined-cycle site; pairs conceptually with an **urban** Case 3 if you want “coastal energy + city” contrast.  
- **Caveats:** **LAX** and dense **Westside** traffic within tens of km — mixed sources.

## Practical selection rules

1. **TEMPO overpass:** Choose a granule with **low cloud**, good QA, and **solar geometry** similar to your Case 1 scene if possible.  
2. **Same processing** as Case 1 for enhancement mass (background subtraction, flags).  
3. **Document** facility name, coordinates of box center, and granule id in `case2_metadata.csv`.  
4. If the plant is **not** operating strongly that hour, enhancement may be weak — have a **backup date** or second candidate plant.

## Suggested default for “most active / high NOₓ” narrative

**Walnut Creek Energy Park** is a defensible first choice for **NOₓ prominence** in public reporting and inventories; **AES Alamitos** is a defensible choice for a **classic large coastal** generator. Pick based on whether you prefer **inland peaker** vs **coastal** meteorology.
