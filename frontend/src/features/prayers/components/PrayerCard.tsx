import { BRASS, BRASS_BRIGHT } from "@/components/ui";
import { alpha, Card, CardActionArea, styled, Tooltip, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

/** Gilded prayer-time card; `next` highlights the upcoming prayer. */
const PrayerRoot = styled(Card, {
  shouldForwardProp: (prop) => prop !== "next",
})<{ next?: boolean }>(({ next }) => ({
  position: "relative",
  overflow: "hidden",
  borderRadius: "1.25rem",
  backgroundColor: next ? alpha(BRASS, 0.12) : "var(--surface)",
  backgroundImage: next
    ? `radial-gradient(120% 90% at 50% 0%, ${alpha(BRASS, 0.28)}, transparent 65%)`
    : "none",
  border: `1px solid ${next ? alpha(BRASS, 0.55) : "var(--line)"}`,
  boxShadow: next ? "none" : "inset 0 1px 0 rgba(236, 230, 214, 0.05)",
  animation: next ? "breathe 4.5s ease-in-out infinite" : "none",
  backdropFilter: "blur(14px)",
  transition: "transform .25s ease, border-color .25s ease, box-shadow .25s ease",
  "&:hover": {
    transform: "translateY(-4px)",
    borderColor: alpha(BRASS, 0.5),
    boxShadow: `0 14px 44px ${alpha(BRASS, next ? 0.32 : 0.14)}`,
  },
  // gilded hairline at the very top — the mihrab arch's keystone
  "&::before": {
    content: '""',
    position: "absolute",
    top: 0,
    left: "50%",
    transform: "translateX(-50%)",
    width: next ? "70%" : "34%",
    height: "2px",
    borderRadius: "2px",
    background: `linear-gradient(90deg, transparent, ${next ? BRASS_BRIGHT : BRASS}, transparent)`,
    transition: "width .25s ease",
  },
}));

const TimeText = styled("span")({
  fontFamily: "var(--font-display)",
  fontWeight: 400,
  lineHeight: 1.05,
  color: "var(--parchment)",
  fontVariantNumeric: "tabular-nums",
  whiteSpace: "nowrap",
  display: "inline-flex",
  alignItems: "baseline",
  gap: "0.28em",
});

const Meridiem = styled("span")({
  fontSize: "0.42em",
  fontWeight: 600,
  letterSpacing: "0.08em",
  color: "var(--mist)",
});

export function PrayerCard(props: {
  readonly selectedCard?: string;
  readonly id: string;
  readonly title: string;
  readonly date: Date;
  readonly timezone: string;
  readonly setSelectedCard: (id: string) => void;
  readonly isNext?: boolean;
}) {
  const { t, i18n } = useTranslation();
  const isActive = props.selectedCard === props.id;
  const next = !!props.isNext;

  const parts = Intl.DateTimeFormat(i18n.resolvedLanguage, { hour: "2-digit", minute: "2-digit" }).formatToParts(props.date);
  const hour = parts.find((p) => p.type === "hour")?.value ?? "";
  const minute = parts.find((p) => p.type === "minute")?.value ?? "";
  const meridiem = parts.find((p) => p.type === "dayPeriod")?.value;

  return (
    <Tooltip title={`${props.title} · ${props.timezone}`} arrow>
      <PrayerRoot next={next}>
        <CardActionArea
          onClick={() => props.setSelectedCard(props.id)}
          data-active={isActive ? "" : undefined}
          sx={{ px: 1.5, py: 2.25, display: "flex", flexDirection: "column", alignItems: "center", gap: 0.75 }}
        >
          {next && (
            <Typography sx={{ position: "absolute", top: 8, right: 10, fontSize: "0.55rem", letterSpacing: "0.25em", fontWeight: 700, color: BRASS_BRIGHT }}>
              {t('prayers.next')}
            </Typography>
          )}
          <Typography sx={{ textTransform: "uppercase", letterSpacing: "0.22em", fontSize: "0.66rem", fontWeight: 600, color: next ? BRASS_BRIGHT : "var(--mist)" }}>
            {props.title}
          </Typography>
          <TimeText sx={{ fontSize: { xs: "1.8rem", md: "2.15rem" } }}>
            {hour}:{minute}
            {meridiem && <Meridiem>{meridiem}</Meridiem>}
          </TimeText>
        </CardActionArea>
      </PrayerRoot>
    </Tooltip>
  );
}
