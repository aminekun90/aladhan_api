import { Typography } from "@mui/material";
import { useEffect, useState } from "react";

export function DateClock(props: Readonly<{ variation: "h1" | "h2" | "h3" | "h4" | "h5" | "h6" }>) {
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    return (
        <Typography variant={props.variation} sx={{ textAlign: 'center', textTransform: 'capitalize' }}>
            {Intl.DateTimeFormat('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).format(currentTime)} -
            {Intl.DateTimeFormat('fr-FR', { hour: 'numeric', minute: 'numeric', second: 'numeric' }).format(currentTime)}
        </Typography>
    );
}
