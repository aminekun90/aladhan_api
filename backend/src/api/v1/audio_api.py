from fastapi import APIRouter, Query
from src.core.repository_factory import RepositoryContainer
from src.domain import AudioRepository
from .models import AudioResponse, MessageResponse

router = APIRouter()

repos = RepositoryContainer()
audio_repo: AudioRepository = repos.audio_repo



@router.get("/audio")
def get_audio(
    name: str = Query(..., min_length=1),
) -> AudioResponse | MessageResponse:
    """
    Search audio by name and return the first match.
    """
    audio = audio_repo.get_audio_by_name(name)
    if audio:
        return AudioResponse(**audio.get_dict())
    return MessageResponse(message="Audio not found")


@router.get("/audio/list")
def get_audio_list() -> list[AudioResponse]:
    """
    List all available audio files.
    """
    audios = audio_repo.list_audios()
    return [AudioResponse(**audio.get_dict()) for audio in audios]