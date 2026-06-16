import { alpha, Box, Card, CardActionArea, Tooltip, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

const BRASS = "#d4ad5f";
const BRASS_BRIGHT = "#ecca7e";

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

  const time = Intl.DateTimeFormat(i18n.resolvedLanguage, { hour: "2-digit", minute: "2-digit" }).format(props.date);

  return (
    <Tooltip title={`${props.title} · ${props.timezone}`} arrow>
      <Card
        sx={{
          position: "relative",
          overflow: "hidden",
          borderRadius: "1.25rem",
          backgroundColor: next ? alpha(BRASS, 0.12) : "var(--surface)",
          backgroundImage: next
            ? `radial-gradient(120% 90% at 50% 0%, ${alpha(BRASS, 0.28)}, transparent 65%)`
            : "none",
          border: `1px solid ${next ? alpha(BRASS, 0.55) : "var(--line)"}`,
          boxShadow: next ? `0 10px 40px ${alpha(BRASS, 0.25)}` : "none",
          backdropFilter: "blur(8px)",
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
        }}
      >
        <CardActionArea
          onClick={() => props.setSelectedCard(props.id)}
          data-active={isActive ? "" : undefined}
          sx={{
            px: 1.5,
            py: 2.25,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 0.75,
          }}
        >
          {next && (
            <Typography
              sx={{
                position: "absolute",
                top: 8,
                right: 10,
                fontSize: "0.55rem",
                letterSpacing: "0.25em",
                fontWeight: 700,
                color: BRASS_BRIGHT,
              }}
            >
              {t('prayers.next')}
            </Typography>
          )}
          <Typography
            sx={{
              textTransform: "uppercase",
              letterSpacing: "0.22em",
              fontSize: "0.66rem",
              fontWeight: 600,
              color: next ? BRASS_BRIGHT : "var(--mist)",
            }}
          >
            {props.title}
          </Typography>
          <Box
            component="span"
            sx={{
              fontFamily: "var(--font-display)",
              fontWeight: 400,
              fontSize: { xs: "1.7rem", md: "2rem" },
              lineHeight: 1.05,
              color: "var(--parchment)",
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {time}
          </Box>
        </CardActionArea>
      </Card>
    </Tooltip>
  );
}
