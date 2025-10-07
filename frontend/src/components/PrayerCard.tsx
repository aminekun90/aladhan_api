import { Card, CardActionArea, CardContent, Typography } from "@mui/material";


export function PrayerCard(props: {
  readonly selectedCard?: string;
  readonly id: string;
  readonly title: string;
  readonly date: Date;
  readonly setSelectedCard: (id: string) => void
  readonly isNext?: boolean;
}) {
  return (<Card sx={{ width: "100%" }}>
    <CardActionArea
      key={props.id}
      onClick={() => props.setSelectedCard(props.id)}
      data-active={props.selectedCard === props.id ? '' : undefined}
      data-next={props.isNext ? '' : undefined}
      sx={{
        height: '100%',
        '&[data-active]': {
          backgroundColor: 'action.selected',
          '&:hover': {
            backgroundColor: 'action.selectedHover',
          },
        },
        '&[data-next]': {
          backgroundColor: '#F37021',
        },
      }}
    >
      <CardContent>
        <Typography component={"div"}>{props.title}</Typography>
        <Typography color="text.secondary">{Intl.DateTimeFormat(
          'fr-FR', {
          hour: 'numeric',
          minute: 'numeric',
        }
        ).format(props.date)}</Typography>
      </CardContent>
    </CardActionArea>
  </Card>);
}