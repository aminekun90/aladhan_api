import { Card, CardActionArea, CardContent, Typography } from "@mui/material";

export function PrayerCard(props: {
  readonly selectedCard?: string;
  readonly id: string;
  readonly title: string;
  readonly date: Date;
  readonly setSelectedCard: (id: string) => void;
  readonly isNext?: boolean;
}) {
  const isActive = props.selectedCard === props.id;

  return (
    <Card
      sx={{
        width: "100%",
        position: "relative",
        borderRadius: "1.5rem",
        padding: "0.5rem",
        background: "rgba(255,255,255,0.15)",
        backdropFilter: "blur(2px) saturate(180%)",
        border: "0.0625rem solid rgba(255,255,255,0.4)",
        boxShadow:
          "0 8px 32px rgba(31, 38, 135, 0.2), inset 0 4px 20px rgba(255,255,255,0.3)",
        transition: "all 0.25s ease",
        "&:hover": {
          boxShadow:
            "0 10px 40px rgba(31, 38, 135, 0.25), inset 0 6px 24px rgba(255,255,255,0.4)",
        },
        "&::after": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background: "rgba(255,255,255,0.1)",
          borderRadius: "1.5rem",
          backdropFilter: "blur(1px)",
          boxShadow:
            "inset -10px -8px 0px -11px rgba(255,255,255,1), inset 0px -9px 0px -8px rgba(255,255,255,1)",
          opacity: 0.6,
          zIndex: -1,
          filter: "blur(1px) drop-shadow(5px 2px 4px rgba(0,0,0,0.3)) brightness(115%)",
          pointerEvents: "none",
        },
      }}
    >
      <CardActionArea
        key={props.id}
        onClick={() => props.setSelectedCard(props.id)}
        data-active={isActive ? "" : undefined}
        data-next={props.isNext ? "" : undefined}
        sx={{
          height: "100%",
          borderRadius: "1.5rem",
          transition: "all 0.25s ease",
          "&[data-active]": {
            backgroundColor: "rgba(100, 180, 255, 0.3)", // soft blue for active
            "&:hover": {
              backgroundColor: "rgba(100, 180, 255, 0.4)",
            },
          },
          "&[data-next]": {
            backgroundColor: "rgba(243, 112, 33, 0.5)", // soft orange for next
            color: "rgba(255, 255, 255, 1)",
            "&:hover": {
              backgroundColor: "rgba(243, 112, 33, 0.9)",
            },
          },
        }}
      >
        <CardContent>
          <Typography component={"div"} fontWeight={600}>
            {props.title}
          </Typography>
          <Typography color="text.secondary">
            {Intl.DateTimeFormat("fr-FR", {
              hour: "numeric",
              minute: "numeric",
            }).format(props.date)}
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
