import base64
from fastapi import APIRouter, Query,Response
from src.core.repository_factory import RepositoryContainer
from .models import AudioResponse, MessageResponse
from src.services.audio_service import AudioService
from fastapi.responses import StreamingResponse
from io import BytesIO
router = APIRouter()

repos = RepositoryContainer()

audio_service = AudioService(repos.audio_repo)


@router.get("/audio")
def get_audio(
    name: str = Query(..., min_length=1),
) -> AudioResponse | MessageResponse:
    """
    Search audio by name and return the first match.
    """
    audio = audio_service.get_audio_by_name(name)
    if audio:
        return AudioResponse(**audio.get_dict())
    return MessageResponse(message="Audio not found")


@router.get("/audio/list")
def get_audio_list() -> list[AudioResponse]:
    """
    List all available audio files.
    """
    audios = audio_service.list_audios()
    if audios is None:
        return []
    
    return [AudioResponse(id=audio.id, name=audio.name, blob=audio.blob) for audio in audios if audio is not None and audio.blob is not None and audio.name is not None and audio.id is not None]


@router.get("/audio_by_id/{audio_id}")
def get_audio_by_id(audio_id: int) -> AudioResponse | MessageResponse:
    """
    Get an audio file by its ID.
    """
    audio = audio_service.get_audio_by_id(audio_id)
    if audio:
        return AudioResponse(**audio.get_dict())
    return MessageResponse(message="Audio not found")

@router.get("/load_audios_from_data_folder")
def load_audios_from_data_folder() -> MessageResponse:
    """
    Load audio files from data/audio folder and add them to the database.
    """
    audio_service.load_audios_files_from_data_folder()
    return MessageResponse(message="Audios loaded successfully")

@router.get("/audio/{audio_name}")
def get_audio_blob(audio_name: str):
    audio = audio_service.get_audio_by_name(audio_name)
    if not audio or not audio.blob:
        return Response(status_code=404)

    blob_data = audio.blob

    # If blob_data is a string (likely Base64-encoded), decode it
    if isinstance(blob_data, str):
        try:
            blob_data = base64.b64decode(blob_data)
        except Exception:
            return Response(status_code=500, content="Invalid audio data")

    audio_stream = BytesIO(blob_data)

    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",  # standard for mp3
        headers={"Content-Disposition": f'inline; filename="{audio.name}"'}
    )