import { SectionHeading } from "@/components/SectionHeading";
import { DevicesComponent } from "@/features/devices/components/DevicesGrid";
import { Device } from "@/features/devices/types/device";
import { Box, CircularProgress, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

export function DevicesSection({
    devices,
    socoDevices,
    connectedBt,
    loading,
    error,
    socoLoading,
    socoError,
    selectedIp,
    onSelect,
    onOpenSettings,
    onOpenInfo,
}: Readonly<{
    devices: Device[];
    socoDevices: Device[];
    connectedBt: string[];
    loading: boolean;
    error: boolean;
    socoLoading: boolean;
    socoError: boolean;
    selectedIp?: string | number | null;
    onSelect: (device: Device) => void;
    onOpenSettings: (device: Device) => void;
    onOpenInfo: (device: Device) => void;
}>) {
    const { t } = useTranslation();
    return (
        <Box component="section">
            <SectionHeading>{t("sections.devices")}</SectionHeading>
            {loading ? (
                <Box sx={{ textAlign: "center" }}><CircularProgress sx={{ color: "var(--brass)" }} /></Box>
            ) : error ? (
                <Typography sx={{ textAlign: "center", color: "var(--mist)" }}>{t("devices.errorFetching")}</Typography>
            ) : (
                <>
                    {/* DB devices (incl. 'Cet appareil') render immediately; Sonos/Freebox
                        discovery only refines availability in the background. */}
                    <DevicesComponent
                        devices={devices}
                        soCoDevices={socoDevices}
                        connectedBtMacs={connectedBt}
                        selectedIp={selectedIp}
                        onClick={onSelect}
                        onOpenSettings={onOpenSettings}
                        onOpenInfo={onOpenInfo}
                    />
                    {socoLoading && !socoError && (
                        <Stack direction="row" alignItems="center" justifyContent="center" spacing={1} sx={{ mt: 2, color: "var(--mist)" }}>
                            <CircularProgress size={14} sx={{ color: "var(--brass)" }} />
                            <Typography sx={{ fontSize: "0.8rem", letterSpacing: "0.04em" }}>{t("devices.searching")}</Typography>
                        </Stack>
                    )}
                </>
            )}
        </Box>
    );
}
