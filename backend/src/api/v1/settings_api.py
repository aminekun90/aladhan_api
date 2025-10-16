from fastapi import APIRouter
from typing import List
from src.core.repository_factory import RepositoryContainer
from src.services.settings_service import SettingsService
from src.domain.models import Settings

from src.api.v1.models import SettingResponse, MessageResponse, SettingRequest,CreateSettingOfDeviceRequest

router = APIRouter()
repos = RepositoryContainer()

router = APIRouter(
    prefix="/settings",
)

settings_service = SettingsService(repos.setting_repo)

@router.get("/{id}", response_model=SettingResponse | MessageResponse)
def get_setting(id: int) -> SettingResponse | MessageResponse:
    """
    Get a setting by key.
    Returns: setting value as string
    """
    setting = settings_service.get_setting(id)
    if setting:
        return SettingResponse(**setting.get_dict())
    return MessageResponse(message="Setting not found")
    
@router.get("/", response_model=List[SettingResponse])
def list_settings() -> List[SettingResponse]:
    """
    List all settings.
    Returns: list of {key, value}
    """
    settings = settings_service.list_settings()
    return [SettingResponse(**s.get_dict()) for s in settings]


@router.put("/", response_model=MessageResponse)
def update_settings_bulk(settings: list[SettingRequest]) -> MessageResponse:
    """
    Update multiple settings in bulk.
    Example input: 
    """
    
    settings_service.update_settings_bulk( [Settings(**s.get_dict(),audio=None,device=None,city=None) for s in settings])
    return MessageResponse(message="Settings updated successfully")


# create empty settings
@router.put("/create_settings_of_device", response_model=SettingResponse)
def create_settings_of_device(request: CreateSettingOfDeviceRequest) -> SettingResponse:
    """
    Create a new setting in the database for a device.
    """
    settings = settings_service.create_setting_of_device(request.device_id)
    return SettingResponse(**settings.get_dict())
    