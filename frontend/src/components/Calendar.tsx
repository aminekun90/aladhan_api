import { allTimings } from "@/api/apiPrayer";
import { DialogPdfGrid } from "@/components/DialogPdfGrid";
import { Timing } from "@/models/Timing";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import { Box, capitalize, Card, Chip, IconButton, Stack, Typography, useTheme } from "@mui/material";
import { Grid } from "@mui/system";
import { DateCalendar, DayCalendarSkeleton, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useQuery } from "@tanstack/react-query";
import dayjs, { Dayjs } from "dayjs";
import "dayjs/locale/fr";
import { useMemo, useState } from "react";


type TimingKey = "Imsak" | "Fajr" | "Dhuhr" | "Asr" | "Maghrib" | "Isha";

export function DateCalendarComponent({ coord }: Readonly<{ coord: { lat?: number, lon?: number } }>) {
    const theme = useTheme();
    const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
    const [openPdfModal, setOpenPdfModal] = useState<boolean>(false);

    // Fetch events for the current month
    const { data: events, isLoading, isError } = useQuery({
        queryKey: ["events", selectedDate.month() + 1, selectedDate.year(), coord],
        queryFn: () => allTimings(selectedDate.month() + 1, selectedDate.year(), coord),
    });

    // --- REMOVED THE ENTIRE useEffect BLOCK ---

    // --- SOLUTION: Calculate derived state with useMemo ---

    /**
     * 1. Calculate the events for the selected day.
     * This will *only* re-run when "events" or 'selectedDate' changes.
     */
    const eventsForSelectedDay = useMemo(() => {
        if (!events || events.length === 0) {
            return [];
        }

        // Use dayjs.isSame() for a robust and fast comparison
        return events.filter((event: Timing) =>
            dayjs(event.date).isSame(selectedDate, 'day')
        );
    }, [events, selectedDate]);

    /**
     * 2. Calculate the Hijri month/year range string.
     * This will *only* re-run when 'events' changes.
     */
    const hijriMonthYear = useMemo(() => {
        if (!events || events.length === 0) {
            return "";
        }

        try {
            const firstEvent = events[0];
            const lastEvent = events.at(-1);

            if (!firstEvent || !lastEvent) return "";

            // Parse the first event's date
            // e.g., "الإثنين 5 جمادى الأولى 1447"
            const firstParts = firstEvent.hijri_date.split(' ');
            // Slices from index 2 to the end: ["جمادى", "الأولى", "1447"]
            // Joins to: "جمادى الأولى "
            const firstPart = firstParts.slice(2, -1).join(' ');
            // Slices from the end: ["1447"]
            const year = firstParts.at(-1);

            // Parse the last event's date
            // e.g., "الثلاثاء 4 جمادى الاخرة 1447"
            const lastParts = lastEvent.hijri_date.split(' ');
            // Slices from index 2 up to (but not including) the last part: ["جمادى", "الاخرة"]
            // Joins to: "جمادى الاخرة"
            const lastPart = lastParts.slice(2, -1).join(' ');

            if (firstPart && lastPart) {
                // Creates the final string: " 1447 جمادى الأولى-جمادى الاخرة"
                // if first part and last part are equal return " 1447 جمادى الأولى"
                if (firstPart === lastPart) return ` ${year} ${firstPart}`;
                return ` ${firstPart}-${lastPart} ${year}`;
            }

            return ""; // Fallback for safety
        } catch (error) {
            console.error("Failed to parse Hijri date:", error);
            return ""; // Return an empty string on error
        }
    }, [events]);

    // --- END OF useMemo SOLUTION ---


    const handleDayClick = (date: Dayjs) => setSelectedDate(date);

    return (
        <Grid container sx={{ flexGrow: 1, justifyContent: "center", padding: 2 }}>
            <Card
                sx={{
                    padding: 2,
                    minWidth: 300,
                    borderRadius: "1.5rem",
                    background: "rgba(255, 255, 255, 0.15)",
                    backdropFilter: "blur(2px) saturate(180%)",
                    border: "0.0625rem solid rgba(255, 255, 255, 0.4)",
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
                        background: "rgba(255, 255, 255, 0.1)",
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

                <Grid justifyContent="flex-end" sx={{ display: "flex", alignItems: "center", height: 60 }} >
                    <IconButton sx={{ color: "white", height: 60, width: 60 }} onClick={() => setOpenPdfModal(true)}>
                        <PictureAsPdfIcon />
                    </IconButton>
                </Grid>


                <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="fr-FR">
                    <DateCalendar
                        loading={isLoading}
                        onChange={handleDayClick}
                        renderLoading={() => <DayCalendarSkeleton />}
                    />
                </LocalizationProvider>


                <Box sx={{ marginTop: 2, textAlign: "center" }}>
                    <Typography variant="h6">Les prières du {selectedDate.format("DD/MM/YYYY")}</Typography>
                    {eventsForSelectedDay.length > 0 ? (
                        eventsForSelectedDay.map((event: Timing, index) => (
                            <Stack direction="column" spacing={1} key={`${event.date}-${index}`}>
                                <Typography dir="rtl" key={event.hijri_date}>{event.hijri_date}</Typography>
                                {(["Imsak", "Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"] as TimingKey[]).map((key) => (
                                    <Chip
                                        key={`${index}-${key}`}
                                        label={`${key}: ${event.times[key]}`}
                                        sx={{
                                            backgroundColor: "rgba(255,255,255,0.2)",
                                            backdropFilter: "blur(2px)",
                                            color: theme.palette.text.primary,
                                            fontWeight: 600,
                                        }}
                                    />
                                ))}
                            </Stack>
                        ))
                    ) : (
                        <Typography>Aucune prière trouvée.</Typography>
                    )}
                    {isError && <Typography>Erreur lors de la récupération des prières</Typography>}
                </Box>
            </Card>

            {events && (
                <DialogPdfGrid
                    events={events}
                    openDialog={openPdfModal}
                    onClose={() => setOpenPdfModal(false)}
                    // remove from hijri date the day and date keep year and month for example الإثنين 5 جمادى الأولى 1447
                    // becomes جمادى الأولى 1447
                    title={`${capitalize(selectedDate.format("MMMM YYYY"))} - ${hijriMonthYear}`}
                />
            )}
        </Grid>
    );
}
