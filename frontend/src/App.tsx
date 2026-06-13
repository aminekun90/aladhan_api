import { getSettings } from "@/api/apiPrayer";
import bgIslamic from "@/assets/bg-islamic.jpg";
import bg from "@/assets/bg.jpg";
import { DateCalendarComponent } from '@/components/Calendar';
import { DateClock } from "@/components/Clock";
import { DevicesComponent } from "@/components/DevicesComponent";
import { PrayersComponent } from "@/components/PrayersComponent";
import { SettingsDialog } from '@/components/SettingsDialog';
import { ToastContainer, useToast } from '@aminekun90/react-toast';
import BluetoothSearchingIcon from '@mui/icons-material/BluetoothSearching';
import InfoIcon from '@mui/icons-material/Info';
import SettingsIcon from '@mui/icons-material/Settings';
import SyncIcon from '@mui/icons-material/Sync';
import { alpha, Box, CircularProgress, createTheme, CssBaseline, IconButton, Stack, ThemeProvider, Tooltip, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import { Grid } from '@mui/system';
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import packageJson from '../package.json';
import { DEFAULT_COORD } from "@/const";
import { createDeviceSettings, getDevices, getSoCoDevices, scanBluetooth, scheduleAllDevices } from "./api/apiDevice";
import { AboutDialog } from "./components/about";
import { Settings } from "./models/Settings";
import { Device } from "./models/device";
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});
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
    onSuccess: () => {
      notifySuccess('Devices Scheduled', 'All devices have been scheduled !');
    }
  })
  const syncPrayers = () => {
    notifySuccess('Syncing Prayers', 'Prayers have been synced !');
    scheduleAllDevicesMutation.mutate();
  }

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
    }
  })
  useEffect(() => {
    const updateSetting = () => {
      if (settings && settings.length > 0 && !settingsLoading) {
        setCurrentSetting(settings.find(s => s.device?.getIp() === currentDeviceIp) || null);
      }
    };

    updateSetting();
  }, [settings, settingsLoading, deviceLoading, currentDeviceIp, settingsError, deviceClicked]);

  return (
    <ThemeProvider theme={darkTheme}>
       <ToastContainer />
      <CssBaseline />
      <Stack
        direction="column"

        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: alpha(grey[900], 0.5),
          backgroundImage: `url(${bg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',
          overflowX: 'hidden',
          minHeight: '100vh',
          maxWidth: '100vw',
          width: '100%',
          padding: 5,
          borderRadius: '1rem',

        }}
      >
        <Box sx={{
          borderRadius: 8,
          paddingTop: 0,
          backgroundColor: alpha(grey[900], 0.5),
          backgroundImage: `url(${bgIslamic})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',

        }}>
          <Grid container justifyContent="flex-end" sx={{ display: 'flex', alignItems: 'center', justifyItems: 'center', height: 60 }}>

            {!deviceLoading && devices?.length && <Tooltip title="Sync prayers">
              <IconButton onClick={() => { syncPrayers() }} sx={{ color: 'white', height: 60, width: 60 }}>
                <SyncIcon />
              </IconButton>
            </Tooltip>}
            <Tooltip title="Scan Bluetooth speakers">
              <IconButton onClick={() => { scanBluetoothMutation.mutate() }} disabled={scanBluetoothMutation.isPending} sx={{ color: 'white', height: 60, width: 60 }}>
                <BluetoothSearchingIcon />
              </IconButton>
            </Tooltip>
            {!!currentSetting &&
              <Tooltip title="Settings">
                <IconButton onClick={() => { setIsSettingOpen(true) }} sx={{ color: 'white', height: 60, width: 60 }}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
            }
            <Tooltip title="About">
              <IconButton onClick={() => { setIsAboutOpen(true) }} sx={{ color: 'white', height: 60, width: 60 }}>
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </Grid>

          <Grid sx={{ padding: 10, textAlign: 'center' }}>
            <DateClock variation="h2" />
            <Typography dir="rtl" variant="h4" sx={{ textAlign: 'center', margin: '1em 0', }}>{currentHijirDate}</Typography>
            {settingsLoading && <CircularProgress />}
            {!!currentSetting && <>
              <Typography sx={{ textAlign: 'center', margin: '1em 0' }}>{(currentSetting.city?.name ?? "Not set") + " | " + (currentSetting.city?.country ?? "Not set")}</Typography>
              <PrayersComponent coord={{ lat: currentSetting?.city?.lat ?? DEFAULT_COORD.lat, lon: currentSetting?.city?.lon ?? DEFAULT_COORD.lon }} updateDate={(date: string) => { setCurrentHijirDate(date) }} />

            </>}
            {deviceError && <Typography>Error fetching devices</Typography>
            }
            {deviceLoading && <CircularProgress />}
            {devices && !deviceLoading && socoDevices && !socoDevicesError &&
              !socoLoading && <DevicesComponent devices={devices} soCoDevices={socoDevices} onClick={(device: Device) => {
                setDeviceClicked(!deviceClicked);
                if (deviceClicked) {
                  setCurrentDeviceIp(device.getIp());

                  // Find the setting for the selected device
                  const foundDeviceSettings = settings?.find(s => s.device?.getIp() === device.getIp());

                  if (foundDeviceSettings) {
                    setCurrentSetting(foundDeviceSettings);
                  } else {
                    createSettingMutation.mutate(device);
                  }

                } else {
                  setCurrentDeviceIp(null);
                  setCurrentSetting(null);
                }

              }} />}

            {!!currentSetting && <DateCalendarComponent coord={{ lat: currentSetting?.city?.lat ?? DEFAULT_COORD.lat, lon: currentSetting?.city?.lon ?? DEFAULT_COORD.lon }} />}

          </Grid>
        </Box>
        <Typography sx={{ color: 'white', fontSize: 12 }}>Version beta {packageJson.version}</Typography>
        {currentDeviceIp && currentSetting && <SettingsDialog key={currentSetting.id} isOpen={isSettingOpen} onClose={() => { setIsSettingOpen(false) }} settings={currentSetting} />
        }</Stack>
      <AboutDialog open={isAboutOpen} onClose={() => { setIsAboutOpen(false) }} />
    </ThemeProvider>
  )
}

export default App
