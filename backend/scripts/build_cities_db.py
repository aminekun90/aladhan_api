#!/usr/bin/env python3
"""Build a compact cities table from the GeoNames allCountries dump.

The shipped database carries the *entire* GeoNames feature dump (~13M rows,
~1.5 GB) — every mountain, stream and farm — which is why city search is slow,
full of duplicates, and the file is huge. This rebuilds a `cities` table that
keeps only real populated places (feature class "P") above a population
threshold, deduped by (name, country), inserted in descending population order
so prefix search naturally surfaces the largest city first.

Usage:
    # Build a standalone compact DB (safe, non-destructive):
    uv run python scripts/build_cities_db.py \
        --source src/data/allCountries.txt --out src/data/cities_compact.db

    # Rebuild the cities table in-place in the live app DB (stop the server first):
    uv run python scripts/build_cities_db.py \
        --source src/data/allCountries.txt --target src/data/cities.db --in-place

GeoNames columns (tab-separated):
    0 geonameid 1 name 2 asciiname 3 alternatenames 4 lat 5 lon
    6 feature_class 7 feature_code 8 country_code ... 14 population ...
"""
import argparse
import os
import sqlite3
import sys

MIN_POPULATION_DEFAULT = 1000


def iter_cities(source: str, min_population: int):
    with open(source, encoding="utf-8") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 15 or cols[6] != "P":
                continue
            try:
                population = int(cols[14] or 0)
            except ValueError:
                continue
            if population < min_population:
                continue
            name = cols[1].strip()
            if not name:
                continue
            try:
                lat, lon = float(cols[4]), float(cols[5])
            except ValueError:
                continue
            yield name, lat, lon, cols[8].strip(), population


def build(source: str, min_population: int):
    best: dict[tuple, tuple] = {}
    scanned = 0
    for name, lat, lon, country, population in iter_cities(source, min_population):
        scanned += 1
        key = (name.upper(), country.upper())
        if key not in best or population > best[key][4]:
            best[key] = (name, lat, lon, country, population)
        if scanned % 500_000 == 0:
            print(f"  …scanned {scanned:,} populated places, kept {len(best):,}", file=sys.stderr)
    # Descending population so search (no ORDER BY) returns big cities first.
    return sorted(best.values(), key=lambda c: c[4], reverse=True)


def write_table(conn: sqlite3.Connection, rows):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cities")
    cur.execute(
        "CREATE TABLE cities ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, lat REAL NOT NULL, lon REAL NOT NULL, country TEXT NOT NULL)"
    )
    cur.executemany(
        "INSERT INTO cities (name, lat, lon, country) VALUES (?, ?, ?, ?)",
        [(name, lat, lon, country) for name, lat, lon, country, _pop in rows],
    )
    cur.execute("CREATE INDEX idx_name ON cities(name)")
    cur.execute("CREATE INDEX idx_country ON cities(country)")
    cur.execute("CREATE INDEX idx_name_country ON cities(name, country)")
    conn.commit()
    cur.execute("VACUUM")
    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default="src/data/allCountries.txt", help="GeoNames allCountries.txt")
    parser.add_argument("--out", help="Write a fresh standalone sqlite DB to this path")
    parser.add_argument("--target", help="Existing app DB to rebuild the cities table in (use with --in-place)")
    parser.add_argument("--in-place", action="store_true", help="Rebuild cities table inside --target")
    parser.add_argument("--min-population", type=int, default=MIN_POPULATION_DEFAULT)
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Source not found: {args.source}", file=sys.stderr)
        return 1
    if not (args.out or (args.in_place and args.target)):
        print("Provide --out PATH, or --in-place --target PATH", file=sys.stderr)
        return 2

    print(f"Filtering populated places (population ≥ {args.min_population:,}) from {args.source}…", file=sys.stderr)
    rows = build(args.source, args.min_population)
    print(f"Kept {len(rows):,} unique cities.", file=sys.stderr)

    db_path = args.target if args.in_place else args.out
    conn = sqlite3.connect(db_path)
    try:
        write_table(conn, rows)
    finally:
        conn.close()
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"Wrote {len(rows):,} cities to {db_path} ({size_mb:.1f} MB).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
