import os
import argparse
import sqlite3
import csv
import zipfile
import requests
from tqdm import tqdm

DATA_DIR = "../backend/src/data"
DB_FILE = os.path.join(DATA_DIR, "cities.db")
ZIP_FILE = os.path.join(DATA_DIR, "allCountries.zip")
TXT_FILE = os.path.join(DATA_DIR, "allCountries.txt")
URL = "https://download.geonames.org/export/dump/allCountries.zip"
BATCH_SIZE = 10_000


def download_file(url: str, dest: str):
    """Download with progress bar."""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc="Downloading GeoNames"
        ) as pbar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))


def extract_zip(zip_path: str, extract_to: str):
    print("Extracting ZIP...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)


def import_to_sqlite(db_file, txt_file):
    conn = sqlite3.connect(db_file if db_file else DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        name TEXT,
        lat REAL,
        lon REAL,
        country TEXT
    )
    """)

    print("Counting total lines...")
    with open(txt_file if txt_file else TXT_FILE, "r", encoding="utf-8") as f:
        total = sum(1 for _ in f)

    with open(txt_file if txt_file else TXT_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        batch = []
        for row in tqdm(reader, total=total, desc="Importing cities"):
            try:
                name = row[1]
                lat = float(row[4])
                lon = float(row[5])
                country = row[8]
                batch.append((name, lat, lon, country))
            except (IndexError, ValueError):
                continue

            if len(batch) >= BATCH_SIZE:
                cur.executemany("INSERT INTO cities VALUES (?, ?, ?, ?)", batch)
                conn.commit()
                batch.clear()

        if batch:
            cur.executemany("INSERT INTO cities VALUES (?, ?, ?, ?)", batch)
            conn.commit()

    print("Creating indexes...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_name ON cities(name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_country ON cities(country);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_name_country ON cities(name, country);")
    conn.commit()
    conn.close()
    print("✅ Import complete!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--download",
        default="https://download.geonames.org/export/dump/allCountries.zip",
        help="URL to download GeoNames data from"
    )
    parser.add_argument(
        "--output",
        default="../backend/src/data/cities.db",
        help="Output path for cities.db"
    )
    args = parser.parse_args()

    # update globals or just local variables
    data_dir = os.path.dirname(args.output)
    db_file = args.output
    zip_file = os.path.join(data_dir, "allCountries.zip")
    txt_file = os.path.join(data_dir, "allCountries.txt")

    os.makedirs(data_dir, exist_ok=True)

    if not os.path.exists(zip_file):
        download_file(args.download, zip_file)
    if not os.path.exists(txt_file):
        extract_zip(zip_file, data_dir)
    if not os.path.exists(db_file):
        import_to_sqlite(db_file, txt_file)
    else:
        print("Database already exists, skipping import.")


if __name__ == "__main__":
    main()
