import { allTimings } from '@/api/apiPrayer';
import { DialogPdfGrid } from '@/components/DialogPdfGrid';
import { Timing } from '@/models/Timing';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import { Box, Card, Chip, IconButton, Stack, Typography } from "@mui/material";
import { Grid } from '@mui/system';
import { DateCalendar, DayCalendarSkeleton, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { useQuery } from '@tanstack/react-query';
import dayjs, { Dayjs } from 'dayjs';
import "dayjs/locale/fr";
import { useEffect, useState } from "react";
type TimingKey = "Imsak" | "Fajr" | "Dhuhr" | "Asr" | "Maghrib" | "Isha";


export function DateCalendarComponent({ coord }: Readonly<{ coord: { lat?: number, lon?: number } }>) {
    const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
    const [eventsForSelectedDay, setEventsForSelectedDay] = useState<Timing[]>([]);
    const [openPdfModal, setOpenPdfModal] = useState<boolean>(false);
    // Fetch events for the current month
    const { data: events, isLoading, isError } = useQuery({
        queryKey: ["events", selectedDate.month() + 1, selectedDate.year(), coord],
        queryFn: () => allTimings(selectedDate.month() + 1, selectedDate.year(), coord),
    });

    // Filter events whenever selectedDate or events change
    useEffect(() => {
        if (!events) return;
        // Extract Gregorian date as string
        const formattedDate = selectedDate.format("DD-MM-YYYY");

        const filteredEvents = events.filter((event: Timing) => {

            const eventDate = dayjs(new Date(event.date)).format("DD-MM-YYYY");

            return eventDate === formattedDate;
        });
        setEventsForSelectedDay(filteredEvents);
    }, [selectedDate, events]);

    // Function to update selected date
    const handleDayClick = (date: Dayjs) => {
        setSelectedDate(date);
    };

    return (
        <Grid container sx={{ flexGrow: 1, justifyContent: "center", padding: 2 }}>
            <Card sx={{ padding: 2, minWidth: 300 }}>
                {/* Header */}
                <Grid justifyContent="flex-end" sx={{ display: "flex", alignItems: "center", height: 60 }} >
                    <IconButton sx={{ color: "white", height: 60, width: 60 }} onClick={() => setOpenPdfModal(true)}>
                        <PictureAsPdfIcon />
                    </IconButton>
                </Grid>

                {/* Date Picker */}
                <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="fr-FR">
                    <DateCalendar
                        loading={isLoading}
                        onChange={handleDayClick} // Handle day click
                        renderLoading={() => <DayCalendarSkeleton />}
                    />
                </LocalizationProvider>

                {/* Selected Day Events */}
                <Box sx={{ marginTop: 2, textAlign: "center" }}>
                    <Typography variant="h6">Les prières du {selectedDate.format("DD/MM/YYYY")}</Typography>
                    {
                        eventsForSelectedDay.length > 0 ? (
                            eventsForSelectedDay.map((event: Timing, index) => {
                                return <Stack direction="column" spacing={1} key={`${event.date}-${index}`}>
                                    <Typography dir="rtl" key={event.hijri_date}>{event.hijri_date}</Typography>

                                    {(["Imsak", "Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"] as TimingKey[]).map((key) => (
                                        <Chip key={`${index}-${key}`} label={`${key}: ${event.times[key]}`} />
                                    ))}
                                </Stack>;
                            }
                            ))
                            : (
                                <Typography>Aucune prière trouvée.</Typography>
                            )}

                    {isError && <Typography>Erreur lors de la récupération des prières</Typography>}
                </Box>
            </Card>
            {events && <DialogPdfGrid events={events} openDialog={openPdfModal} onClose={() => setOpenPdfModal(false)} title={selectedDate.format("MMMM YYYY")} />
            }
        </Grid>

    );
}
