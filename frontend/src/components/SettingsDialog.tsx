import { AudioFilePath, getAzanList, saveSetting } from "@/api/apiPrayer";
import { Settings } from "@/models/Settings";
import { CloseOutlined, VolumeDown, VolumeUp } from "@mui/icons-material";
import { Autocomplete, Button, Checkbox, Dialog, FormControl, FormControlLabel, IconButton, InputLabel, MenuItem, Select, SelectChangeEvent, Slider, TextField, Typography } from "@mui/material";
import { Box, Grid, Stack } from "@mui/system";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useMutation, useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { ChangeEvent, useEffect, useState } from "react";


export function SettingsDialog({ isOpen, onClose, settings }: Readonly<{ isOpen: boolean, onClose: () => void, settings: Settings }>) {

    const { data, error, isLoading } = useQuery({
        queryKey: ["azanList"],
        queryFn: getAzanList,
    });



    const [method, setMethod] = useState(settings.api.selectedMethod);
    const [volume, setVolume] = useState(settings.device.volume);
    const [audioFilePath, setAudioFilePath] = useState<AudioFilePath>();

    useEffect(() => {
        if (data && !isLoading && !error)
            setAudioFilePath(data.find((azan) => azan.description === settings.playlist.fileName));
    }, [settings.playlist.fileName, data, isLoading, error]);

    const mutateSettings = useMutation({
        mutationFn: (settings: Settings) => saveSetting(settings),
        onSuccess: (data) => {
            console.log("Save settings success", data);
            onClose();
        }
    })


    const [enableScheduler, setEnableScheduler] = useState(settings.enableScheduler);
    const handleChange = (event: SelectChangeEvent) => {
        setMethod(parseInt(event.target.value));
    };
    const handleAzanChange = (event: SelectChangeEvent) => {
        if (data)
            setAudioFilePath(data?.find((azan) => azan.id === event.target.value));
    };
    const handleVolumeChange = (_: Event, newValue: number | number[]) => {
        setVolume(newValue as number);
    }
    const handleSchedulerChange = (event: ChangeEvent<HTMLInputElement>) => {
        setEnableScheduler(event.target.checked);
    }

    const handleSave = () => {
        console.log("Save settings", settings, audioFilePath);
        settings.api.selectedMethod = method;
        settings.device.volume = volume;
        settings.playlist.fileName = audioFilePath?.description ?? "";
        settings.enableScheduler = enableScheduler;
        mutateSettings.mutate(settings);
        onClose();
    }
    return (
        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="fr-FR">
            <Dialog open={isOpen} onClose={onClose} maxWidth="md" fullWidth >
                <Box sx={{ p: 2 }}>
                    <Grid container justifyContent="space-between" sx={{ p: 2 }}>
                        <Typography variant="h4">Settings</Typography>
                        <IconButton onClick={onClose}><CloseOutlined /></IconButton>
                    </Grid>
                    <Grid container justifyContent="left" sx={{ p: 2 }} spacing={2} direction="column">
                        <Autocomplete
                            disablePortal
                            value={settings.api.city}
                            freeSolo
                            options={[]}
                            sx={{ width: 300 }}
                            renderInput={(params) => <TextField {...params} label="Ville" />}
                        />
                        <Autocomplete
                            disablePortal
                            value={settings.api.country}
                            freeSolo
                            options={[]}
                            sx={{ width: 300 }}
                            renderInput={(params) => <TextField {...params} label="Pays" />}
                        />

                        <FormControl fullWidth>
                            <InputLabel id="demo-simple-select-label">Méthode de calcule</InputLabel>
                            <Select
                                labelId="demo-simple-select-label"
                                id="demo-simple-select"
                                value={`${method}`}
                                label="Méthode de calcule"
                                onChange={handleChange}
                            >
                                {settings.calculationMethods.map((method) =>
                                    <MenuItem key={method.id} value={method.id}>{method.description}</MenuItem>)}
                            </Select>
                        </FormControl>
                        <DatePicker defaultValue={dayjs(settings.api.forceDate)} label="Date" />
                        <Stack spacing={2} direction="row" sx={{ alignItems: 'center', mb: 1 }}>
                            <VolumeDown />
                            <Slider aria-label="Volume" value={volume} onChange={handleVolumeChange} valueLabelDisplay="auto" />
                            <VolumeUp />
                        </Stack>
                        <FormControlLabel control={<Checkbox checked={enableScheduler} onChange={handleSchedulerChange} />} label="Enable Call for prayer" />

                        <FormControl fullWidth>
                            <InputLabel id="demo-simple-select-label">Audio d'appel a la prière</InputLabel>
                            {<Select
                                labelId="demo-simple-select-label"
                                id="demo-simple-select"
                                value={`${audioFilePath?.id}`}
                                label="Méthode de calcule"
                                onChange={handleAzanChange}
                            >
                                {!isLoading && data && data.map((azan) =>
                                    <MenuItem key={azan.id} value={azan.id}>{azan.description}</MenuItem>)}
                            </Select>}
                        </FormControl>
                        <audio src={`/${audioFilePath?.description}`} controls>
                            <track kind="captions" />
                        </audio>

                        <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }} >
                            <Button variant="contained" color="primary" onClick={handleSave} >Enregistrer</Button>
                        </Box>
                    </Grid>
                </Box>
            </Dialog>
        </LocalizationProvider>
    )
}