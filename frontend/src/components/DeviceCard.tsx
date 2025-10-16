import symfonisk from "@/assets/symfonisk.jpg";
import { Device } from "@/models/device";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import {
    Box,
    Card,
    CardContent,
    CardMedia,
    IconButton,
    Typography,
    useTheme,
} from "@mui/material";

export default function DeviceCard({ device, available }: Readonly<{ device: Device, available?: boolean }>) {
    const theme = useTheme();

    return (
        <Card
            key={device.getIp()}
            sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "column" }, // image moves to top on small screens
                justifyContent: "space-between",
                alignItems: "center",
                maxWidth: 200,
                mx: "auto",
                cursor: 'pointer',
                opacity: available ? 1 : 0.5,
                bgcolor: available ? theme.palette.background.paper : theme.palette.grey[800],
                boxShadow: available ? 3 : 0,
                "&:hover": {
                    boxShadow: available ? 6 : 0,
                },
            }}
        >
            <CardMedia
                component="img"
                sx={{
                    width: "100%",
                    objectFit: "cover",
                }}
                image={symfonisk}
                alt="Device image"
            />

            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    width: "100%",
                    alignItems: "center",
                    textAlign: "center",
                }}
            >
                <CardContent sx={{ flex: "1 0 auto" }}>
                    <Typography component="div" variant="h5">
                        {device.getName()}
                    </Typography>
                    <Typography
                        variant="subtitle1"
                        component="div"
                        sx={{ color: "text.secondary" }}
                    >
                        {device.getPlayingTitle().title}
                    </Typography>
                </CardContent>

                <Box sx={{ display: "flex", alignItems: "center", pb: 1 }}>
                    <IconButton aria-label="previous">
                        {theme.direction === "rtl" ? <SkipNextIcon /> : <SkipPreviousIcon />}
                    </IconButton>
                    <IconButton aria-label="play/pause">
                        <PlayArrowIcon sx={{ height: 38, width: 38 }} />
                    </IconButton>
                    <IconButton aria-label="next">
                        {theme.direction === "rtl" ? <SkipPreviousIcon /> : <SkipNextIcon />}
                    </IconButton>
                </Box>
            </Box>
        </Card>
    );
}
