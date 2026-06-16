import os
from typing import Optional

from src.domain import AudioRepository
from src.domain.models import Audio
from src.schemas.log_config import LogConfig

logger = LogConfig.get_logger()
class AudioService:
    def __init__(self, audio_repo:AudioRepository,data_path="src/data/audio"):
        """Initialize the AudioService with the audio repository and data folder path."""
        self.audio_repo = audio_repo
        self.data_path = data_path
        self.load_audios_files_from_data_folder()
        
    def load_audios_files_from_data_folder(self):
        """Load audio files from data/audio folder and add them to the database."""
        # Open the audio files in data/audio folder and add them to the database as Audio objects
        for filename in os.listdir(self.data_path):
            if filename.endswith(".mp3"):
                logger.info(f"Loading audio file: {filename}")
                # open file and read as bytes
                with open(f"{self.data_path}/{filename}", "rb") as f:
                    audio_bytes = f.read()
                if audio_bytes is None:
                    
                    continue
                else:
                    audio = Audio(name=filename,blob=audio_bytes)
                    # create Audio object
                    self.audio_repo.add_audio(audio)
    
    def list_audios(self)->list[Audio]:
        """List all audio files in the database."""
        return self.audio_repo.list_audios()
    
    def get_audio_by_name(self,name:str)->Optional[Audio]:
        """Retrieve an audio file by its name (case-insensitive)."""
        return self.audio_repo.get_audio_by_name(name)
    
    def get_audio_by_id(self,audio_id:int)->Optional[Audio]:
        """Retrieve an audio file by its ID."""
        return self.audio_repo.get_audio_by_id(audio_id)

    def save_uploaded_audio(self, filename: str, content: bytes) -> Audio:
        """Persist an uploaded MP3 to disk (for local/Bluetooth playback) and to
        the database (for the streamed /audio/{name} URL used by Sonos/Freebox)."""
        safe_name = os.path.basename(filename).strip()
        if not safe_name.lower().endswith(".mp3"):
            safe_name = f"{safe_name}.mp3"
        os.makedirs(self.data_path, exist_ok=True)
        with open(os.path.join(self.data_path, safe_name), "wb") as f:
            f.write(content)
        self.audio_repo.add_audio(Audio(name=safe_name, blob=content))
        logger.info(f"Saved uploaded audio: {safe_name} ({len(content)} bytes)")
        return self.audio_repo.get_audio_by_name(safe_name) or Audio(name=safe_name, blob=content)

    def delete_audio(self, name: str) -> None:
        """Remove an audio from the database and disk."""
        self.audio_repo.delete_audio(name)
        path = os.path.join(self.data_path, os.path.basename(name))
        if os.path.exists(path):
            os.remove(path)
        logger.info(f"Deleted audio: {name}")