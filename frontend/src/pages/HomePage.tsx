import { AboutDialog } from "@/components/about";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { MihrabArch } from "@/components/MihrabArch";
import { CalendarSection } from "@/features/calendar/CalendarSection";
import { DeviceInfoDialog } from "@/features/devices/components/DeviceInfoDialog";
import { SettingsDialog } from "@/features/devices/components/SettingsDialog";
import { DevicesSection } from "@/features/devices/DevicesSection";
import { useDevicesData } from "@/features/devices/hooks/useDevicesData";
import { useDeviceSelection } from "@/features/devices/hooks/useDeviceSelection";
import { Device } from "@/features/devices/types/device";
import { getSettings } from "@/features/prayers/api/apiPrayer";
import { DateClock } from "@/features/prayers/components/Clock";
import { usePrayerLocation } from "@/features/prayers/hooks/usePrayerLocation";
import { PrayersSection } from "@/features/prayers/PrayersSection";
import BluetoothSearchingIcon from "@mui/icons-material/BluetoothSearching";
import InfoIcon from "@mui/icons-material/Info";
import MyLocationIcon from "@mui/icons-material/MyLocation";
import PlaceOutlinedIcon from "@mui/icons-material/PlaceOutlined";
import SyncIcon from "@mui/icons-material/Sync";
import { Box, CircularProgress, IconButton, Stack, Tooltip, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import packageJson from "../../package.json";

export function HomePage() {
    const { t } = useTranslation();

    const { devicesQuery, socoQuery, connectedBtQuery, syncPrayers, scanBluetoothMutation } = useDevicesData();
    const { data: settingsData, isLoading: settingsLoading } = useQuery({ queryKey: ["settings"], queryFn: getSettings });
    const settings = Array.isArray(settingsData) ? settingsData : undefined;

    const { currentDeviceIp, currentSetting, selectDevice } = useDeviceSelection(
        devicesQuery.data, settings, devicesQuery.isLoading, settingsLoading,
    );
    const { coord, locationLabel, geoCoords, geoStatus, requestLocation } = usePrayerLocation(currentSetting);

    const [currentHijirDate, setCurrentHijirDate] = useState<string>("");
    const [isAboutOpen, setIsAboutOpen] = useState<boolean>(false);
    const [isSettingOpen, setIsSettingOpen] = useState<boolean>(false);
    const [infoDevice, setInfoDevice] = useState<Device | null>(null);
    const [isInfoOpen, setIsInfoOpen] = useState<boolean>(false);

    const openDeviceSettings = (device: Device) => {
        if (currentDeviceIp !== device.getIp()) selectDevice(device);
        setIsSettingOpen(true);
    };
    const openDeviceInfo = (device: Device) => {
        setInfoDevice(device);
        setIsInfoOpen(true);
    };

    const devices = devicesQuery.data;

    return (
        <>
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
                        {!devicesQuery.isLoading && !!devices?.length && (
                            <Tooltip title={t("nav.sync")}><IconButton onClick={syncPrayers}><SyncIcon /></IconButton></Tooltip>
                        )}
                        <Tooltip title={t("nav.scanBluetooth")}>
                            <span>
                                <IconButton onClick={() => scanBluetoothMutation.mutate()} disabled={scanBluetoothMutation.isPending}>
                                    <BluetoothSearchingIcon />
                                </IconButton>
                            </span>
                        </Tooltip>
                        <LanguageSwitcher />
                        <Tooltip title={t("nav.about")}><IconButton onClick={() => setIsAboutOpen(true)}><InfoIcon /></IconButton></Tooltip>
                    </Stack>
                </Stack>

                {/* Hero */}
                <Box sx={{ position: "relative", textAlign: "center", px: 2, pt: { xs: 8, md: 11 }, pb: { xs: 4, md: 6 } }}>
                    <MihrabArch />
                    <Box sx={{ position: "relative", zIndex: 1, animation: "rise .8s ease both" }}>
                        <DateClock />
                        {currentHijirDate && (
                            <Typography dir="rtl" sx={{ fontFamily: "var(--font-arabic)", fontSize: { xs: "1.7rem", md: "2.2rem" }, color: "var(--brass-bright)", mt: 2.5 }}>
                                {currentHijirDate}
                            </Typography>
                        )}
                        <Stack direction="row" alignItems="center" justifyContent="center" spacing={0.5} sx={{ mt: 1.5, color: "var(--mist)" }}>
                            <PlaceOutlinedIcon sx={{ fontSize: "1rem" }} />
                            <Typography sx={{ fontSize: "0.85rem", letterSpacing: "0.04em" }}>{locationLabel}</Typography>
                            <Tooltip title={geoStatus === "denied" ? t("location.denied") : t("location.useMyLocation")}>
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

                    <PrayersSection coord={coord} updateDate={setCurrentHijirDate} />

                    <DevicesSection
                        devices={devices ?? []}
                        socoDevices={socoQuery.data ?? []}
                        connectedBt={connectedBtQuery.data ?? []}
                        loading={devicesQuery.isLoading}
                        error={!!devicesQuery.error}
                        socoLoading={socoQuery.isLoading}
                        socoError={!!socoQuery.error}
                        selectedIp={currentDeviceIp}
                        onSelect={selectDevice}
                        onOpenSettings={openDeviceSettings}
                        onOpenInfo={openDeviceInfo}
                    />

                    <CalendarSection coord={coord} locationLabel={locationLabel} />
                </Stack>

                <Typography sx={{ textAlign: "center", color: "var(--mist)", fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase", pb: 4 }}>
                    {t("app.version", { version: packageJson.version })}
                </Typography>
            </Box>

            {currentDeviceIp && currentSetting && (
                <SettingsDialog key={currentSetting.id} isOpen={isSettingOpen} onClose={() => setIsSettingOpen(false)} settings={currentSetting} />
            )}
            <DeviceInfoDialog device={infoDevice} open={isInfoOpen} onClose={() => setIsInfoOpen(false)} />
            <AboutDialog open={isAboutOpen} onClose={() => setIsAboutOpen(false)} />
        </>
    );
}
