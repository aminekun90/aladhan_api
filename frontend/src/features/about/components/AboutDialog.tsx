import { useChangelog } from "@/features/about/hooks/useChangelog";
import { ChangelogVersion, ChangeType, Component, RoadmapStatus } from "@/features/about/types/changelog";
import GitHubIcon from "@mui/icons-material/GitHub";
import {
    Box, Button, Chip, CircularProgress, Dialog, DialogActions, DialogContent,
    Divider, Link, Stack, Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

const TYPE_COLOR: Record<ChangeType, string> = {
    feat: "#3a7d44",
    fix: "#9c6b1f",
    refactor: "#4a5d8a",
    perf: "#6a4a8a",
};

const STATUS_COLOR: Record<RoadmapStatus, string> = {
    "planned": "#4a5d8a",
    "in-progress": "#9c6b1f",
    "idea": "#6b6b6b",
    "done": "#3a7d44",
};

const COMPONENTS: Component[] = ["frontend", "backend"];

export function AboutDialog({ open, onClose }: Readonly<{ open: boolean; onClose?: () => void }>) {
    const { t } = useTranslation();
    const { changelog, isLoading, frontendVersion, backendVersion, isUnseen } = useChangelog();

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth scroll="paper">
            <DialogContent dividers>
                <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1}>
                    <Typography variant="h6">{t("about.titleShort")}</Typography>
                    <Link title="GitHub" href="https://github.com/aminekun90/aladhan_api" target="_blank" rel="noopener" sx={{ color: "inherit" }}>
                        <GitHubIcon />
                    </Link>
                </Stack>

                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                    <Chip size="small" label={`${t("about.frontend")} v${frontendVersion}`} variant="outlined" />
                    {backendVersion && <Chip size="small" label={`${t("about.backend")} v${backendVersion}`} variant="outlined" />}
                </Stack>

                <Typography variant="body2" sx={{ mt: 1.5, color: "text.secondary" }}>
                    {t("about.body")}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle2" gutterBottom>{t("about.whatsNew")}</Typography>
                {isLoading ? (
                    <CircularProgress size={20} />
                ) : (
                    <Stack spacing={2}>
                        {changelog?.versions.map((version) => (
                            <VersionBlock key={version.version} version={version} unseen={isUnseen(version.version)} />
                        ))}
                        {!changelog?.versions.length && (
                            <Typography variant="body2" color="text.secondary">{t("about.noChanges")}</Typography>
                        )}
                    </Stack>
                )}

                {!!changelog?.roadmap.length && (
                    <>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="subtitle2" gutterBottom>{t("about.roadmapTitle")}</Typography>
                        <Stack spacing={1}>
                            {changelog.roadmap.map((item) => (
                                <Stack key={item.id} direction="row" alignItems="center" spacing={1}>
                                    <Chip
                                        size="small"
                                        label={t(`about.roadmapStatus.${item.status}`)}
                                        sx={{ bgcolor: STATUS_COLOR[item.status], color: "#fff", minWidth: 92 }}
                                    />
                                    <Typography variant="body2">{t(item.title)}</Typography>
                                </Stack>
                            ))}
                        </Stack>
                    </>
                )}
            </DialogContent>
            <DialogActions>
                <Button variant="contained" color="primary" onClick={onClose} autoFocus>
                    {t("about.close")}
                </Button>
            </DialogActions>
        </Dialog>
    );
}

function VersionBlock({ version, unseen }: Readonly<{ version: ChangelogVersion; unseen: boolean }>) {
    const { t } = useTranslation();
    return (
        <Box
            sx={{
                p: 1.5, borderRadius: 1,
                border: "1px solid", borderColor: unseen ? "primary.main" : "divider",
                bgcolor: unseen ? "action.hover" : "transparent",
            }}
        >
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                <Typography variant="subtitle2">v{version.version}</Typography>
                <Typography variant="caption" color="text.secondary">{version.date}</Typography>
                {unseen && <Chip size="small" color="primary" label={t("about.new")} />}
            </Stack>
            {COMPONENTS.map((component) => {
                const items = version.changes.filter((c) => c.component === component);
                if (!items.length) return null;
                return (
                    <Box key={component} sx={{ mb: 1 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>{t(`about.${component}`)}</Typography>
                        <Stack spacing={0.5} sx={{ mt: 0.5 }}>
                            {items.map((change, i) => (
                                <Stack key={i} direction="row" alignItems="flex-start" spacing={1}>
                                    <Chip
                                        size="small"
                                        label={t(`about.types.${change.type}`)}
                                        sx={{ bgcolor: TYPE_COLOR[change.type], color: "#fff", height: 18, fontSize: "0.65rem" }}
                                    />
                                    <Typography variant="body2">{change.summary}</Typography>
                                </Stack>
                            ))}
                        </Stack>
                    </Box>
                );
            })}
        </Box>
    );
}
