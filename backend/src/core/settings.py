class Settings:
    APP_NAME: str = "Adhan API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Prayer times calculation API (Python FastAPI implementation)"
    DEBUG: bool = False
    CALCULATIONS_METHOD: str = "MWL"
    CALCULATIONS_MADHAB: str = "Shafi"
    DEVICE:dict = {
        "volume": 25,
    }
    enable_scheduler: bool = True
    adhan_file_binary: str = "adhan"
    country_code: str = "FR"
    longitude: float = 2.3488
    latitude: float = 48.8534
    timezone: str = "Europe/Paris"

settings = Settings()
