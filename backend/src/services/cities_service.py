# src/services/cities_service.py
import sqlite3
from typing import List, Dict, Optional

DB_PATH = "src/data/cities.db"

def search_cities(query: str, country: Optional[str] = None) -> List[Dict]:
    """
    Search cities by name (partial match) and optional country filter
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = "SELECT name, lat, lon, country FROM cities WHERE name LIKE ?"
    params = [f"%{query}%"]

    if country:
        sql += " AND country = ? GROUP BY name"
        params.append(country.upper())

    cur.execute(sql, params)
    results = [dict(row) for row in cur.fetchall()]
    conn.close()
    return results

def get_city(name: str) -> Optional[Dict]:
    """
    Get a city by exact name match
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT name, lat, lon, country FROM cities WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
