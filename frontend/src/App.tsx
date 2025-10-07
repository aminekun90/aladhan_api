import { getSettings } from "@/api/apiPrayer";
import bgIslamic from "@/assets/bg-islamic.jpg";
import bg from "@/assets/bg.jpg";
import { DateCalendarComponent } from '@/components/Calendar';
import { DateClock } from "@/components/Clock";
import { DevicesComponent } from "@/components/DevicesComponent";
import { PrayersComponent } from "@/components/PrayersComponent";
import { SettingsDialog } from '@/components/SettingsDialog';
import { DateInfo } from '@/models/prayer';
import SettingsIcon from '@mui/icons-material/Settings';
import { alpha, Box, createTheme, CssBaseline, IconButton, Stack, ThemeProvider, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import Grid from '@mui/material/Grid2';
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import packageJson from '../package.json';
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});
function App() {

  const [currentHijirDate, setCurrentHijirDate] = useState<string>("");
  const [isSettingOpen, setIsSettingOpen] = useState<boolean>(false);
  const settings = useQuery({
    queryKey: ["settings"],
    queryFn: getSettings,
  });

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
          // height: '100vh',
          width: '100vw',
          padding: 5,

        }}
      >
        <Box sx={{
          backgroundColor: alpha(grey[900], 0.5),
          borderRadius: 8,
          paddingTop: 0,
          background: `url(${bgIslamic}) no-repeat top fixed`,

        }}>
          <Grid container justifyContent="flex-end" sx={{ display: 'flex', alignItems: 'center', justifyItems: 'center', height: 60 }}>
            <IconButton onClick={() => { setIsSettingOpen(true) }} sx={{ color: 'white', height: 60, width: 60 }}>
              <SettingsIcon />
            </IconButton>
          </Grid>
          <Grid sx={{ padding: 10, textAlign: 'center' }}>
            <DateClock variation="h2" />
            <Typography dir="rtl" variant="h4" sx={{ textAlign: 'center', margin: '1em 0', }}>{currentHijirDate}</Typography>
            {settings.isLoading && <Typography>Loading...</Typography>}
            {!!settings.data && <Typography sx={{ textAlign: 'center', margin: '1em 0' }}>{(settings.data).api.city + " | " + (settings.data).api.country}</Typography>}
            <PrayersComponent updateDate={(date: DateInfo) => { setCurrentHijirDate(date.hijri.weekday.ar + " " + date.hijri.day + " " + date.hijri.month.ar + " " + date.hijri.year) }} />
            <DevicesComponent />
            <DateCalendarComponent />
          </Grid>
        </Box>
        <Typography sx={{ color: 'white', fontSize: 12 }}>Version beta {packageJson.version}</Typography>
        {!!settings.data && <SettingsDialog isOpen={isSettingOpen} onClose={() => { setIsSettingOpen(false) }} settings={settings.data} />
        }</Stack>
    </ThemeProvider>
  )
}

export default App
