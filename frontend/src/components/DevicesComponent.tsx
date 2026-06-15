import DeviceCard from "@/components/DeviceCard";
import { Device } from "@/models/device";
import { Stack, } from "@mui/material";
import { Grid } from '@mui/system';
export function DevicesComponent({ devices, onClick, onOpenSettings, soCoDevices, selectedIp }: Readonly<{
    devices: Device[],
    onClick?: (device: Device) => void,
    onOpenSettings?: (device: Device) => void,
    soCoDevices?: Device[],
    selectedIp?: string | number | null,
}>) {
    return (
        <Stack spacing={2} sx={{ mt: 2 }} >
            <Grid container spacing={3} sx={{ flexGrow: 1, justifyContent: 'center' }}>
                {devices?.map((device) => {
                    // Local & Freebox players are always reachable; Sonos availability
                    // depends on live network discovery.
                    const available = device.type === "sonos_player"
                        ? !!soCoDevices?.some(d => d.getIp() === device.getIp())
                        : true;
                    return <DeviceCard
                        key={device.getId()}
                        device={device}
                        available={available}
                        selected={selectedIp != null && device.getIp() === selectedIp}
                        onClick={() => onClick?.(device)}
                        onOpenSettings={() => onOpenSettings?.(device)}
                    />;
                })}
            </Grid>
        </Stack>
    )
}
