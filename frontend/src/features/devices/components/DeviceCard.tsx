import { controlDevice, getDeviceState, PlayerAction } from "@/features/devices/api/apiDevice";
import freebox from "@/assets/freebox-devialet.png";
import symfonisk from "@/assets/symfonisk.jpg";
import { BRASS } from "@/components/ui";
import { Device } from "@/features/devices/types/device";
import { logger } from "@/utils/logger";
import BluetoothIcon from "@mui/icons-material/Bluetooth";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import AirplayIcon from "@mui/icons-material/Airplay";
import GraphicEqIcon from "@mui/icons-material/GraphicEq";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
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
    CircularProgress,
    IconButton,
    Stack,
    styled,
    Tooltip,
    Typography,
    useTheme,
} from "@mui/material";
import { useToast } from "@aminekun90/react-toast";
import { useMutation, useQuery } from "@tanstack/react-query";
import { MouseEvent, useState } from "react";
import { useTranslation } from "react-i18next";

/** Selectable gilded device card. `selected` glows; `available` dims when offline. */
const DeviceRoot = styled(Card, {
    shouldForwardProp: (prop) => prop !== "selected" && prop !== "available",
})<{ selected?: boolean; available?: boolean }>(({ selected, available }) => ({
    position: "relative",
    display: "flex",
    flexDirection: "column",
    padding: "1.1rem",
    cursor: "pointer",
    opacity: available ? 1 : 0.55,
    borderRadius: "1.5rem",
    background: selected ? alpha(BRASS, 0.12) : "var(--surface)",
    backdropFilter: "blur(16px)",
    border: `${selected ? 2 : 1}px solid ${selected ? BRASS : "var(--line)"}`,
    transform: selected ? "translateY(-4px)" : "none",
    boxShadow: selected
        ? `inset 0 1px 0 rgba(236, 230, 214, 0.1), 0 18px 52px ${alpha(BRASS, 0.32)}`
        : "inset 0 1px 0 rgba(236, 230, 214, 0.05)",
    transition: "transform .25s ease, border-color .25s ease, box-shadow .25s ease, background .25s ease",
    "&:hover": {
        transform: "translateY(-4px)",
        borderColor: alpha(BRASS, selected ? 1 : 0.5),
        boxShadow: `0 14px 44px ${alpha(BRASS, selected ? 0.3 : 0.16)}`,
    },
}));

export default function DeviceCard({
    device,
    available = true,
    selected = false,
    onClick,
    onOpenSettings,
    onOpenInfo,
}: Readonly<{
    device: Device;
    available?: boolean;
    selected?: boolean;
    onClick?: () => void;
    onOpenSettings?: () => void;
    onOpenInfo?: () => void;
}>) {
    const theme = useTheme();
    const { t } = useTranslation();
    const { show } = useToast();
    const [isPlaying, setIsPlaying] = useState(false);

    const notify = (type: "success" | "error", message: string) =>
        show({ type, title: t("toast.control.title"), message, position: "top-right", duration: 3000, progressBar: true });

    const controlMutation = useMutation({
        mutationFn: (action: PlayerAction) => {
            const id = device.getId();
            if (!id) return Promise.reject(new Error("Device has no id"));
            return controlDevice(id, action);
        },
        onSuccess: (_result, action) => notify("success", t(`toast.control.${action}`)),
        onError: (error, action) => {
            logger.error("Device control failed:", error);
            // Revert the optimistic play/pause toggle.
            if (action === "play") setIsPlaying(false);
            if (action === "pause") setIsPlaying(true);
            notify("error", t("toast.control.error", { device: device.getName() }));
        },
    });

    const pendingAction = controlMutation.isPending ? controlMutation.variables : undefined;

    const sendControl = (action: PlayerAction) => (event: MouseEvent) => {
        event.stopPropagation(); // don't trigger card selection
        if (action === "play") setIsPlaying(true);
        if (action === "pause") setIsPlaying(false);
        controlMutation.mutate(action);
    };

    const isFreeboxPlayer = device.type === "freebox_player";
    const isAirMedia = device.type === "freebox_airmedia";
    const isBluetooth = device.type === "bluetooth_speaker";

    // Freebox players stay reachable when turned off with the remote (standby);
    // playback then routes through AirMedia. Surface that so the card doesn't look
    // broken. Only polled while the player is reachable.
    const deviceId = device.getId();
    const { data: liveState } = useQuery({
        queryKey: ["deviceState", deviceId],
        queryFn: () => getDeviceState(deviceId as number),
        enabled: isFreeboxPlayer && available && !!deviceId,
        refetchInterval: 30_000,
    });
    const isStandby = liveState?.standby === true;
    const isLocal = device.type === "local_player";
    // No product photo for these — AirMedia targets are diverse (TV, speaker…)
    // reachable via the Freebox's AirPlay-based casting, so show an icon, not a
    // misleading Sonos/Freebox photo.
    const iconOnly = isBluetooth || isLocal || isAirMedia;
    // Transport controls only make sense for a reachable network player.
    const controllable = available && !!device.getId() && !isBluetooth && !isLocal;

    let deviceImage = symfonisk;
    if (isFreeboxPlayer || device.getRawAttributes().device_model === "fbx7hd-delta") {
        deviceImage = freebox;
    }

    return (
        <DeviceRoot
            selected={selected}
            available={available}
            onClick={onClick}
            role="button"
            aria-pressed={selected}
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onClick?.(); }}
            sx={{ width: { xs: 150, sm: 180, md: 200 } }}
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
                {isStandby && (
                    <Tooltip title={t('devices.standbyHint')}>
                        <Chip size="small" label={t('devices.standby')} color="warning" variant="outlined" />
                    </Tooltip>
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
                        {isLocal
                            ? <LaptopMacIcon sx={{ fontSize: 64 }} />
                            : isAirMedia
                                ? <AirplayIcon sx={{ fontSize: 64 }} />
                                : <GraphicEqIcon sx={{ fontSize: 64 }} />}
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
                    <Stack direction="row" alignItems="center" justifyContent="center" spacing={0.75}>
                        {isPlaying && available && (
                            <Box sx={{ display: "flex", alignItems: "flex-end", gap: "2px", height: 11 }}>
                                {[0, 1, 2, 3].map((i) => (
                                    <Box key={i} className="eq-bar" sx={{ width: "2.5px", height: "100%", borderRadius: "1px", background: "var(--brass-bright)" }} />
                                ))}
                            </Box>
                        )}
                        <Typography variant="subtitle2" color={available ? "text.secondary" : "text.disabled"}>
                            {device.getPlayingTitle().title}
                        </Typography>
                    </Stack>
                </CardContent>

                <Box sx={{ display: "flex", alignItems: "center", pb: 1 }}>
                    <Tooltip title={t('devices.info', { defaultValue: 'Infos & réseau' })}>
                        <IconButton aria-label="device info"
                            onClick={(e) => { e.stopPropagation(); onOpenInfo?.(); }}>
                            <InfoOutlinedIcon fontSize="small" />
                        </IconButton>
                    </Tooltip>
                    <IconButton aria-label="previous" disabled={!controllable || controlMutation.isPending} onClick={sendControl("previous")}>
                        {pendingAction === "previous"
                            ? <CircularProgress size={20} />
                            : theme.direction === "rtl" ? <SkipNextIcon /> : <SkipPreviousIcon />}
                    </IconButton>
                    <IconButton aria-label="play/pause" disabled={!controllable || controlMutation.isPending}
                        onClick={sendControl(isPlaying ? "pause" : "play")}>
                        {pendingAction === "play" || pendingAction === "pause"
                            ? <CircularProgress size={32} />
                            : isPlaying
                                ? <PauseIcon sx={{ height: 38, width: 38 }} />
                                : <PlayArrowIcon sx={{ height: 38, width: 38 }} />}
                    </IconButton>
                    <IconButton aria-label="next" disabled={!controllable || controlMutation.isPending} onClick={sendControl("next")}>
                        {pendingAction === "next"
                            ? <CircularProgress size={20} />
                            : theme.direction === "rtl" ? <SkipPreviousIcon /> : <SkipNextIcon />}
                    </IconButton>
                </Box>
            </Box>
        </DeviceRoot>
    );
}
