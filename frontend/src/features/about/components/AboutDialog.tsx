import { useChangelog } from "@/features/about/hooks/useChangelog";
import { useUpdateStatus } from "@/features/about/hooks/useUpdateStatus";
import { ChangelogVersion, ChangeType, Component, RoadmapStatus } from "@/features/about/types/changelog";
import GitHubIcon from "@mui/icons-material/GitHub";
import {
    Alert, Box, Button, Chip, CircularProgress, Dialog, DialogContent,
    IconButton, Link, Stack, Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { ReactNode } from "react";
import { useTranslation } from "react-i18next";

const TYPE_COLOR: Record<ChangeType, string> = {
    feat: "#5a9e6f",
    fix: "#c9962f",
    refactor: "#6f86c4",
    perf: "#9a78c4",
};

const STATUS_COLOR: Record<RoadmapStatus, string> = {
    "planned": "#6f86c4",
    "in-progress": "#c9962f",
    "idea": "#8a8a8a",
    "done": "#5a9e6f",
};

const COMPONENTS: Component[] = ["frontend", "backend"];

const PAPER_SX = {
    background: "linear-gradient(180deg, rgba(20,28,48,0.98), rgba(13,20,38,0.98))",
    border: "1px solid var(--line)",
    borderRadius: "1.25rem",
    backdropFilter: "blur(12px)",
    color: "var(--parchment)",
} as const;

function Eyebrow({ children }: Readonly<{ children: ReactNode }>) {
    return (
        <Typography sx={{ fontSize: 11, letterSpacing: "0.22em", textTransform: "uppercase", color: "var(--brass)", mb: 1.25 }}>
            {children}
        </Typography>
    );
}

export function AboutDialog({ open, onClose }: Readonly<{ open: boolean; onClose?: () => void }>) {
    const { t } = useTranslation();
    const { changelog, isLoading, frontendVersion, backendVersion, isUnseen } = useChangelog();
    const { status, approve, isApproving, isApproved, force, isForcing, isForced } = useUpdateStatus({ enabled: open });

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth scroll="paper" PaperProps={{ sx: PAPER_SX }}>
            {/* Branded header */}
            <Box sx={{ position: "relative", px: 3, pt: 3, pb: 2.5, borderBottom: "1px solid var(--line)" }}>
                <Box sx={{ position: "absolute", left: 0, bottom: -1, height: 2, width: "38%", background: "linear-gradient(90deg, var(--brass), transparent)" }} />
                <IconButton aria-label={t("about.close")} onClick={onClose} sx={{ position: "absolute", top: 12, right: 12, color: "var(--mist)" }}>
                    <CloseIcon fontSize="small" />
                </IconButton>
                <Stack direction="row" alignItems="center" spacing={1.25}>
                    <Box sx={{ width: 12, height: 22, borderRadius: "50% 50% 0 0 / 70% 70% 0 0", border: "1.5px solid var(--brass)", borderBottom: "none" }} />
                    <Typography sx={{ fontFamily: "var(--font-display)", fontSize: "1.4rem", letterSpacing: "0.04em" }}>
                        {t("about.titleShort")}
                    </Typography>
                </Stack>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1.75 }}>
                    <Chip size="small" label={`${t("about.frontend")} v${frontendVersion}`} sx={CHIP_SX} />
                    {backendVersion && <Chip size="small" label={`${t("about.backend")} v${backendVersion}`} sx={CHIP_SX} />}
                    <Box sx={{ flex: 1 }} />
                    <Link title="GitHub" href="https://github.com/aminekun90/aladhan_api" target="_blank" rel="noopener" sx={{ color: "var(--mist)", "&:hover": { color: "var(--brass)" } }}>
                        <GitHubIcon fontSize="small" />
                    </Link>
                </Stack>
                <Typography variant="body2" sx={{ mt: 1.75, color: "var(--mist)", lineHeight: 1.6 }}>
                    {t("about.body")}
                </Typography>
            </Box>

            <DialogContent sx={{ px: 3, py: 2.5 }}>
                {isApproved ? (
                    <Alert severity="success" variant="outlined" sx={{ mb: 2.5 }}>{t("about.update.deploying")}</Alert>
                ) : status?.pending && (
                    <Alert
                        severity="info"
                        variant="outlined"
                        sx={{ mb: 2.5 }}
                        action={
                            <Button color="inherit" size="small" variant="outlined" onClick={() => approve()} disabled={isApproving}>
                                {isApproving ? t("about.update.approving") : t("about.update.approve")}
                            </Button>
                        }
                    >
                        {t("about.update.available", { version: status.newVersion })}
                    </Alert>
                )}

                <Eyebrow>{t("about.whatsNew")}</Eyebrow>
                {isLoading ? (
                    <CircularProgress size={20} sx={{ color: "var(--brass)" }} />
                ) : (
                    <Box sx={{ position: "relative", pl: 2.5, "&::before": { content: '""', position: "absolute", left: 4, top: 4, bottom: 4, width: "1px", background: "var(--line)" } }}>
                        <Stack spacing={2.5}>
                            {changelog?.versions.map((version) => (
                                <VersionBlock key={version.version} version={version} unseen={isUnseen(version.version)} />
                            ))}
                            {!changelog?.versions.length && (
                                <Typography variant="body2" sx={{ color: "var(--mist)" }}>{t("about.noChanges")}</Typography>
                            )}
                        </Stack>
                    </Box>
                )}

                {!!changelog?.roadmap.length && (
                    <Box sx={{ mt: 3.5 }}>
                        <Eyebrow>{t("about.roadmapTitle")}</Eyebrow>
                        <Stack spacing={1.25}>
                            {changelog.roadmap.map((item) => (
                                <Stack key={item.id} direction="row" alignItems="center" spacing={1.25}>
                                    <Chip
                                        size="small"
                                        label={t(`about.roadmapStatus.${item.status}`)}
                                        sx={{ bgcolor: STATUS_COLOR[item.status], color: "#0d1426", fontWeight: 600, minWidth: 96 }}
                                    />
                                    <Typography variant="body2">{t(item.title)}</Typography>
                                </Stack>
                            ))}
                        </Stack>
                    </Box>
                )}

                {/* Manual fallback: force a redeploy to pull the newest image. */}
                <Box sx={{ mt: 3.5, pt: 2, borderTop: "1px solid var(--line)" }}>
                    {isForced ? (
                        <Alert severity="success" variant="outlined">{t("about.update.deploying")}</Alert>
                    ) : (
                        <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={1.5}>
                            <Typography variant="caption" sx={{ color: "var(--mist)" }}>{t("about.update.forceHint")}</Typography>
                            <Button
                                size="small"
                                variant="outlined"
                                onClick={() => force()}
                                disabled={isForcing}
                                sx={{ flexShrink: 0, borderColor: "var(--line)", color: "var(--parchment)", "&:hover": { borderColor: "var(--brass)" } }}
                            >
                                {isForcing ? t("about.update.forcing") : t("about.update.force")}
                            </Button>
                        </Stack>
                    )}
                </Box>
            </DialogContent>
        </Dialog>
    );
}

const CHIP_SX = {
    fontFamily: "var(--font-display)",
    color: "var(--parchment)",
    border: "1px solid var(--line)",
    background: "transparent",
} as const;

function VersionBlock({ version, unseen }: Readonly<{ version: ChangelogVersion; unseen: boolean }>) {
    const { t } = useTranslation();
    return (
        <Box sx={{ position: "relative" }}>
            {/* timeline node */}
            <Box sx={{
                position: "absolute", left: -24, top: 5, width: 9, height: 9, borderRadius: "50%",
                background: unseen ? "var(--brass)" : "var(--surface)",
                border: `1.5px solid ${unseen ? "var(--brass)" : "var(--line)"}`,
                boxShadow: unseen ? "0 0 0 4px rgba(212,173,95,0.15)" : "none",
            }} />
            <Stack direction="row" alignItems="baseline" spacing={1} sx={{ mb: 1 }}>
                <Typography sx={{ fontFamily: "var(--font-display)", fontSize: "1rem", color: "var(--parchment)" }}>
                    v{version.version}
                </Typography>
                <Typography variant="caption" sx={{ color: "var(--mist)" }}>{version.date}</Typography>
                {unseen && <Chip size="small" label={t("about.new")} sx={{ height: 18, bgcolor: "var(--brass)", color: "#0d1426", fontWeight: 700, fontSize: "0.62rem" }} />}
            </Stack>
            {COMPONENTS.map((component) => {
                const items = version.changes.filter((c) => c.component === component);
                if (!items.length) return null;
                return (
                    <Box key={component} sx={{ mb: 1.25 }}>
                        <Typography sx={{ fontSize: 10, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--mist)", mb: 0.5 }}>
                            {t(`about.${component}`)}
                        </Typography>
                        <Stack spacing={0.75}>
                            {items.map((change, i) => (
                                <Stack key={i} direction="row" alignItems="center" spacing={1}>
                                    <Box sx={{ width: 6, height: 6, borderRadius: "2px", flexShrink: 0, background: TYPE_COLOR[change.type] }} />
                                    <Typography variant="body2" sx={{ color: "var(--parchment)", opacity: 0.92 }}>
                                        {change.summary}
                                    </Typography>
                                </Stack>
                            ))}
                        </Stack>
                    </Box>
                );
            })}
        </Box>
    );
}
