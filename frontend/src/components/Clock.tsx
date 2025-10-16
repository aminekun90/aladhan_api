import { Typography } from "@mui/material";

import { useState } from "react";

export function DateClock(props: Readonly<{ variation: "h4" | "h5" | "h6" | "h3" | "h2" | "h1" }>) {
    const [currentTime, setCurrentTime] = useState(new Date());

    const interval = setInterval(() => {
        setCurrentTime(new Date());

    }, 1000);
    clearInterval(interval);
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