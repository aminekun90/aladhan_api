from zoneinfo import ZoneInfo
from src.schemas.log_config import LogConfig

DEFAULT_TZ = "Europe/Paris"
logger = LogConfig.get_logger()
def get_tz()-> str:
        try:
            import tzlocal
            tz_string = tzlocal.get_localzone()
            logger.info(f"with tzlocal: {tz_string.key}")  # example Europe/Paris
        except Exception:
                logger.info(f"tzlocal not found, using {DEFAULT_TZ}")
                tz_string = ZoneInfo(DEFAULT_TZ)
        return tz_string.key