import { PrayerColumn, PrayerRow } from '@/models/prayer';
import { DataGrid, GridToolbarContainer, GridToolbarExport } from '@mui/x-data-grid';
function CustomToolbar() {
    return (
        <GridToolbarContainer>
            <GridToolbarExport />
        </GridToolbarContainer>
    );
}
export default function PrayersDataGrid({ data, loading }: Readonly<{ data: { rows: PrayerRow[], columns: PrayerColumn[] }, loading: boolean }>) {
    return (
        <DataGrid {...data} loading={loading} slots={{
            toolbar: CustomToolbar,
        }} />
    )
}