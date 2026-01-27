import freebox from "@/assets/freebox-devialet.png";
import symfonisk from "@/assets/symfonisk.jpg";
import { Device } from "@/models/device";
import LockOpenIcon from '@mui/icons-material/LockOpen';
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import {
    Box,
    Card,
    CardActionArea,
    CardContent,
    CardMedia,
    IconButton,
    Typography,
    useTheme,
} from "@mui/material";
import { useState } from "react";

export default function DeviceCard({
    device,
    available = true,
    onClick,
    key,
}: Readonly<{
    device: Device;
    available?: boolean;
    onClick?: () => void;
    key?: string | number;
}>) {
    const theme = useTheme();
    const [clicked, setClicked] = useState(false);

    const handleClick = () => {
        setClicked(!clicked);
        onClick?.();
    };
    const isSonosPlayer = device.type === "sonos_player";
    const isFreeboxPlayer = device.type === "freebox_player";

    let deviceImage = symfonisk; // use generic image by default
    if (isFreeboxPlayer || device.getRawAttributes().device_model === "fbx7hd-delta") {
        deviceImage = freebox;
    } else if (isSonosPlayer) {
        deviceImage = symfonisk;
    }
    return (
        <Card
            key={key}
            onClick={handleClick}
            tabIndex={0}
            sx={{
                position: "relative",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                alignItems: "center",
                maxWidth: 220,
                width: "max-content",
                cursor: "pointer",
                opacity: available ? 1 : 0.6,
                transform: clicked ? "scale(1.02)" : "scale(1)",
                transition: "all 0.25s ease",
                background: "rgba(255, 255, 255, 0.15)",
                backdropFilter: "blur(2px) saturate(180%)",
                border: "0.0625rem solid rgba(255, 255, 255, 0.4)",
                borderRadius: "2rem",
                padding: "1.25rem",
                boxShadow:
                    "0 8px 32px rgba(31, 38, 135, 0.2), inset 0 4px 20px rgba(255, 255, 255, 0.3)",
                "&:hover": {
                    boxShadow:
                        "0 10px 40px rgba(31, 38, 135, 0.25), inset 0 6px 24px rgba(255, 255, 255, 0.4)",
                },
                "&::after": {
                    content: '""',
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: "100%",
                    background: "rgba(255, 255, 255, 0.1)",
                    borderRadius: "2rem",
                    backdropFilter: "blur(1px)",
                    boxShadow:
                        "inset -10px -8px 0px -11px rgba(255, 255, 255, 1), inset 0px -9px 0px -8px rgba(255, 255, 255, 1)",
                    opacity: 0.6,
                    zIndex: -1,
                    filter: "blur(1px) drop-shadow(10px 4px 6px black) brightness(115%)",
                    pointerEvents: "none",
                },
                ...(clicked && {
                    border: `0.125rem solid ${theme.palette.primary.main}`,
                    boxShadow:
                        "0 0 25px rgba(100, 180, 255, 0.6), inset 0 6px 24px rgba(255,255,255,0.4)",
                }),
            }}
        >
            <CardActionArea>
                {device.type === "freebox_player" && <Box sx={{ mb: 2 }} >
                    <IconButton><LockOpenIcon /></IconButton>
                </Box>}

                <CardMedia
                    component="img"
                    sx={{
                        width: "100%",
                        objectFit: "cover",
                        borderRadius: "1.5rem",
                        filter: available ? "none" : "grayscale(100%)",
                        backgroundColor: "#fff",
                    }}
                    image={deviceImage}
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
                        <Typography
                            component="div"
                            variant="h6"
                            color={available ? "text.primary" : "text.disabled"}
                        >
                            {device.getName()}
                        </Typography>
                        <Typography
                            variant="subtitle2"
                            component="div"
                            color={available ? "text.secondary" : "text.disabled"}
                        >
                            {device.getPlayingTitle().title}
                        </Typography>
                    </CardContent>

                    <Box sx={{ display: "flex", alignItems: "center", pb: 1 }}>
                        <IconButton aria-label="previous">
                            {theme.direction === "rtl" ? (
                                <SkipNextIcon />
                            ) : (
                                <SkipPreviousIcon />
                            )}
                        </IconButton>
                        <IconButton aria-label="play/pause">
                            <PlayArrowIcon sx={{ height: 38, width: 38 }} />
                        </IconButton>
                        <IconButton aria-label="next">
                            {theme.direction === "rtl" ? (
                                <SkipPreviousIcon />
                            ) : (
                                <SkipNextIcon />
                            )}
                        </IconButton>
                    </Box>

                </Box>
            </CardActionArea>
        </Card >
    );
}
