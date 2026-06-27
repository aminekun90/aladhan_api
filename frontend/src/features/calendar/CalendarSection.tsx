import { SectionHeading } from "@/components/SectionHeading";
import { DateCalendarComponent } from "@/features/calendar/components/Calendar";
import { Box } from "@mui/material";
import { useTranslation } from "react-i18next";

export function CalendarSection({
    coord,
    locationLabel,
}: Readonly<{ coord: { lat?: number; lon?: number }; locationLabel?: string }>) {
    const { t } = useTranslation();
    return (
        <Box component="section">
            <SectionHeading>{t("sections.calendar")}</SectionHeading>
            <DateCalendarComponent coord={coord} locationLabel={locationLabel} />
        </Box>
    );
}
