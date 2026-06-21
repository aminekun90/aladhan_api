"""Schemas for the Freebox AirMedia API (push media to a receiver, AirPlay-like)."""
from typing import Dict, Optional

from pydantic import BaseModel


class AirMediaReceiver(BaseModel):
    """An AirMedia receiver advertised by the Freebox."""
    name: str
    password_protected: bool = False
    capabilities: Dict[str, bool] = {}


class AirMediaPlayRequest(BaseModel):
    media_url: str
    password: Optional[str] = None


class AirMediaResult(BaseModel):
    status: str
    message: str
