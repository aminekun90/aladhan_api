from typing import List, Optional
from src.adapters.base import SQLRepositoryBase
from src.domain import AudioRepository
from src.domain.models import Audio
from src.adapters.models import AudioTable
from src.schemas.log_config import LogConfig

logger = LogConfig.get_logger()

class SQLiteAudioRepository(SQLRepositoryBase, AudioRepository):
    """SQLite implementation of AudioRepository."""

    def __init__(self, db_path: str = "sqlite:///src/data/cities.db"):
        super().__init__(db_path)

    def get_audio_by_name(self, name: str) -> Optional[Audio]:
        """Retrieve an audio file by its name (case-insensitive)."""
        with self.session_maker() as session:
            audio = session.query(AudioTable).filter(AudioTable.name.ilike(name)).first()
            if audio:
                return Audio(**audio.get_dict())
        return None

    def get_audio_by_id(self, audio_id: int) -> Optional[Audio]:
        """Retrieve an audio file by its ID."""
        with self.session_maker() as session:
            audio = session.query(AudioTable).filter(AudioTable.id == audio_id).first()
            if audio:
                return Audio(**audio.get_dict())
        return None

    def add_audio(self, audio: Audio) -> None:
        """
            Add a new audio file to the database if the name exists already update it.
            
            This method checks if the name is unique
            
            Args:
                audio (Audio): The audio file to add to the database.
        """
        with self.session_maker() as session:
            # find the audio by name and update it if it already exists
            existing_audio = (
                session.query(AudioTable)
                .filter(AudioTable.name == audio.name)
                .first()
            )
            if existing_audio:
                if audio.blob is not None and existing_audio.blob is not None and audio.blob != existing_audio.blob:
                    existing_audio.blob = audio.blob
                    logger.info(f"Updating audio {audio.name}")
                else:
                    logger.info(f"Audio {audio.name} already exists in the database, skipping")
                
                session.commit()
                return
            session.add(AudioTable(**audio.get_dict()))
            session.commit()

    def add_audios_bulk(self, audios: List[Audio]) -> None:
        """Add multiple audio files in one transaction."""
        with self.session_maker() as session:
            session.add_all([AudioTable(**a.get_dict()) for a in audios])
            session.commit()

    def update_audio(self, audio: Audio) -> None:
        """Update an existing audio file by ID."""
        with self.session_maker() as session:
            existing_audio = (
                session.query(AudioTable)
                .filter(AudioTable.id == audio.id)
                .first()
            )
            if existing_audio:
                for field, value in audio.get_dict().items():
                    setattr(existing_audio, field, value)
                session.commit()

    def update_audios_bulk(self, audios: List[Audio]) -> None:
        """Update or insert multiple audio files (bulk upsert)."""
        with self.session_maker() as session:
            for audio in audios:
                existing_audio = (
                    session.query(AudioTable)
                    .filter(AudioTable.id == audio.id)
                    .first()
                )
                if existing_audio:
                    for field, value in audio.get_dict().items():
                        setattr(existing_audio, field, value)
                else:
                    session.add(AudioTable(**audio.get_dict()))
            session.commit()

    def delete_audio(self, name: str) -> None:
        """Delete an audio file by its name."""
        with self.session_maker() as session:
            audio = session.query(AudioTable).filter(AudioTable.name == name).first()
            if audio:
                session.delete(audio)
                session.commit()

    def delete_audio_by_id(self, audio_id: int) -> None:
        """Delete an audio file by its ID."""
        with self.session_maker() as session:
            audio = session.query(AudioTable).filter(AudioTable.id == audio_id).first()
            if audio:
                session.delete(audio)
                session.commit()

    def list_audios(self) -> List[Audio]:
        """List all audio files in the database."""
        with self.session_maker() as session:
            audios = session.query(AudioTable).all()
            return [Audio(**a.get_dict()) for a in audios]
