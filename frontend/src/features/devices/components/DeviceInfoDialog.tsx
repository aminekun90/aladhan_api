import {
    controlDevice,
    DeviceInfo,
    getDeviceInfo,
    PlayerAction,
    setDeviceVolume,
} from "@/features/devices/api/apiDevice";
import { Device } from "@/features/devices/types/device";
import { logger } from "@/utils/logger";
import CloseIcon from "@mui/icons-material/Close";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import {
    Box,
    Chip,
    CircularProgress,
    Dialog,
    DialogContent,
    DialogTitle,
    Divider,
    IconButton,
    Slider,
    Stack,
    Tooltip,
    Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

/** One label/value row with an optional copy-to-clipboard button. */
function InfoRow({ label, value, mono }: Readonly<{ label: string; value?: string | null; mono?: boolean }>) {
    if (!value) return null;
    const copy = () => navigator.clipboard?.writeText(value).catch(() => undefined);
    return (
        <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1} sx={{ py: 0.6 }}>
            <Typography variant="body2" sx={{ color: "var(--mist)", minWidth: 120 }}>{label}</Typography>
            <Stack direction="row" alignItems="center" spacing={0.5} sx={{ minWidth: 0 }}>
                <Typography
                    variant="body2"
                    sx={{ fontFamily: mono ? "monospace" : undefined, wordBreak: "break-all", textAlign: "right" }}
                >
                    {value}
                </Typography>
                <Tooltip title="Copier">
                    <IconButton size="small" onClick={copy} aria-label={`copy ${label}`}>
                        <ContentCopyIcon sx={{ fontSize: 14 }} />
                    </IconButton>
                </Tooltip>
            </Stack>
        </Stack>
    );
}

export function DeviceInfoDialog({
    device,
    open,
    onClose,
}: Readonly<{ device: Device | null; open: boolean; onClose: () => void }>) {
    const { t } = useTranslation();
    const deviceId = device?.getId();

    const { data: info, isLoading, isError } = useQuery<DeviceInfo>({
        queryKey: ["deviceInfo", deviceId],
        queryFn: () => getDeviceInfo(deviceId as number),
        enabled: open && !!deviceId,
        refetchInterval: open ? 30_000 : false,
    });

    const [volume, setVolume] = useState<number>(0);
    useEffect(() => {
        // Sync the slider with the volume fetched from the device (external state).
        // eslint-disable-next-line react-hooks/set-state-in-effect
        if (typeof info?.volume === "number") setVolume(info.volume);
    }, [info?.volume]);

    const sendControl = (action: PlayerAction) => () => {
        if (!deviceId) return;
        controlDevice(deviceId, action).catch((e) => logger.error("control failed", e));
    };
    const commitVolume = (v: number) => {
        if (!deviceId) return;
        setDeviceVolume(deviceId, v).catch((e) => logger.error("volume failed", e));
    };

    const controllable =
        !!deviceId &&
        info?.online === true &&
        info?.control_channel !== "host" &&
        info?.control_channel !== "airmedia";

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span>{device?.getName() || t("deviceInfo.title", { defaultValue: "Infos appareil" })}</span>
                <IconButton onClick={onClose} aria-label="close"><CloseIcon /></IconButton>
            </DialogTitle>
            <DialogContent dividers>
                {isLoading && (
                    <Box sx={{ display: "grid", placeItems: "center", py: 4 }}>
                        <CircularProgress size={22} sx={{ color: "var(--brass)" }} />
                    </Box>
                )}
                {isError && (
                    <Typography color="error" variant="body2">
                        {t("deviceInfo.error", { defaultValue: "Impossible de charger les infos de l'appareil." })}
                    </Typography>
                )}
                {info && (
                    <Stack spacing={1}>
                        <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap" }}>
                            {info.type && (
                                <Chip size="small" color="primary" variant="outlined"
                                    label={t(`deviceTypes.${info.type}`, { defaultValue: info.type })} />
                            )}
                            <Chip size="small" variant="outlined"
                                color={info.online ? "success" : "default"}
                                label={info.online
                                    ? t("devices.online", { defaultValue: "En ligne" })
                                    : t("devices.offline", { defaultValue: "Hors ligne" })} />
                            {info.standby && (
                                <Chip size="small" color="warning" variant="outlined"
                                    label={t("devices.standby", { defaultValue: "Veille" })} />
                            )}
                        </Stack>

                        <Divider sx={{ my: 0.5 }} />
                        <InfoRow label={t("deviceInfo.vendor", { defaultValue: "Fabricant" })} value={info.vendor} />
                        <InfoRow label={t("deviceInfo.model", { defaultValue: "Modèle" })} value={info.model} />
                        <InfoRow label={t("deviceInfo.hostname", { defaultValue: "Nom d'hôte" })} value={info.hostname} />
                        <InfoRow label="IPv4" value={info.ipv4.join(", ")} mono />
                        <InfoRow label="IPv6" value={info.ipv6.join(", ")} mono />
                        <InfoRow label={t("deviceInfo.mac", { defaultValue: "Adresse MAC" })} value={info.mac} mono />
                        <InfoRow label="UID" value={info.uid} mono />
                        <InfoRow label={t("deviceInfo.control", { defaultValue: "Canal de contrôle" })} value={info.control_channel} />
                        <InfoRow
                            label={t("deviceInfo.location", { defaultValue: "Localisation" })}
                            value={info.city ? [info.city, info.country].filter(Boolean).join(", ") : null}
                        />
                        <InfoRow
                            label={t("deviceInfo.coordinates", { defaultValue: "Coordonnées" })}
                            value={info.latitude != null && info.longitude != null ? `${info.latitude.toFixed(4)}, ${info.longitude.toFixed(4)}` : null}
                            mono
                        />
                        {info.note && (
                            <Typography variant="caption" sx={{ color: "var(--mist)", mt: 0.5 }}>{info.note}</Typography>
                        )}

                        {controllable && (
                            <>
                                <Divider sx={{ my: 1 }} />
                                <Stack direction="row" alignItems="center" justifyContent="center" spacing={1}>
                                    <IconButton aria-label="play" onClick={sendControl("play")}><PlayArrowIcon /></IconButton>
                                    <IconButton aria-label="pause" onClick={sendControl("pause")}><PauseIcon /></IconButton>
                                    <IconButton aria-label="stop" onClick={sendControl("stop")}><StopIcon /></IconButton>
                                </Stack>
                                <Stack direction="row" alignItems="center" spacing={2} sx={{ px: 1 }}>
                                    <Typography variant="caption" sx={{ color: "var(--mist)" }}>
                                        {t("deviceInfo.volume", { defaultValue: "Volume" })}
                                    </Typography>
                                    <Slider
                                        size="small"
                                        value={volume}
                                        min={0}
                                        max={100}
                                        valueLabelDisplay="auto"
                                        onChange={(_, v) => setVolume(v as number)}
                                        onChangeCommitted={(_, v) => commitVolume(v as number)}
                                        sx={{ color: "var(--brass)" }}
                                    />
                                </Stack>
                            </>
                        )}
                    </Stack>
                )}
            </DialogContent>
        </Dialog>
    );
}
