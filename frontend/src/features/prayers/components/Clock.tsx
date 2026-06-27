import { Box, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

/**
 * Hero time display. Large optical-serif clock with a tracked date overline,
 * formatted in the active language.
 */
export function DateClock() {
    const { i18n } = useTranslation();
    const [now, setNow] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => setNow(new Date()), 1000);
        return () => clearInterval(interval);
    }, []);

    const locale = i18n.resolvedLanguage;
    const time = Intl.DateTimeFormat(locale, { hour: "2-digit", minute: "2-digit" }).format(now);
    const seconds = Intl.DateTimeFormat(locale, { second: "2-digit" }).format(now);
    const date = Intl.DateTimeFormat(locale, { weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(now);

    return (
        <Box sx={{ textAlign: "center" }}>
            <Typography
                component="div"
                sx={{
                    fontFamily: "var(--font-display)",
                    fontWeight: 300,
                    lineHeight: 1,
                    fontSize: { xs: "4.5rem", sm: "6rem", md: "7.5rem" },
                    letterSpacing: "-0.03em",
                    color: "var(--parchment)",
                    fontVariantNumeric: "tabular-nums",
                    textShadow: "0 0 60px rgba(212, 173, 95, 0.25)",
                }}
            >
                {time}
                <Box
                    component="span"
                    sx={{
                        fontSize: { xs: "1.4rem", md: "2rem" },
                        color: "var(--brass)",
                        ml: 1,
                        verticalAlign: "super",
                        fontVariantNumeric: "tabular-nums",
                    }}
                >
                    {seconds}
                </Box>
            </Typography>
            <Typography
                sx={{
                    mt: 1.5,
                    textTransform: "uppercase",
                    letterSpacing: "0.3em",
                    fontSize: { xs: "0.65rem", md: "0.78rem" },
                    color: "var(--mist)",
                    fontWeight: 500,
                }}
            >
                {date}
            </Typography>
        </Box>
    );
}
