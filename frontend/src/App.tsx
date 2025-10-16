import { getSettings } from "@/api/apiPrayer";
import bgIslamic from "@/assets/bg-islamic.jpg";
import bg from "@/assets/bg.jpg";
import { DateCalendarComponent } from '@/components/Calendar';
import { DateClock } from "@/components/Clock";
import { DevicesComponent } from "@/components/DevicesComponent";
import { PrayersComponent } from "@/components/PrayersComponent";
import { SettingsDialog } from '@/components/SettingsDialog';
import SettingsIcon from '@mui/icons-material/Settings';
import { alpha, Box, CircularProgress, createTheme, CssBaseline, IconButton, Stack, ThemeProvider, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import { Grid } from '@mui/system';
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import packageJson from '../package.json';
import { createDeviceSettings, getDevices, getSoCoDevices } from "./api/apiDevice";
import { Settings } from "./models/Settings";
import { Device } from "./models/device";

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});
function App() {

  const [currentHijirDate, setCurrentHijirDate] = useState<string>("");
  const [isSettingOpen, setIsSettingOpen] = useState<boolean>(false);
  const [currentDeviceIp, setCurrentDeviceIp] = useState<string | null | undefined>();
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

  // mutation create device settings with device ID

  const createSettingMutation = useMutation({
    mutationFn: (device: Device) => createDeviceSettings(device.getId()),
    onSuccess: (data: Settings | null) => {
      console.log("✅ Settings saved successfully:", data);
      setCurrentSetting(data);
    }
  })
  useEffect(() => {
    if (settings && settings.length > 0 && !settingsLoading) {
      setCurrentSetting(settings.find(s => s.device?.getIp() === currentDeviceIp) || null);
    }
  }, [settings, settingsLoading, deviceLoading, currentDeviceIp, settingsError],);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Stack
        direction="column"

        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: `url(${bg}) no-repeat center fixed`,
          overflowX: 'hidden',
          minHeight: '100vh',
          height: 'max-content',
          maxWidth: '100vw',
          width: '100%',
          padding: 5,

        }}
      >
        <Box sx={{
          backgroundColor: alpha(grey[900], 0.5),
          borderRadius: 8,
          paddingTop: 0,
          background: `url(${bgIslamic}) no-repeat top fixed`,

        }}>
          {!!currentSetting && <Grid container justifyContent="flex-end" sx={{ display: 'flex', alignItems: 'center', justifyItems: 'center', height: 60 }}>
            <IconButton onClick={() => { setIsSettingOpen(true) }} sx={{ color: 'white', height: 60, width: 60 }}>
              <SettingsIcon />
            </IconButton>
          </Grid>}

          <Grid sx={{ padding: 10, textAlign: 'center' }}>
            <DateClock variation="h2" />
            <Typography dir="rtl" variant="h4" sx={{ textAlign: 'center', margin: '1em 0', }}>{currentHijirDate}</Typography>
            {settingsLoading && <CircularProgress />}
            {!!currentSetting && <>
              <Typography sx={{ textAlign: 'center', margin: '1em 0' }}>{currentSetting.city?.name + " | " + currentSetting.city?.country}</Typography>
              <PrayersComponent coord={{ lat: currentSetting?.city?.lat ?? 47.23999925644779, lon: currentSetting?.city?.lon ?? -1.5304936560937061 }} updateDate={(date: string) => { setCurrentHijirDate(date) }} />

            </>}
            {deviceError && <Typography>Error fetching devices</Typography>
            }
            {deviceLoading && <CircularProgress />}
            {devices && !deviceLoading && socoDevices && !socoDevicesError &&
              !socoLoading && <DevicesComponent devices={devices} soCoDevices={socoDevices} onClick={(device: Device) => {
                console.log("Selected device", device);
                setCurrentDeviceIp(device.getIp());

                // Find the setting for the selected device
                const foundDeviceSettings = settings?.find(s => s.device?.getIp() === device.getIp());

                if (foundDeviceSettings) {
                  setCurrentSetting(foundDeviceSettings);
                } else {
                  createSettingMutation.mutate(device);
                }

                console.log("Current setting", foundDeviceSettings, device);
              }} />}

            {!!currentSetting && <DateCalendarComponent coord={{ lat: currentSetting?.city?.lat ?? 47.23999925644779, lon: currentSetting?.city?.lon ?? -1.5304936560937061 }} />}

          </Grid>
        </Box>
        <Typography sx={{ color: 'white', fontSize: 12 }}>Version beta {packageJson.version}</Typography>
        {currentDeviceIp && currentSetting && <SettingsDialog isOpen={isSettingOpen} onClose={() => { setIsSettingOpen(false) }} settings={currentSetting} />
        }</Stack>
    </ThemeProvider>
  )
}

export default App
