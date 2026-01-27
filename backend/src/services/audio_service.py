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