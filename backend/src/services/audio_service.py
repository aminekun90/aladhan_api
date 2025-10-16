import os
from src.domain.models import Audio
from src.domain import AudioRepository
from typing import Optional

class AudioService:
    def __init__(self, audio_repo:AudioRepository,data_path="data/audio"):
        """Initialize the AudioService with the audio repository and data folder path."""
        self.audio_repo = audio_repo
        self.data_path = data_path
        self.load_audios_files_from_data_folder()
        
    def load_audios_files_from_data_folder(self):
        """Load audio files from data/audio folder and add them to the database."""
        # Open the audio files in data/audio folder and add them to the database as Audio objects
        for filename in os.listdir(self.data_path):
            if filename.endswith(".mp3"):
                audio = Audio(name=filename, blob=open(f"{filename}", "rb").read())
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