import { controlDevice, PlayerAction } from "@/api/apiDevice";
import freebox from "@/assets/freebox-devialet.png";
import symfonisk from "@/assets/symfonisk.jpg";
import { Device } from "@/models/device";
import { logger } from "@/utils/logger";
import BluetoothIcon from "@mui/icons-material/Bluetooth";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import GraphicEqIcon from "@mui/icons-material/GraphicEq";
import LaptopMacIcon from "@mui/icons-material/LaptopMac";
import LockOpenIcon from '@mui/icons-material/LockOpen';
import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import SettingsIcon from "@mui/icons-material/Settings";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import {
    alpha,
    Box,
    Card,
    CardContent,
    CardMedia,
    Chip,
    IconButton,
    Tooltip,
    Typography,
    useTheme,
} from "@mui/material";
import { useMutation } from "@tanstack/react-query";
import { MouseEvent, useState } from "react";
import { useTranslation } from "react-i18next";

const BRASS = "#d4ad5f";

export default function DeviceCard({
    device,
    available = true,
    selected = false,
    onClick,
    onOpenSettings,
}: Readonly<{
    device: Device;
    available?: boolean;
    selected?: boolean;
    onClick?: () => void;
    onOpenSettings?: () => void;
}>) {
    const theme = useTheme();
    const { t } = useTranslation();
    const [isPlaying, setIsPlaying] = useState(false);

    const controlMutation = useMutation({
        mutationFn: (action: PlayerAction) => {
            const id = device.getId();
            if (!id) return Promise.reject(new Error("Device has no id"));
            return controlDevice(id, action);
        },
        onError: (error) => logger.error("Device control failed:", error),
    });

    const sendControl = (action: PlayerAction) => (event: MouseEvent) => {
        event.stopPropagation(); // don't trigger card selection
        if (action === "play") setIsPlaying(true);
        if (action === "pause") setIsPlaying(false);
        controlMutation.mutate(action);
    };

    const isFreeboxPlayer = device.type === "freebox_player";
    const isBluetooth = device.type === "bluetooth_speaker";
    const isLocal = device.type === "local_player";
    const iconOnly = isBluetooth || isLocal; // no product photo for these
    // Transport controls only make sense for a reachable network player.
    const controllable = available && !!device.getId() && !isBluetooth && !isLocal;

    let deviceImage = symfonisk;
    if (isFreeboxPlayer || device.getRawAttributes().device_model === "fbx7hd-delta") {
        deviceImage = freebox;
    }

    return (
        <Card
            onClick={onClick}
            role="button"
            aria-pressed={selected}
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onClick?.(); }}
            sx={{
                position: "relative",
                display: "flex",
                flexDirection: "column",
                width: { xs: 150, sm: 180, md: 200 },
                p: "1.1rem",
                cursor: "pointer",
                opacity: available ? 1 : 0.55,
                borderRadius: "1.5rem",
                background: selected ? alpha(BRASS, 0.12) : "var(--surface)",
                backdropFilter: "blur(10px)",
                border: `${selected ? 2 : 1}px solid ${selected ? BRASS : "var(--line)"}`,
                transform: selected ? "translateY(-4px)" : "none",
                boxShadow: selected ? `0 16px 48px ${alpha(BRASS, 0.3)}` : "none",
                transition: "transform .25s ease, border-color .25s ease, box-shadow .25s ease, background .25s ease",
                "&:hover": {
                    transform: "translateY(-4px)",
                    borderColor: alpha(BRASS, selected ? 1 : 0.5),
                    boxShadow: `0 14px 44px ${alpha(BRASS, selected ? 0.3 : 0.16)}`,
                },
            }}
        >
            {/* Selected indicator + per-device settings */}
            {selected && (
                <CheckCircleIcon sx={{ position: "absolute", top: 10, left: 12, fontSize: 20, color: BRASS }} />
            )}
            {selected && (
                <Tooltip title={t('devices.settings')}>
                    <IconButton
                        size="small"
                        aria-label="device settings"
                        onClick={(e) => { e.stopPropagation(); onOpenSettings?.(); }}
                        sx={{ position: "absolute", top: 6, right: 6 }}
                    >
                        <SettingsIcon fontSize="small" />
                    </IconButton>
                </Tooltip>
            )}

            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0.75, mb: 2, flexWrap: "wrap" }}>
                {device.type && (
                    <Chip
                        size="small"
                        icon={isBluetooth ? <BluetoothIcon /> : undefined}
                        label={t(`deviceTypes.${device.type}`, { defaultValue: device.type })}
                        color={selected || available ? "primary" : "default"}
                        variant={selected ? "filled" : "outlined"}
                    />
                )}
                {!available && (
                    <Chip size="small" label={t('devices.offline')} color="default" variant="outlined"
                        sx={{ color: "var(--mist)", borderColor: "var(--line)" }} />
                )}
                {isFreeboxPlayer && available && <LockOpenIcon fontSize="small" sx={{ color: "var(--mist)" }} />}
            </Box>

            <Box sx={{
                width: "100%",
                aspectRatio: "1 / 1",
                borderRadius: "1.25rem",
                overflow: "hidden",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: "1px solid var(--line)",
                background: "radial-gradient(120% 120% at 50% 0%, rgba(212,173,95,0.12), rgba(13,20,38,0.6))",
            }}>
                {iconOnly ? (
                    <Box sx={{ color: "var(--brass)", display: "grid", placeItems: "center", opacity: available ? 0.95 : 0.5 }}>
                        {isLocal ? <LaptopMacIcon sx={{ fontSize: 64 }} /> : <GraphicEqIcon sx={{ fontSize: 64 }} />}
                    </Box>
                ) : (
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
                )}
            </Box>

            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", width: "100%" }}>
                <CardContent sx={{ flex: "1 0 auto", pb: 1 }}>
                    <Typography variant="h6" color={available ? "text.primary" : "text.disabled"}>
                        {device.getName()}
                    </Typography>
                    <Typography variant="subtitle2" color={available ? "text.secondary" : "text.disabled"}>
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
        </Card>
    );
}
