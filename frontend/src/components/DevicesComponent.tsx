import { getSoCoDevices } from "@/api/apiDevice";
import DeviceCard from "@/components/DeviceCard";
import { Stack, Typography } from "@mui/material";
import Grid from '@mui/material/Grid2';
import { useQuery } from "@tanstack/react-query";
export function DevicesComponent() {
    const { data, isLoading, isError } = useQuery({
        queryKey: ["devices"],
        queryFn: getSoCoDevices,
    });
    return (
        <Stack spacing={2} sx={{ mt: 2 }}>
            <Grid container spacing={3} sx={{ flexGrow: 1, justifyContent: 'center' }}>
                {isLoading && <Typography>Loading...</Typography>}
                {isError && <Typography>Error...</Typography>}
                {!!data && data?.map((device) => (
                    <Grid size={{ xs: 6, md: 6 }} key={device.getIp()}>
                        <DeviceCard device={device} />
                    </Grid>
                ))}
            </Grid>
        </Stack>
    )
}