import { getSettings } from "@/api/apiPrayer";
import { DateCalendarComponent } from '@/components/Calendar';
import { DateClock } from "@/components/Clock";
import { DevicesComponent } from "@/components/DevicesComponent";
import { PrayersComponent } from "@/components/PrayersComponent";
import { SettingsDialog } from '@/components/SettingsDialog';
import { DEFAULT_COORD } from "@/const";
import { theme } from "@/theme";
import { ToastContainer, useToast } from '@aminekun90/react-toast';
import BluetoothSearchingIcon from '@mui/icons-material/BluetoothSearching';
import InfoIcon from '@mui/icons-material/Info';
import PlaceOutlinedIcon from '@mui/icons-material/PlaceOutlined';
import SettingsIcon from '@mui/icons-material/Settings';
import SyncIcon from '@mui/icons-material/Sync';
import { Box, CircularProgress, CssBaseline, IconButton, Stack, ThemeProvider, Tooltip, Typography } from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ReactNode, useEffect, useState } from "react";
import packageJson from '../package.json';
import { createDeviceSettings, getDevices, getSoCoDevices, scanBluetooth, scheduleAllDevices } from "./api/apiDevice";
import { AboutDialog } from "./components/about";
import { Settings } from "./models/Settings";
import { Device } from "./models/device";

/** Decorative pointed (ogival) arch — the mihrab motif framing the hero. */
function MihrabArch() {
  return (
    <Box
      component="svg"
      viewBox="0 0 200 280"
      aria-hidden
      sx={{
        position: "absolute",
        top: { xs: -28, md: -48 },
        left: "50%",
        transform: "translateX(-50%)",
        width: { xs: 300, sm: 380, md: 460 },
        height: "auto",
        zIndex: 0,
        pointerEvents: "none",
        opacity: 0.45,
      }}
    >
      <defs>
        <linearGradient id="archStroke" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ecca7e" stopOpacity="0.9" />
          <stop offset="55%" stopColor="#d4ad5f" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#d4ad5f" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path
        d="M28 280 L28 130 A 86 116 0 0 1 100 14 A 86 116 0 0 1 172 130 L172 280"
        fill="none"
        stroke="url(#archStroke)"
        strokeWidth="1.5"
      />
      <circle cx="100" cy="30" r="2.5" fill="#ecca7e" opacity="0.8" />
    </Box>
  );
}

function SectionHeading({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <Stack direction="row" alignItems="center" spacing={2} sx={{ width: "100%", maxWidth: 900, mx: "auto", mb: 3 }}>
      <Box sx={{ flex: 1, height: "1px", background: "linear-gradient(90deg, transparent, var(--line))" }} />
      <Typography variant="overline" sx={{ color: "var(--brass)", fontSize: "0.72rem", whiteSpace: "nowrap" }}>
        {children}
      </Typography>
      <Box sx={{ flex: 1, height: "1px", background: "linear-gradient(90deg, var(--line), transparent)" }} />
    </Stack>
  );
}

function App() {
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
  const [deviceClicked, setDeviceClicked] = useState<boolean>(true);

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

  const scheduleAllDevicesMutation = useMutation({
    mutationFn: () => scheduleAllDevices(),
    onSuccess: () => notifySuccess('Devices Scheduled', 'All devices have been scheduled !'),
  });
  const syncPrayers = () => {
    notifySuccess('Syncing Prayers', 'Prayers have been synced !');
    scheduleAllDevicesMutation.mutate();
  };

  const scanBluetoothMutation = useMutation({
    mutationFn: () => scanBluetooth(),
    onSuccess: (found) => {
      notifySuccess('Bluetooth Scan', `Found ${found.length} device(s)`);
      queryClient.invalidateQueries({ queryKey: ["devices"] });
    },
  });

  const createSettingMutation = useMutation({
    mutationFn: (device: Device) => createDeviceSettings(device.getId()),
    onSuccess: (data: Settings | null) => {
      notifySuccess('Settings Saved', 'Settings have been saved !');
      setCurrentSetting(data);
    },
  });

  useEffect(() => {
    const syncSelectedSetting = () => {
      if (settings && settings.length > 0 && !settingsLoading) {
        setCurrentSetting(settings.find(s => s.device?.getIp() === currentDeviceIp) || null);
      }
    };
    syncSelectedSetting();
  }, [settings, settingsLoading, deviceLoading, currentDeviceIp, settingsError, deviceClicked]);

  const coord = {
    lat: currentSetting?.city?.lat ?? DEFAULT_COORD.lat,
    lon: currentSetting?.city?.lon ?? DEFAULT_COORD.lon,
  };

  const handleDeviceClick = (device: Device) => {
    setDeviceClicked(!deviceClicked);
    if (deviceClicked) {
      setCurrentDeviceIp(device.getIp());
      const found = settings?.find(s => s.device?.getIp() === device.getIp());
      if (found) setCurrentSetting(found);
      else createSettingMutation.mutate(device);
    } else {
      setCurrentDeviceIp(null);
      setCurrentSetting(null);
    }
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
              <Tooltip title="Sync prayers"><IconButton onClick={syncPrayers}><SyncIcon /></IconButton></Tooltip>
            )}
            <Tooltip title="Scan Bluetooth speakers">
              <span>
                <IconButton onClick={() => scanBluetoothMutation.mutate()} disabled={scanBluetoothMutation.isPending}>
                  <BluetoothSearchingIcon />
                </IconButton>
              </span>
            </Tooltip>
            {!!currentSetting && (
              <Tooltip title="Settings"><IconButton onClick={() => setIsSettingOpen(true)}><SettingsIcon /></IconButton></Tooltip>
            )}
            <Tooltip title="About"><IconButton onClick={() => setIsAboutOpen(true)}><InfoIcon /></IconButton></Tooltip>
          </Stack>
        </Stack>

        {/* Hero */}
        <Box sx={{ position: "relative", textAlign: "center", px: 2, pt: { xs: 6, md: 9 }, pb: { xs: 4, md: 6 } }}>
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
            {!!currentSetting && (
              <Stack direction="row" alignItems="center" justifyContent="center" spacing={0.75} sx={{ mt: 1.5, color: "var(--mist)" }}>
                <PlaceOutlinedIcon sx={{ fontSize: "1rem" }} />
                <Typography sx={{ fontSize: "0.85rem", letterSpacing: "0.04em" }}>
                  {(currentSetting.city?.name ?? "Not set")} · {(currentSetting.city?.country ?? "Not set")}
                </Typography>
              </Stack>
            )}
          </Box>
        </Box>

        {/* Content */}
        <Stack spacing={{ xs: 6, md: 9 }} sx={{ px: { xs: 2, md: 5 }, pb: 8, width: "100%", maxWidth: 1200, mx: "auto" }}>
          {settingsLoading && <Box sx={{ textAlign: "center" }}><CircularProgress sx={{ color: "var(--brass)" }} /></Box>}

          {!!currentSetting && (
            <Box component="section">
              <SectionHeading>Heures de prière</SectionHeading>
              <PrayersComponent coord={coord} updateDate={setCurrentHijirDate} />
            </Box>
          )}

          <Box component="section">
            <SectionHeading>Appareils</SectionHeading>
            {deviceError && <Typography sx={{ textAlign: "center", color: "var(--mist)" }}>Error fetching devices</Typography>}
            {deviceLoading && <Box sx={{ textAlign: "center" }}><CircularProgress sx={{ color: "var(--brass)" }} /></Box>}
            {devices && !deviceLoading && socoDevices && !socoDevicesError && !socoLoading && (
              <DevicesComponent devices={devices} soCoDevices={socoDevices} onClick={handleDeviceClick} />
            )}
          </Box>

          {!!currentSetting && (
            <Box component="section">
              <SectionHeading>Calendrier</SectionHeading>
              <DateCalendarComponent coord={coord} />
            </Box>
          )}
        </Stack>

        <Typography sx={{ textAlign: "center", color: "var(--mist)", fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase", pb: 4 }}>
          Version beta {packageJson.version}
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
