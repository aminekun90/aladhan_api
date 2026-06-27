import { SectionHeading } from "@/components/SectionHeading";
import { PrayersComponent } from "@/features/prayers/components/PrayersComponent";
import { Box } from "@mui/material";
import { useTranslation } from "react-i18next";

export function PrayersSection({
    coord,
    updateDate,
}: Readonly<{ coord: { lat?: number; lon?: number }; updateDate: (date: string) => void }>) {
    const { t } = useTranslation();
    return (
        <Box component="section">
            <SectionHeading>{t("sections.prayerTimes")}</SectionHeading>
            <PrayersComponent coord={coord} updateDate={updateDate} />
        </Box>
    );
}
