import { allTimings } from "@/api/apiPrayer";
import { logger } from "@/utils/logger";
import { DialogPdfGrid } from "@/components/DialogPdfGrid";
import { Timing } from "@/models/Timing";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import {
    Box,
    capitalize,
    Card,
    Chip,
    Grid,
    IconButton,
    Stack,
    Tooltip,
    Typography,
    useTheme,
} from "@mui/material";

import {
    DateCalendar,
    DayCalendarSkeleton,
    LocalizationProvider,
} from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useQuery } from "@tanstack/react-query";
import dayjs, { Dayjs } from "dayjs";
import "dayjs/locale/fr";
import { useMemo, useState } from "react";

type TimingKey = "Imsak" | "Fajr" | "Dhuhr" | "Asr" | "Maghrib" | "Isha";

export function DateCalendarComponent({
  coord,
}: Readonly<{ coord: { lat?: number; lon?: number } }>) {
  const theme = useTheme();
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [openPdfModal, setOpenPdfModal] = useState<boolean>(false);

  // Fetch events for the current month
  const {
    data: events,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["events", selectedDate.month() + 1, selectedDate.year(), coord],
    queryFn: () =>
      allTimings(selectedDate.month() + 1, selectedDate.year(), coord),
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
      dayjs(event.date).isSame(selectedDate, "day"),
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
      const firstParts = firstEvent.hijri_date.split(" ");
      // Slices from index 2 to the end: ["جمادى", "الأولى", "1447"]
      // Joins to: "جمادى الأولى "
      const firstPart = firstParts.slice(2, -1).join(" ");
      // Slices from the end: ["1447"]
      const year = firstParts.at(-1);

      // Parse the last event's date
      // e.g., "الثلاثاء 4 جمادى الاخرة 1447"
      const lastParts = lastEvent.hijri_date.split(" ");
      // Slices from index 2 up to (but not including) the last part: ["جمادى", "الاخرة"]
      // Joins to: "جمادى الاخرة"
      const lastPart = lastParts.slice(2, -1).join(" ");

      if (firstPart && lastPart) {
        // Creates the final string: " 1447 جمادى الأولى-جمادى الاخرة"
        // if first part and last part are equal return " 1447 جمادى الأولى"
        if (firstPart === lastPart) return ` ${year} ${firstPart}`;
        return ` ${firstPart}-${lastPart} ${year}`;
      }

      return ""; // Fallback for safety
    } catch (error) {
      logger.error("Failed to parse Hijri date:", error);
      return ""; // Return an empty string on error
    }
  }, [events]);

  // --- END OF useMemo SOLUTION ---

  const handleDayClick = (value: Dayjs | null) => {
    if (value) setSelectedDate(value);
  };

  return (
    <Grid container sx={{ flexGrow: 1, justifyContent: "center", px: { xs: 0, sm: 2 } }}>
      <Card
        sx={{
          p: { xs: 1.5, sm: 2 },
          width: "100%",
          maxWidth: 420,
          borderRadius: "1.5rem",
          background: "var(--surface)",
          backdropFilter: "blur(10px)",
          border: "1px solid var(--line)",
          transition: "border-color .25s ease, box-shadow .25s ease",
          "&:hover": {
            borderColor: "rgba(212,173,95,0.35)",
            boxShadow: "0 14px 44px rgba(212,173,95,0.12)",
          },
        }}
      >
        <Grid
          container
          component="div"
          justifyContent="flex-end"
          sx={{ display: "flex", alignItems: "center" }}
        >
          <Tooltip title="Exporter en PDF">
            <IconButton onClick={() => setOpenPdfModal(true)}>
              <PictureAsPdfIcon />
            </IconButton>
          </Tooltip>
        </Grid>

        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="fr-FR">
          <DateCalendar
            loading={isLoading}
            onChange={handleDayClick}
            renderLoading={() => <DayCalendarSkeleton />}
          />
        </LocalizationProvider>

        <Box sx={{ marginTop: 2, textAlign: "center" }}>
          <Typography variant="h6">
            Les prières du {selectedDate.format("DD/MM/YYYY")}
          </Typography>
          {eventsForSelectedDay.length > 0 ? (
            eventsForSelectedDay.map((event: Timing, index) => (
              <Stack spacing={1.5} key={`${event.date}-${index}`} sx={{ mt: 1 }}>
                <Typography dir="rtl" sx={{ fontFamily: "var(--font-arabic)", fontSize: "1.1rem", color: "var(--brass-bright)" }}>
                  {event.hijri_date}
                </Typography>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, justifyContent: "center" }}>
                  {(
                    [
                      "Imsak",
                      "Fajr",
                      "Dhuhr",
                      "Asr",
                      "Maghrib",
                      "Isha",
                    ] as TimingKey[]
                  ).map((key) => (
                    <Chip
                      key={`${index}-${key}`}
                      size="small"
                      label={`${key} ${event.times[key]}`}
                      sx={{
                        backgroundColor: "rgba(212,173,95,0.1)",
                        border: "1px solid var(--line)",
                        color: theme.palette.text.primary,
                        fontWeight: 500,
                        fontFamily: "var(--font-ui)",
                      }}
                    />
                  ))}
                </Box>
              </Stack>
            ))
          ) : (
            <Typography>Aucune prière trouvée.</Typography>
          )}
          {isError && (
            <Typography>Erreur lors de la récupération des prières</Typography>
          )}
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
