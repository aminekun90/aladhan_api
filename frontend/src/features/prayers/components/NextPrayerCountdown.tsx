import { getPrayers } from "@/features/prayers/api/apiPrayer";
import { Box, Stack, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

const DAY_MS = 24 * 60 * 60 * 1000;
const pad = (n: number) => String(n).padStart(2, "0");

/**
 * Live countdown to the next prayer, with a gilded progress arc between the
 * previous and next prayer. Shares the prayers query cache (same queryKey).
 */
export function NextPrayerCountdown({ coord }: Readonly<{ coord: { lat?: number; lon?: number } }>) {
    const { t } = useTranslation();
    const { data } = useQuery({
        queryKey: ["prayers", coord.lat, coord.lon],
        queryFn: () => getPrayers(coord),
    });

    const [now, setNow] = useState(() => Date.now());
    useEffect(() => {
        const id = setInterval(() => setNow(Date.now()), 1000);
        return () => clearInterval(id);
    }, []);

    if (!data?.prayers?.length) return null;
    const list = data.prayers;
    const times = list.map((p) => p.getTime().getTime());

    // Next prayer = first one still ahead; after Isha it rolls to tomorrow's first.
    let idx = times.findIndex((ms) => ms >= now);
    let nextMs: number;
    let prevMs: number;
    let nextName: string;
    if (idx === -1) {
        nextName = list[0].getName();
        nextMs = times[0] + DAY_MS;
        prevMs = times[times.length - 1];
    } else {
        nextName = list[idx].getName();
        nextMs = times[idx];
        prevMs = idx === 0 ? times[times.length - 1] - DAY_MS : times[idx - 1];
    }

    const remaining = Math.max(0, nextMs - now);
    const h = Math.floor(remaining / 3_600_000);
    const m = Math.floor((remaining % 3_600_000) / 60_000);
    const s = Math.floor((remaining % 60_000) / 1000);
    const progress = Math.min(1, Math.max(0, (now - prevMs) / (nextMs - prevMs)));
    const name = nextName.charAt(0).toUpperCase() + nextName.slice(1);

    return (
        <Box sx={{ mt: { xs: 3, md: 4 }, animation: "rise .8s ease both" }}>
            <Typography sx={{ fontSize: 11, letterSpacing: "0.32em", textTransform: "uppercase", color: "var(--brass)", mb: 1 }}>
                {t("prayers.nextPrayer", { defaultValue: "Prochaine prière" })}
            </Typography>

            <Stack direction="row" alignItems="baseline" justifyContent="center" spacing={1.5} sx={{ flexWrap: "wrap" }}>
                <Typography sx={{ fontFamily: "var(--font-display)", fontSize: { xs: "1.6rem", md: "2rem" }, color: "var(--parchment)" }}>
                    {name}
                </Typography>
                <Typography
                    sx={{
                        fontFamily: "var(--font-display)",
                        fontVariantNumeric: "tabular-nums",
                        fontSize: { xs: "1.9rem", md: "2.4rem" },
                        letterSpacing: "0.02em",
                        color: "var(--brass-bright)",
                        textShadow: "0 0 32px rgba(212, 173, 95, 0.45)",
                    }}
                >
                    {h > 0 ? `${pad(h)}:` : ""}{pad(m)}:{pad(s)}
                </Typography>
            </Stack>

            {/* Progress between the previous and next prayer */}
            <Box sx={{ mx: "auto", mt: 1.75, width: { xs: 220, md: 300 }, height: 3, borderRadius: 3, background: "var(--line)", overflow: "hidden" }}>
                <Box sx={{ width: `${progress * 100}%`, height: "100%", borderRadius: 3, background: "linear-gradient(90deg, rgba(212,173,95,0.5), var(--brass-bright))", transition: "width 1s linear" }} />
            </Box>
        </Box>
    );
}
