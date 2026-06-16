import { getNearestCity, getSettings } from "@/api/apiPrayer";
import { DateCalendarComponent } from '@/components/Calendar';
import { DateClock } from "@/components/Clock";
import { DevicesComponent } from "@/components/DevicesComponent";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { MihrabArch } from "@/components/MihrabArch";
import { PrayersComponent } from "@/components/PrayersComponent";
import { SectionHeading } from "@/components/SectionHeading";
import { SettingsDialog } from '@/components/SettingsDialog';
import { DEFAULT_COORD } from "@/const";
import { useGeolocation } from "@/hooks/useGeolocation";
import { theme } from "@/theme";
import { ToastContainer, useToast } from '@aminekun90/react-toast';
import BluetoothSearchingIcon from '@mui/icons-material/BluetoothSearching';
import InfoIcon from '@mui/icons-material/Info';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import PlaceOutlinedIcon from '@mui/icons-material/PlaceOutlined';
import SyncIcon from '@mui/icons-material/Sync';
import { Box, CircularProgress, CssBaseline, IconButton, Stack, ThemeProvider, Tooltip, Typography } from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import packageJson from '../package.json';
import { createDeviceSettings, getConnectedBluetooth, getDevices, getSoCoDevices, scanBluetooth, scheduleAllDevices } from "./api/apiDevice";
import { AboutDialog } from "./components/about";
import { Settings } from "./models/Settings";
import { Device } from "./models/device";

function App() {
  const { t } = useTranslation();
  const { show } = useToast();
  const queryClient = useQueryClient();

  const notifySuccess = (title: string, message: string) => {
    show({ type: 'success', title, message, position: 'top-right', duration: 3000, progressBar: true });
  };

  const [currentHijirDate, setCurrentHijirDate] = useState<string>("");
  const [isAboutOpen, setIsAboutOpen] = useState<boolean>(false);
  const [isSettingOpen, setIsSettingOpen] = useState<boolean>(false);
  const [currentDeviceIp, setCurrentDeviceIp] = useState<string | number | null | undefined>();
  const [currentSetting, setCurrentSetting] = useState<Settings | null>(null);

  const { data: devices, error: deviceError, isLoading: deviceLoading } = useQuery({
    queryKey: ["devices"],
    queryFn: getDevices,
  });
  const { data: socoDevices, error: socoDevicesError, isLoading: socoLoading } = useQuery({
    queryKey: ["socoDevices"],
    queryFn: getSoCoDevices,
  });
  const { data: settings, error: settingsError, isLoading: settingsLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: getSettings,
  });
  const { data: connectedBt } = useQuery({
    queryKey: ["connectedBluetooth"],
    queryFn: getConnectedBluetooth,
    refetchInterval: 30000,
  });

  const scheduleAllDevicesMutation = useMutation({
    mutationFn: () => scheduleAllDevices(),
    onSuccess: () => notifySuccess(t('toast.scheduled.title'), t('toast.scheduled.message')),
  });
  const syncPrayers = () => {
    notifySuccess(t('toast.synced.title'), t('toast.synced.message'));
    scheduleAllDevicesMutation.mutate();
  };

  const scanBluetoothMutation = useMutation({
    mutationFn: () => scanBluetooth(),
    onSuccess: (found) => {
      if (found.length > 0) {
        notifySuccess(t('toast.bluetooth'), t('bluetooth.found', { count: found.length }));
        queryClient.invalidateQueries({ queryKey: ["devices"] });
      } else {
        show({
          type: 'info', title: t('toast.bluetooth'), message: t('bluetooth.noneFound'),
          position: 'top-right', duration: 5000, progressBar: true,
        });
      }
    },
    onError: () => {
      show({
        type: 'error', title: t('toast.bluetooth'), message: t('bluetooth.scanFailed'),
        position: 'top-right', duration: 5000, progressBar: true,
      });
    },
  });

  const createSettingMutation = useMutation({
    // Auto-provisions default settings when a device without settings is selected.
    // This is not a user "save", so it stays silent.
    mutationFn: (device: Device) => createDeviceSettings(device.getId()),
    onSuccess: (data: Settings | null) => {
      if (data) setCurrentSetting(data);
    },
  });

  useEffect(() => {
    const syncSelectedSetting = () => {
      if (settings && settings.length > 0 && !settingsLoading) {
        setCurrentSetting(settings.find(s => s.device?.getIp() === currentDeviceIp) || null);
      }
    };
    syncSelectedSetting();
  }, [settings, settingsLoading, deviceLoading, currentDeviceIp, settingsError]);

  // Select the always-available "this device" player by default, so the adhan
  // plays on the host out of the box when nothing else is chosen.
  useEffect(() => {
    const selectLocalByDefault = () => {
      if (currentDeviceIp != null || deviceLoading || !devices?.length) return;
      const local = devices.find(d => d.type === "local_player");
      if (!local) return;
      setCurrentDeviceIp(local.getIp());
      const found = settings?.find(s => s.device?.getIp() === local.getIp());
      if (found) setCurrentSetting(found);
      else createSettingMutation.mutate(local);
    };
    selectLocalByDefault();
  }, [devices, deviceLoading, settings, currentDeviceIp, createSettingMutation]);

  const { coords: geoCoords, status: geoStatus, request: requestLocation } = useGeolocation();

  // Reverse-geocode the GPS position to a city name for display.
  const { data: nearestCity } = useQuery({
    queryKey: ["nearestCity", geoCoords?.lat, geoCoords?.lon],
    queryFn: () => getNearestCity(geoCoords!.lat, geoCoords!.lon),
    enabled: !!geoCoords,
  });

  // Coordinate precedence: an explicitly configured city wins; otherwise use the
  // device's GPS position; finally fall back to the default location.
  const hasCity = currentSetting?.city?.lat != null && currentSetting?.city?.lon != null;
  const coord = hasCity
    ? { lat: currentSetting!.city!.lat, lon: currentSetting!.city!.lon }
    : (geoCoords ?? DEFAULT_COORD);
  const locationLabel = hasCity
    ? `${currentSetting?.city?.name ?? ""} · ${currentSetting?.city?.country ?? ""}`
    : geoCoords
      ? (nearestCity ? `${nearestCity.name} · ${nearestCity.country}` : t('location.myPosition'))
      : t('location.default');

  const selectDevice = (device: Device) => {
    // Toggle: clicking the selected device again deselects it.
    if (currentDeviceIp === device.getIp()) {
      setCurrentDeviceIp(null);
      setCurrentSetting(null);
      return;
    }
    setCurrentDeviceIp(device.getIp());
    const found = settings?.find(s => s.device?.getIp() === device.getIp());
    if (found) setCurrentSetting(found);
    else createSettingMutation.mutate(device);
  };

  const openDeviceSettings = (device: Device) => {
    if (currentDeviceIp !== device.getIp()) selectDevice(device);
    setIsSettingOpen(true);
  };

  return (
    <ThemeProvider theme={theme}>
      <ToastContainer />
      <CssBaseline />

      <Box sx={{ minHeight: "100vh", width: "100%", display: "flex", flexDirection: "column" }}>
        {/* Header / wordmark + actions */}
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          sx={{ px: { xs: 2, md: 5 }, py: 2.5, position: "sticky", top: 0, zIndex: 10, backdropFilter: "blur(6px)" }}
        >
          <Stack direction="row" alignItems="center" spacing={1.25}>
            <Box sx={{ width: 10, height: 18, borderRadius: "50% 50% 0 0 / 70% 70% 0 0", border: "1.5px solid var(--brass)", borderBottom: "none" }} />
            <Typography sx={{ fontFamily: "var(--font-display)", fontSize: "1.25rem", letterSpacing: "0.04em", color: "var(--parchment)" }}>
              Aladhan
            </Typography>
          </Stack>

          <Stack direction="row" spacing={0.5}>
            {!deviceLoading && !!devices?.length && (
              <Tooltip title={t('nav.sync')}><IconButton onClick={syncPrayers}><SyncIcon /></IconButton></Tooltip>
            )}
            <Tooltip title={t('nav.scanBluetooth')}>
              <span>
                <IconButton onClick={() => scanBluetoothMutation.mutate()} disabled={scanBluetoothMutation.isPending}>
                  <BluetoothSearchingIcon />
                </IconButton>
              </span>
            </Tooltip>
            <LanguageSwitcher />
            <Tooltip title={t('nav.about')}><IconButton onClick={() => setIsAboutOpen(true)}><InfoIcon /></IconButton></Tooltip>
          </Stack>
        </Stack>

        {/* Hero */}
        <Box sx={{ position: "relative", textAlign: "center", px: 2, pt: { xs: 8, md: 11 }, pb: { xs: 4, md: 6 } }}>
          <MihrabArch />
          <Box sx={{ position: "relative", zIndex: 1, animation: "rise .8s ease both" }}>
            <DateClock />
            {currentHijirDate && (
              <Typography
                dir="rtl"
                sx={{ fontFamily: "var(--font-arabic)", fontSize: { xs: "1.7rem", md: "2.2rem" }, color: "var(--brass-bright)", mt: 2.5 }}
              >
                {currentHijirDate}
              </Typography>
            )}
            <Stack direction="row" alignItems="center" justifyContent="center" spacing={0.5} sx={{ mt: 1.5, color: "var(--mist)" }}>
              <PlaceOutlinedIcon sx={{ fontSize: "1rem" }} />
              <Typography sx={{ fontSize: "0.85rem", letterSpacing: "0.04em" }}>{locationLabel}</Typography>
              <Tooltip title={geoStatus === "denied" ? t('location.denied') : t('location.useMyLocation')}>
                <IconButton size="small" onClick={requestLocation} sx={{ ml: 0.5 }}>
                  <MyLocationIcon sx={{ fontSize: "1rem", color: geoCoords ? "var(--brass)" : "inherit" }} />
                </IconButton>
              </Tooltip>
            </Stack>
          </Box>
        </Box>

        {/* Content */}
        <Stack spacing={{ xs: 6, md: 9 }} sx={{ px: { xs: 2, md: 5 }, pb: 8, width: "100%", maxWidth: 1200, mx: "auto" }}>
          {settingsLoading && <Box sx={{ textAlign: "center" }}><CircularProgress sx={{ color: "var(--brass)" }} /></Box>}

          <Box component="section">
            <SectionHeading>{t('sections.prayerTimes')}</SectionHeading>
            <PrayersComponent coord={coord} updateDate={setCurrentHijirDate} />
          </Box>

          <Box component="section">
            <SectionHeading>{t('sections.devices')}</SectionHeading>
            {deviceLoading ? (
              <Box sx={{ textAlign: "center" }}><CircularProgress sx={{ color: "var(--brass)" }} /></Box>
            ) : deviceError ? (
              <Typography sx={{ textAlign: "center", color: "var(--mist)" }}>{t('devices.errorFetching')}</Typography>
            ) : (
              <>
                {/* Render DB devices (incl. 'Cet appareil') immediately; Sonos
                    discovery only refines availability and runs in the background. */}
                <DevicesComponent
                  devices={devices ?? []}
                  soCoDevices={socoDevices ?? []}
                  connectedBtMacs={connectedBt ?? []}
                  selectedIp={currentDeviceIp}
                  onClick={selectDevice}
                  onOpenSettings={openDeviceSettings}
                />
                {socoLoading && !socoDevicesError && (
                  <Stack direction="row" alignItems="center" justifyContent="center" spacing={1} sx={{ mt: 2, color: "var(--mist)" }}>
                    <CircularProgress size={14} sx={{ color: "var(--brass)" }} />
                    <Typography sx={{ fontSize: "0.8rem", letterSpacing: "0.04em" }}>{t('devices.searching')}</Typography>
                  </Stack>
                )}
              </>
            )}
          </Box>

          <Box component="section">
            <SectionHeading>{t('sections.calendar')}</SectionHeading>
            <DateCalendarComponent coord={coord} locationLabel={locationLabel} />
          </Box>
        </Stack>

        <Typography sx={{ textAlign: "center", color: "var(--mist)", fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase", pb: 4 }}>
          {t('app.version', { version: packageJson.version })}
        </Typography>
      </Box>

      {currentDeviceIp && currentSetting && (
        <SettingsDialog key={currentSetting.id} isOpen={isSettingOpen} onClose={() => setIsSettingOpen(false)} settings={currentSetting} />
      )}
      <AboutDialog open={isAboutOpen} onClose={() => setIsAboutOpen(false)} />
    </ThemeProvider>
  );
}

export default App;
