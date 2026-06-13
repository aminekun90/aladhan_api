# Maintenance scripts

## build_cities_db.py — slim the cities database

The default `src/data/cities.db` ships the **entire** GeoNames `allCountries`
feature dump (~13.4M rows / ~1.5 GB) plus the raw `allCountries.txt` (~1.6 GB)
and `.zip` (~400 MB). This causes:

- huge disk usage (~3.5 GB total),
- duplicate-laden, slow city search (every feature, not just cities).

This script rebuilds a compact `cities` table keeping only **populated places**
(GeoNames feature class `P`) above a population threshold, deduped by
`(name, country)`, inserted in descending population order so prefix search
returns the largest matching city first.

Result: **~129k cities, ~11 MB** (≈130× smaller) at `--min-population 1000`.

### Build a standalone DB (safe, non-destructive)

```bash
cd backend
uv run python scripts/build_cities_db.py \
  --source src/data/allCountries.txt \
  --out src/data/cities_compact.db \
  --min-population 1000
```

### Adopt it in the live app DB

`cities.db` also holds app tables (devices/settings/audio), so rebuild only the
`cities` table in place. **Stop the API first** (the file must not be open):

```bash
# 1. stop the uvicorn server
uv run python scripts/build_cities_db.py \
  --source src/data/allCountries.txt \
  --target src/data/cities.db --in-place \
  --min-population 1000
# 2. restart the server
```

After adopting, the raw `allCountries.txt` / `.zip` are no longer needed at
runtime and can be deleted to reclaim ~2 GB (they are already git-ignored).

Lower `--min-population` (e.g. `500`) for more small towns at the cost of size.
