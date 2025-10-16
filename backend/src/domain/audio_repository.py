from abc import ABC, abstractmethod
from .models import Audio
from typing import Optional


class AudioRepository(ABC):
    @abstractmethod
    def add_audio(self, audio: Audio) -> None:
        ...
    
    @abstractmethod
    def delete_audio(self, name: str) -> None:
        ...
    @abstractmethod
    def get_audio_by_id(self, audio_id: int) -> Optional[Audio]:
        ...
    @abstractmethod
    def get_audio_by_name(self, name: str) -> Optional[Audio]:
        ...
    @abstractmethod
    def list_audios(self) -> list[Audio]:
        ...