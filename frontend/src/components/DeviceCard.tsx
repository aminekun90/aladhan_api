import { controlDevice, PlayerAction } from "@/api/apiDevice";
import freebox from "@/assets/freebox-devialet.png";
import symfonisk from "@/assets/symfonisk.jpg";
import { Device } from "@/models/device";
import { logger } from "@/utils/logger";
import BluetoothIcon from "@mui/icons-material/Bluetooth";
import LockOpenIcon from '@mui/icons-material/LockOpen';
import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import {
    alpha,
    Box,
    Card,
    CardActionArea,
    CardContent,
    CardMedia,
    Chip,
    IconButton,
    Typography,
    useTheme,
} from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { MouseEvent, useState } from "react";

const BRASS = "#d4ad5f";

const TYPE_LABELS: Record<string, string> = {
    sonos_player: "Sonos",
    freebox_player: "Freebox",
    bluetooth_speaker: "Bluetooth",
};

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
    const [isPlaying, setIsPlaying] = useState(false);

    const handleClick = () => {
        setClicked(!clicked);
        onClick?.();
    };

    const controlMutation = useMutation({
        mutationFn: (action: PlayerAction) => {
            const id = device.getId();
            if (!id) return Promise.reject(new Error("Device has no id"));
            return controlDevice(id, action);
        },
        onError: (error) => logger.error("Device control failed:", error),
    });

    const sendControl = (action: PlayerAction) => (event: MouseEvent) => {
        event.stopPropagation(); // don't toggle card selection
        if (action === "play") setIsPlaying(true);
        if (action === "pause") setIsPlaying(false);
        controlMutation.mutate(action);
    };

    const isSonosPlayer = device.type === "sonos_player";
    const isFreeboxPlayer = device.type === "freebox_player";
    const isBluetooth = device.type === "bluetooth_speaker";
    const controllable = !!device.getId() && !isBluetooth; // BT speakers are fire-and-forget

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
                width: 200,
                cursor: "pointer",
                opacity: available ? 1 : 0.55,
                transition: "transform .25s ease, border-color .25s ease, box-shadow .25s ease",
                transform: clicked ? "translateY(-4px)" : "none",
                background: "var(--surface)",
                backdropFilter: "blur(10px)",
                border: `1px solid ${clicked ? alpha(BRASS, 0.6) : "var(--line)"}`,
                borderRadius: "1.5rem",
                padding: "1.1rem",
                boxShadow: clicked ? `0 14px 44px ${alpha(BRASS, 0.22)}` : "none",
                "&:hover": {
                    transform: "translateY(-4px)",
                    borderColor: alpha(BRASS, 0.45),
                    boxShadow: `0 14px 44px ${alpha(BRASS, 0.16)}`,
                },
            }}
        >
            <CardActionArea>
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1, mb: 2 }}>
                    {device.type && (
                        <Chip
                            size="small"
                            icon={isBluetooth ? <BluetoothIcon /> : undefined}
                            label={TYPE_LABELS[device.type] ?? device.type}
                            color={available ? "primary" : "default"}
                            variant="outlined"
                        />
                    )}
                    {isFreeboxPlayer && <IconButton size="small"><LockOpenIcon fontSize="small" /></IconButton>}
                </Box>

                <Box sx={{
                    width: "100%",
                    aspectRatio: "1 / 1",
                    borderRadius: "1.25rem",
                    overflow: "hidden",
                    border: "1px solid var(--line)",
                    background: "radial-gradient(120% 120% at 50% 0%, rgba(212,173,95,0.12), rgba(13,20,38,0.6))",
                }}>
                    <CardMedia
                        component="img"
                        sx={{
                            width: "100%",
                            height: "100%",
                            objectFit: "cover",
                            mixBlendMode: "luminosity",
                            opacity: available ? 0.92 : 0.5,
                            filter: available ? "none" : "grayscale(100%)",
                        }}
                        image={deviceImage}
                        alt={device.getName()}
                    />
                </Box>

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
                        <IconButton aria-label="previous" disabled={!controllable} onClick={sendControl("previous")}>
                            {theme.direction === "rtl" ? <SkipNextIcon /> : <SkipPreviousIcon />}
                        </IconButton>
                        <IconButton aria-label="play/pause" disabled={!controllable}
                            onClick={sendControl(isPlaying ? "pause" : "play")}>
                            {isPlaying
                                ? <PauseIcon sx={{ height: 38, width: 38 }} />
                                : <PlayArrowIcon sx={{ height: 38, width: 38 }} />}
                        </IconButton>
                        <IconButton aria-label="next" disabled={!controllable} onClick={sendControl("next")}>
                            {theme.direction === "rtl" ? <SkipPreviousIcon /> : <SkipNextIcon />}
                        </IconButton>
                    </Box>

                </Box>
            </CardActionArea>
        </Card >
    );
}
