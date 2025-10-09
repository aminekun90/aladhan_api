import PrayersDataGrid from "@/components/prayersDataGrid";
import { PrayerRow } from "@/models/prayer";
import { Timing } from "@/models/Timing";
import { Dialog } from "@mui/material";
import { useEffect } from "react";

export function DialogPdfGrid({ openDialog, onClose, events, title }: Readonly<{ openDialog: boolean, onClose: () => void, events: Timing[], title: string }>) {
    const rows: PrayerRow[] = events.map((event, index) => {

        return {
            id: index + 1,
            date: Intl.DateTimeFormat('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
            }).format(new Date(event.date).getTime()),
            hijri: event.hijri_date,
            imsak: event.times.Imsak,
            fajr: event.times.Fajr,
            dhuhr: event.times.Dhuhr,
            asr: event.times.Asr,
            maghrib: event.times.Maghrib,
            isha: event.times.Isha,
        }
    });
    const data = {
        rows,
        columns: [
            { field: 'date', headerName: 'Gregorian Date', flex: 1, },
            { field: 'hijri', headerName: 'Hijri Date', flex: 1 },
            { field: 'imsak', headerName: 'Imsak', flex: 1 },
            { field: 'fajr', headerName: 'Fajr', flex: 1 },
            { field: 'dhuhr', headerName: 'Dhuhr', flex: 1 },
            { field: 'asr', headerName: 'Asr', flex: 1 },
            { field: 'maghrib', headerName: 'Maghrib', flex: 1 },
            { field: 'isha', headerName: 'Isha', flex: 1 },

        ]
    }
    const loading = false;
    useEffect(() => {

        document.title = openDialog ? title : "Prayer Player"

    }, [openDialog, title]);
    return (
        <Dialog open={openDialog} onClose={onClose} maxWidth="xl" fullWidth>
            <PrayersDataGrid data={data} loading={loading} />
        </Dialog>
    )
}