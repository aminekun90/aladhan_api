import DeviceCard from "@/components/DeviceCard";
import { Device } from "@/models/device";
import { Stack, } from "@mui/material";
import { Grid } from '@mui/system';
export function DevicesComponent({ devices, onClick, soCoDevices }: Readonly<{ devices: Device[], onClick?: (device: Device) => void, soCoDevices?: Device[] }>) {


    return (
        <Stack spacing={2} sx={{ mt: 2 }} >
            <Grid container spacing={3} sx={{ flexGrow: 1, justifyContent: 'center' }}>
                {!!devices && devices?.map((device) => {
                    // Check if device is available in soCoDevices
                    const available = !!soCoDevices?.some(d => d.getIp() === device.getIp());
                    return <DeviceCard key={device.getId()} device={device} available={available} onClick={() => {
                        onClick?.(device);
                    }} />


                })}
            </Grid>
        </Stack>
    )
}