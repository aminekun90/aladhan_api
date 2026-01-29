import socket
from datetime import date, datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from src.calculations.adhan_calc import SCHEDULABLE_KEYS
from src.domain import DeviceRepository, SettingsRepository
from src.domain.models import Device, Settings
from src.schemas.log_config import LogConfig
from src.services.adhan_service import get_prayer_times
from src.services.freebox_service import FreeboxService
from src.services.soco_service import SoCoService
from src.utils.date_utils import get_tz

logger = LogConfig.get_logger()
DEFAULT_TZ = "Europe/Paris"
class DeviceService:
    _instance = None
    def __new__(cls,device_repository: DeviceRepository, settings_repository: SettingsRepository, debug: bool = False):
        cls._instance = super().__new__(cls)
        cls._instance._init_props(device_repository, settings_repository,debug)
        return cls._instance
    def _init_props(self, device_repository: DeviceRepository, settings_repository: SettingsRepository, debug: bool = False):
        """ Initialize class properties."""
        self.device_repository = device_repository
        self.settings_repository = settings_repository
        self.scheduler = BackgroundScheduler(timezone=DEFAULT_TZ)
        self.scheduler.start()
        self.debug = debug
        self.soco_service = SoCoService()
        self.freebox_service = FreeboxService()
        self.host_ip = self.get_local_ip()
        self.api_port = 8000
        logger.info(f"🌐 Host IP: {self.host_ip}:{self.api_port}")

    # ------------------------------
    # 🧩 Utilities
    # ------------------------------
    def get_device_by_id(self, device_id: int) -> Optional[Device]:
        return self.device_repository.get_device_by_id(device_id)

    def list_devices(self) -> list[Device]:
        return self.device_repository.list_devices()

    def upsert_devices_bulk(self, devices: list[Device]) -> None:
        """ Add multiple devices to the database."""
        return self.device_repository.upsert_devices_bulk(devices=devices)
    def get_local_ip(self) -> str:
        """Get the LAN IP address of the current machine (reachable by Sonos)."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn’t have to connect successfully, just needs to trigger routing
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip
    
    # ------------------------------
    # 🕌 Prayer Job
    # ------------------------------
    def _prayer_job(self, device: Device, prayer_name: str, settings: Settings):
        # Validate input
        if not device or not device.id:
            logger.info("❌ Missing device information, skipping job.")
            return
        if not settings or not settings.audio:
            logger.info(f"⚠️ No audio configured for {device.id}, skipping {prayer_name}.")
            return

        # Get audio name whether dict or ORM object
        if isinstance(settings.audio, dict):
            audio_name = settings.audio.get("name")
        else:
            audio_name = getattr(settings.audio, "name", None)

        if not audio_name:
            logger.info(f"⚠️ Missing audio name for {device.id}, skipping {prayer_name} call.")
            return

        # Build the playable URL
        port_part = f":{self.api_port}" if getattr(self, "api_port", None) else ""
        url = f"http://{self.host_ip}{port_part}/api/v1/audio/{audio_name}" 
        
        logger.info(f"🕌 It's time for {prayer_name} (Device {device.id}) -> playing {url}")

        # Trigger playback
        try:
            if device.type == "freebox_player":
                self.freebox_service.play_media(player_id=device.ip, media_url=url, volume=settings.volume)
            elif device.type == "sonos_player":
                self.soco_service.play_audio(device=device, url=url, volume=settings.volume)
            
        except Exception as e:
            logger.info(f"❌ Failed to play audio for device : name:{device.name} id: {device.id} \nwith error: {e}")


    # ------------------------------
    # 🧠 Debug Helpers
    # ------------------------------
    def debug_jobs(self):
        logger.debug("\n📅 === Current Scheduled Jobs ===")
        jobs = self.scheduler.get_jobs()
        if not jobs:
            logger.debug("No jobs scheduled.")
            return
        for job in jobs:
            logger.debug(f" - {job.id}: runs at {job.next_run_time}")
        logger.debug("=================================\n")

    # ------------------------------
    # 🕒 Date/Time Helpers
    # ------------------------------
    def _get_next_refresh_datetime(self, refresh_interval_minutes: Optional[int] = None) -> datetime:
        """Return next refresh datetime — either in N minutes or at 1 AM next day."""
        if refresh_interval_minutes is not None:
            return datetime.now() + timedelta(minutes=refresh_interval_minutes)
        tomorrow = datetime.now() + timedelta(days=1)
        return datetime.combine(tomorrow.date(), datetime.min.time()) + timedelta(hours=1)

    def _parse_prayer_datetime(self, time_str: str) -> datetime:
        """Convert '07:09:48 (CEST)' → datetime object for today."""
        clean_time = time_str.split()[0]  # remove "(CEST)"
        return datetime.combine(date.today(), datetime.strptime(clean_time, "%H:%M:%S").time())

    # ------------------------------
    # 🧹 Job Management
    # ------------------------------
    def clear_device_jobs(self, device_id: int):
        """Remove all jobs associated with a device."""
        for job in self.scheduler.get_jobs():
            if str(device_id) in job.id:
                self.scheduler.remove_job(job.id)
                if self.debug:
                    logger.info(f"🗑️ Removed job {job.id}")

    def _schedule_prayer_jobs(self, device: Device, ordered_timings: dict, force_refresh: bool,settings: Settings):
        """Add prayer jobs to the scheduler for this device."""
        now = datetime.now()
        for prayer_name, prayer_time in ordered_timings.items():
            prayer_datetime = self._parse_prayer_datetime(prayer_time)
            if prayer_datetime > now or force_refresh:
                job_id = f"device_{device.id}_{prayer_name}"
                self.scheduler.add_job(
                    self._prayer_job,
                    "date",
                    run_date=prayer_datetime,
                    id=job_id,
                    args=[device, prayer_name, settings],
                )
                logger.info(f"✅ Scheduled {prayer_name} at {prayer_datetime} (Device {device.id}) - job id: {job_id}")
        # display all scheduled jobs
        logger.info(f"📅 Scheduled prayers {self.scheduler.get_jobs()}")

    def _schedule_refresh_job(self, device: Device, refresh_interval_minutes: Optional[int]):
        """Schedule next refresh (default: at 1 AM next day, plus DST if applicable)."""
        next_refresh = self._get_next_refresh_datetime(refresh_interval_minutes)
        tz_name = get_tz()
        
        # Normal daily refresh
        self.scheduler.add_job(
            self.schedule_prayers_for_device,
            "date",
            run_date=next_refresh,
            id=f"refresh_device_{device.id}",
            args=[device],
        )
        logger.info(f"🔁 Next normal refresh at {next_refresh} (Device {device.id})")

        # Extra DST refresh if applicable
        dst_change_time = self._is_it_change_time(tz_name)
        if dst_change_time:
            self.scheduler.add_job(
                self.schedule_prayers_for_device,
                "date",
                run_date=dst_change_time,
                id=f"dst_refresh_device_{device.id}",
                args=[device],
            )
            logger.info(f"🕐 Extra DST refresh scheduled at {dst_change_time} (Device {device.id})")

        return next_refresh

    def _is_it_change_time(self, tz_name: Optional[str] = None) -> Optional[datetime]:
        """
        Detects if tonight involves a daylight saving time (DST) change
        for the given timezone (defaults to system or DEFAULT_TZ).

        Returns a datetime just before the change (02:59 local time if DST changes),
        or None if no DST transition occurs tonight.
        """
        try:
            tz_name = tz_name or get_tz() or DEFAULT_TZ
            tz = ZoneInfo(tz_name)

            now = datetime.now(tz)
            today = now.date()
            tomorrow = today + timedelta(days=1)

            # Midnight today and tomorrow
            start = datetime.combine(today, datetime.min.time(), tz)
            end = datetime.combine(tomorrow, datetime.min.time(), tz)

            # Compare UTC offsets
            offset_today = start.utcoffset()
            offset_tomorrow = end.utcoffset()

            if offset_today != offset_tomorrow:
                # Find approximate DST transition moment (binary search)
                low, high = start, end
                while (high - low) > timedelta(minutes=5):  # precision ±5min
                    mid = low + (high - low) / 2
                    if mid.utcoffset() == offset_today:
                        low = mid
                    else:
                        high = mid

                # We'll trigger the refresh a minute before the actual change
                change_time = high - timedelta(minutes=1)
                logger.info(f"⏰ DST change detected in {tz_name} around {high}. Refresh set for {change_time}.")
                return change_time
            logger.info(f"🌞 No DST change detected in {tz_name}.")
            return None

        except Exception as e:
            logger.warning(f"⚠️ DST check failed for tz={tz_name}: {e}")
            return None

    
    #-------------------------------
    # 📅 Schedule Prayer Times for all devices
    # ------------------------------
    
    def schedule_prayers_for_all_devices(self, refresh_interval_minutes: Optional[int] = None, force_refresh: bool = False)->list[dict]:
        """Schedules all prayer times for today for all devices."""
        schedule_devices = []
        logger.info("\n📅 Scheduling prayer times for all devices...")

        # If you need the IANA name (this part is system dependent)
        tz_string = get_tz()
        for device in self.list_devices():
            if not device.id:
                continue
            schedule_devices.append(self.schedule_prayers_for_device(
                device=device,
                refresh_interval_minutes=refresh_interval_minutes,
                force_refresh=force_refresh,
                tz=tz_string
            ))
        return schedule_devices
    # ----------------------------------
    # 📅 schedule prayers for one device
    # ----------------------------------
    def schedule_prayers_for_device(
        self,
        device: Device,
        refresh_interval_minutes: Optional[int] = None,
        force_refresh: bool = False,
        tz: Optional[str] = DEFAULT_TZ,
    ) -> dict:
        """Schedules all prayer times for today for this device."""
        if not device or not device.id:
            return {"status": "error", "message": "Missing device ID"}
        settings: Optional[Settings] = self.settings_repository.get_setting_by_device_id(device_id=device.id)
        if settings and not settings.enable_scheduler:
            logger.info(f"🚫 Scheduler is disabledfor device {device.name}" )
            self.clear_device_jobs(device.id)
            return {"status": "warning", "message": "Scheduler is disabled"}
        if not (settings and settings.city and settings.selected_method):
            logger.info(f"🚫 Missing settings for device {device.id} {device.ip} : {settings}")
            return {"status": "error", "message": "Missing settings for device"}

        # 🌍 Extract coordinates
        lat = settings.city.get("lat") if isinstance(settings.city, dict) else settings.city.lat
        lon = settings.city.get("lon") if isinstance(settings.city, dict) else settings.city.lon
        if not lat or not lon :
            return {"status": "error", "message": "Missing coordinates for device"}
        # 📅 Get prayer times
        logger.info(f"📅 Getting prayer times for device {device.id}")
        
        prayer_times = get_prayer_times(
            lat=lat or 0,
            lon=lon or 0,
            method=settings.selected_method,
            base_date=date.today(),
            tz=get_tz(),
            madhab="Shafi",
        )
        if not prayer_times:
            return {"status": "error", "message": "Failed to get prayer times"}

        ordered_timings = {k: prayer_times["times"][k] for k in SCHEDULABLE_KEYS}

        # 🧹 Remove previous jobs to avoid duplicates
        self.clear_device_jobs(device.id)

        # 🕌 Schedule prayer times
        self._schedule_prayer_jobs(device, ordered_timings, force_refresh, settings)

        # 🔁 Schedule refresh
        next_refresh = self._schedule_refresh_job(device, refresh_interval_minutes)

        if self.debug:
            self.debug_jobs()

        return {
            "status" : "success",
            "message": f"Prayers scheduled successfully for device {device.id}. Next refresh at {next_refresh}.",
            "prayers": ordered_timings,
            "tz"     : tz
        }
        
    def play_audio_in_device(self,  device_id: int):
        if  not device_id:
            return {"status": "error", "message": "Missing device ID"}
        # get setting by device id
        settings = self.settings_repository.get_setting_by_device_id(device_id=device_id)
        if not settings:
            return {"status": "error", "message": "Missing settings for device"}
        # get device by id
        device = self.get_device_by_id(device_id=device_id)
        if not device:
            return {"status": "error", "message": "Device not found"}
        # get audio by id
        audio = settings.audio
        if not audio:
            return {"status": "error", "message": "Audio not found"}
        
        # Build the playable URL
        port_part = f":{self.api_port}" if getattr(self, "api_port", None) else ""
        url = f"http://{self.host_ip}{port_part}/api/v1/audio/{audio.name}" 
       
        self.soco_service.play_audio(device, url=url,volume=settings.volume)

        return {"status": "success", "message": f"Audio played successfully for device {device_id}"}
