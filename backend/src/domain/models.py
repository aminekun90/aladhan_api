from dataclasses import dataclass

@dataclass
class City:
    """
    Domain model for a city.
    This is independent of any database or persistence mechanism.
    """
    id: int | None         # Primary key (can be None before saving to DB)
    name: str              # City name
    lat: float             # Latitude
    lon: float             # Longitude
    country: str           # ISO country code, e.g. "FR"
    
    def get_dict(self)->dict:
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "country": self.country
        }


@dataclass
class Setting:
    """
    Domain model for a setting.
    """
    id: int | None         # Primary key (can be None before saving to DB)
    key: str               # Setting key
    value: str             # Setting value
    
    def get_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value
        }
    
@dataclass
class Device:
    """
    Domain model for a device.
    """
    id: int | None         # Primary key (can be None before saving to DB)
    name: str              # Device name
    ip: str                # Device IP address
    raw_data: str | None   # Raw data from the device (can be None)
    
    def get_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "raw_data": self.raw_data
        }