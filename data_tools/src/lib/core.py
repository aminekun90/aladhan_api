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


def download_file(url: str, dest: str, force=False):
    """Download with progress bar."""
    if os.path.exists(dest) and not force:
        print(f"File {os.path.basename(dest)} already exists, skipping download.")
        return

    print(f"Downloading {url}...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with open(dest, "wb") as f, tqdm(
                total=total, unit="B", unit_scale=True, desc="Downloading"
            ) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
    except Exception as e:
        print(f"Error downloading: {e}")
        if os.path.exists(dest):
            os.remove(dest)
        raise


def extract_zip(zip_path: str, extract_to: str, txt_file=TXT_FILE):
    """Extract ZIP file."""
    if os.path.exists(txt_file):
        print("Text file already extracted, skipping extraction.")
        return
    
    print("Extracting ZIP...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_to)
    except zipfile.BadZipFile:
        print("Error: Zip file is corrupted.")


def import_to_sqlite(db_file, txt_file):
    """Import or Update data from text file into SQLite."""
    
    # NOTE: We removed the "if exists return" check here.
    # We want to run this logic every time to update data.

    print(f"Connecting to database: {db_file}")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # 1. Create table with 'geonameid' as a UNIQUE constraint.
    # This allows us to detect duplicates and update them.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        geonameid INTEGER UNIQUE,  -- Added unique ID from GeoNames
        name TEXT,
        lat REAL,
        lon REAL,
        country TEXT
    )
    """)

    # 2. Check if we need to migrate an old schema (if geonameid is missing)
    # This is a quick check to avoid crashes if you run this on your old DB
    cur.execute("PRAGMA table_info(cities)")
    columns = [info[1] for info in cur.fetchall()]
    if 'geonameid' not in columns:
        print("⚠️ Detected old schema. Dropping table to recreate with geonameid...")
        cur.execute("DROP TABLE cities")
        conn.commit()
        # Recreate
        cur.execute("""
        CREATE TABLE cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            geonameid INTEGER UNIQUE,
            name TEXT,
            lat REAL,
            lon REAL,
            country TEXT
        )
        """)

    print("Counting total lines in source file...")
    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            total = sum(1 for _ in f)
    except FileNotFoundError:
        print(f"❌ Error: Source file {txt_file} not found. Did download fail?")
        return

    print("Starting Import/Update...")
    
    # SQL for UPSERT (Update if exists, Insert if new)
    upsert_sql = """
    INSERT INTO cities (geonameid, name, lat, lon, country) 
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(geonameid) DO UPDATE SET
        name=excluded.name,
        lat=excluded.lat,
        lon=excluded.lon,
        country=excluded.country
    """

    with open(txt_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        batch = []
        
        for row in tqdm(reader, total=total, desc="Processing Cities"):
            try:
                # GeoNames columns: 0=id, 1=name, 4=lat, 5=lon, 8=country
                geonameid = int(row[0])
                name = row[1]
                lat = float(row[4])
                lon = float(row[5])
                country = row[8]
                
                batch.append((geonameid, name, lat, lon, country))
            except (IndexError, ValueError):
                continue

            if len(batch) >= BATCH_SIZE:
                cur.executemany(upsert_sql, batch)
                conn.commit()
                batch.clear()

        # Insert remaining
        if batch:
            cur.executemany(upsert_sql, batch)
            conn.commit()

    print("Creating/Verifying indexes...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_name ON cities(name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_country ON cities(country);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_name_country ON cities(name, country);")
    
    conn.commit()
    conn.close()
    print("✅ Import/Update complete!")


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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download of the ZIP file"
    )
    args = parser.parse_args()

    # Ensure absolute paths
    db_file = os.path.abspath(args.output)
    data_dir = os.path.dirname(db_file)
    zip_file = os.path.join(data_dir, "allCountries.zip")
    txt_file = os.path.join(data_dir, "allCountries.txt")

    os.makedirs(data_dir, exist_ok=True)

    # 1. Download (Skip if zip exists, unless force)
    download_file(args.download, zip_file, force=args.force)
    
    # 2. Extract
    extract_zip(zip_file, data_dir, txt_file=txt_file)
    
    # 3. Import / Update (Always runs)
    import_to_sqlite(db_file, txt_file)

    # Debug info
    print("\nData Directory Content:")
    for f in os.listdir(data_dir):
        print(f" - {os.path.join(data_dir, f)}")

if __name__ == "__main__":
    main()