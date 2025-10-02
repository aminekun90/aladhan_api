# Adhan API

**Adhan API** is a Python FastAPI project that calculates Islamic prayer times **completely from scratch**, without relying on external APIs.  
It supports multiple calculation methods, different madhab options for Asr, and works for any location around the globe.

Everything runs locally — no internet connection required.

---

## Features

- Calculate Fajr, Sunrise, Dhuhr, Asr, Maghrib, and Isha
- Supports multiple calculation methods:
  - MWL (Muslim World League)
  - ISNA
  - Umm al-Qura (Makkah)
  - Egyptian, Karachi, Tehran, Jafari,
  - etc...
- Madhab selection for Asr: Shafi (factor=1) or Hanafi (factor=2)
- Timezone-aware results
- Fully local, no external API calls
- Clean architecture for easy maintenance and extension
- FastAPI integration with auto-generated docs

---

## Project Structure

adhan-api/
├── pyproject.toml
├── README.md
├── src/
│ └── adhan/
│ ├── main.py # FastAPI entrypoint
│ ├── api/ # Routes
│ ├── core/ # Configs & constants
│ ├── services/ # Business logic
│ ├── calculations/ # Astronomy & prayer math
│ └── domain/ # Data models
└── tests/ # Unit & integration tests

---

## Installation

> Requires Python 3.12+  

1. Clone the repository:

```bash
git clone https://github.com/yourusername/adhan-api.git
cd adhan-api
```

Usage
Run the FastAPI server:

```bash
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Visit the API docs:

```bash
http://127.0.0.1:8000/docs
```

Example request:

```bash
GET /api/v1/prayer-times?lat=48.8566&lon=2.3522&day=2025-10-02&method=MWL&madhab=Shafi&tz=Europe/Paris
```

Example JSON response:

```json
{
  "date": "2025-10-02",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "method": "MWL",
  "madhab": "Shafi",
  "times": {
    "fajr": "2025-10-02T05:42:00+02:00",
    "sunrise": "2025-10-02T07:20:00+02:00",
    "dhuhr": "2025-10-02T12:58:00+02:00",
    "asr": "2025-10-02T15:28:00+02:00",
    "sunset": "2025-10-02T18:36:00+02:00",
    "maghrib": "2025-10-02T18:36:00+02:00",
    "isha": "2025-10-02T19:54:00+02:00"
  }
}
```

Extending Calculation Methods
You can add new calculation methods or override angles by editing the presets dictionary in:

```bash
src/adhan/calculations/adhan_calc.py
```

Example:

```python
presets['CustomMethod'] = {'fajr': 16.0, 'isha': ('mins', 90)}

```

## Testing

```bash
pytest tests/
```

## Notes

- High-latitude locations may return null for some prayer times when the sun does not reach the required angle.
- The project follows clean architecture principles:
- calculations → pure math & astronomy
  - services → business logic
  - api → REST endpoints
  - domain → Pydantic models

## License

MIT License
© 2025 Amine Bouzahar
