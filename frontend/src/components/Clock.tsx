import { Typography } from "@mui/material";
import { Variant } from "@mui/material/styles/createTypography";
import { useState } from "react";

export function DateClock(props: { readonly variation: Variant }) {
    const [currentTime, setCurrentTime] = useState(new Date());

    setInterval(() => {
        setCurrentTime(new Date());
    }, 1000);
    return <Typography variant={props.variation} sx={{ textAlign: 'center', textTransform: 'capitalize' }}>
        {
            Intl.DateTimeFormat('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
            }).format(currentTime)
        } - {
            Intl.DateTimeFormat('fr-FR', {
                hour: 'numeric',
                minute: 'numeric',
                second: 'numeric',
            }).format(currentTime)
        }</Typography>;
}