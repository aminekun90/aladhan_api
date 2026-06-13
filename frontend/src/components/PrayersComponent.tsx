import { Typography } from '@mui/material';
import { Grid } from '@mui/system';
import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { getPrayers } from '../api/apiPrayer';
import { PrayerCard } from './PrayerCard';

export function PrayersComponent({ updateDate, coord }: Readonly<{ updateDate: (date: string) => void, coord: { lat?: number, lon?: number } }>) {
    const { data, error, isLoading } = useQuery({
        queryKey: ["prayers"],
        queryFn: () => getPrayers(coord),
    });
    useEffect(() => {
        if (data) {
            updateDate(data.hijri_date);
        }
    }, [data, updateDate]);
    return (
        <Grid container spacing={{ xs: 1.5, sm: 2, md: 3 }} sx={{ flexGrow: 1, justifyContent: 'center', maxWidth: 1000, mx: 'auto' }}>
            {isLoading && <Typography sx={{ color: 'var(--mist)' }}>Loading…</Typography>}
            {error && <Typography sx={{ color: 'var(--mist)' }}>Error fetching prayers</Typography>}

            {!!data && data.prayers.map((prayer, id) => (
                <Grid size={{ xs: 6, sm: 4, md: 2 }} key={prayer.getName()}>
                    <PrayerCard timezone={prayer.getTimeZone()} id={id?.toString()} title={prayer?.getName()} date={prayer?.getTime()} setSelectedCard={() => { }} isNext={data.prayers.find((inner) => inner.getTime().getTime() >= new Date().getTime()) === prayer} />
                </Grid>
            ))}
        </Grid>
    )
}