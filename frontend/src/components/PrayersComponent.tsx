import { Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { getPrayers } from '../api/apiPrayer';
import { PrayerCard } from './PrayerCard';

export function PrayersComponent({ updateDate }: Readonly<{ updateDate: (date: string) => void }>) {
    const { data, error, isLoading } = useQuery({
        queryKey: ["prayers"],
        queryFn: getPrayers,
    });
    useEffect(() => {
        if (data) {
            updateDate(data.hijri_date);
        }
    }, [data, updateDate]);
    return (
        <Grid container spacing={3} sx={{ flexGrow: 1, justifyContent: 'center' }}>
            {isLoading && <Typography>Loading...</Typography>}
            {error && <Typography>Error fetching prayers</Typography>}
            {!!data && data.prayers.map((prayer, id) => (
                <Grid size={{ xs: 6, md: 2 }} key={prayer.getName()}>
                    <PrayerCard id={id?.toString()} title={prayer?.getName()} date={prayer?.getTime()} setSelectedCard={() => { }} isNext={data.prayers.find((inner) => inner.getTime().getTime() >= new Date().getTime()) === prayer} />
                </Grid>
            ))}
        </Grid>
    )
}