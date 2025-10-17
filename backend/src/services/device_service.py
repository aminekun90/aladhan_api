import socket
import time

from datetime import datetime, date, timedelta,timezone
from typing import Optional
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler

from src.domain.models import Device, Settings
from src.domain import DeviceRepository, SettingsRepository
from src.services.adhan_service import get_prayer_times
from src.calculations.adhan_calc import SCHEDULABLE_KEYS
from src.services.soco_service import SoCoService


class DeviceService:
    _instance = None
    def __new__(cls,device_repository: DeviceRepository, settings_repository: SettingsRepository, debug: bool = True):
        cls._instance = super().__new__(cls)
        cls._instance._init_props(device_repository, settings_repository,debug)
        return cls._instance
    def _init_props(self, device_repository: DeviceRepository, settings_repository: SettingsRepository, debug: bool = True):
        """ Initialize class properties."""
        self.device_repository = device_repository
        self.settings_repository = settings_repository
        self.scheduler = BackgroundScheduler(timezone="Europe/Paris")
        self.scheduler.start()
        self.debug = debug
        self.soco_service = SoCoService()
        self.host_ip = self.get_local_ip()
        self.api_port = 8000
        print(f"🌐 Host IP: {self.host_ip}:{self.api_port}")

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
            print("❌ Missing device information, skipping job.")
            return
        if not settings or not settings.audio:
            print(f"⚠️ No audio configured for {device.id}, skipping {prayer_name}.")
            return

        # Get audio name whether dict or ORM object
        if isinstance(settings.audio, dict):
            audio_name = settings.audio.get("name")
        else:
            audio_name = getattr(settings.audio, "name", None)

        if not audio_name:
            print(f"⚠️ Missing audio name for {device.id}, skipping {prayer_name}.")
            return

        # Build the playable URL
        port_part = f":{self.api_port}" if getattr(self, "api_port", None) else ""
        url = f"http://{self.host_ip}{port_part}/audio/{audio_name}"

        print(f"🕌 It's time for {prayer_name} (Device {device.id}) -> playing {url}")

        # Trigger playback
        try:
            self.soco_service.play_audio(device=device, url=url, volume=settings.volume)
        except Exception as e:
            print(f"❌ Failed to play audio for {device.id}: {e}")


    # ------------------------------
    # 🧠 Debug Helpers
    # ------------------------------
    def debug_jobs(self):
        print("\n📅 === Current Scheduled Jobs ===")
        jobs = self.scheduler.get_jobs()
        if not jobs:
            print("No jobs scheduled.")
            return
        for job in jobs:
            print(f" - {job.id}: runs at {job.next_run_time}")
        print("=================================\n")

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
                    print(f"🗑️ Removed job {job.id}")

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
                print(f"✅ Scheduled {prayer_name} at {prayer_datetime} (Device {device.id})")

    def _schedule_refresh_job(self, device_id: int, refresh_interval_minutes: Optional[int]):
        """Schedule next refresh (default: at 1 AM next day)."""
        next_refresh = self._get_next_refresh_datetime(refresh_interval_minutes)
        self.scheduler.add_job(
            self.schedule_prayers_for_device,
            "date",
            run_date=next_refresh,
            id=f"refresh_device_{device_id}",
            args=[device_id],
        )
        print(f"🔁 Next prayer schedule refresh at {next_refresh} (Device {device_id})")
        return next_refresh

    def get_tz(self):
        try:
            import tzlocal
            tz_string = tzlocal.get_localzone()
            print(tz_string.key)  # example Europe/Paris
        except Exception:   
                tz_string = ZoneInfo("UTC")
        return tz_string.key
    #-------------------------------
    # 📅 Schedule Prayer Times for all devices
    # ------------------------------
    
    def schedule_prayers_for_all_devices(self, refresh_interval_minutes: Optional[int] = None, force_refresh: bool = False)->list[dict]:
        """Schedules all prayer times for today for all devices."""
        schedule_devices = []
        print("\n📅 Scheduling prayer times for all devices...")

        # If you need the IANA name (this part is system dependent)
        tz_string = self.get_tz()
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
    # ------------------------------
    # 📅 schedule prayers for one device
    # ------------------------------
    def schedule_prayers_for_device(
        self,
        device: Device,
        refresh_interval_minutes: Optional[int] = None,
        force_refresh: bool = False,
        tz: Optional[str] = "Europe/Paris",
    ) -> dict:
        """Schedules all prayer times for today for this device."""
        if not device.id:
            return {"status": "error", "message": "Missing device ID"}
        settings: Optional[Settings] = self.settings_repository.get_setting_by_device_id(device_id=device.id)
        if settings and not settings.enable_scheduler:
            print("🚫 Scheduler is disabled")
            self.clear_device_jobs(device.id)
            return {"status": "error", "message": "Scheduler is disabled"}
        if not (settings and settings.city and settings.selected_method):
            return {"status": "error", "message": "Missing settings for device"}

        # 🌍 Extract coordinates
        lat = settings.city.get("lat") if isinstance(settings.city, dict) else settings.city.lat
        lon = settings.city.get("lon") if isinstance(settings.city, dict) else settings.city.lon
        if not lat or not lon :
            return {"status": "error", "message": "Missing coordinates for device"}
        # 📅 Get prayer times
        prayer_times = get_prayer_times(
            lat=lat or 0,
            lon=lon or 0,
            method=settings.selected_method,
            base_date=date.today(),
            tz=tz,
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
        next_refresh = self._schedule_refresh_job(device.id, refresh_interval_minutes)

        if self.debug:
            self.debug_jobs()

        return {
            "status" : "success",
            "message": f"Prayers scheduled successfully for device {device.id}. Next refresh at {next_refresh}.",
            "prayers": ordered_timings,
            "tz"     : tz
        }
