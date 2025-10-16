import {
    getAzanList,
    getCitiesByName,
    getMethods,
    saveSetting,
} from "@/api/apiPrayer";
import { City } from "@/models/City";
import { AudioFile, Settings } from "@/models/Settings";
import {
    CloseOutlined,
    VolumeDown,
    VolumeUp,
} from "@mui/icons-material";
import LocationPinIcon from "@mui/icons-material/LocationOnOutlined";
import {
    Autocomplete,
    Button,
    Checkbox,
    Dialog,
    FormControl,
    FormControlLabel,
    IconButton,
    Input,
    InputAdornment,
    InputLabel,
    MenuItem,
    Select,
    Slider,
    TextField,
    Typography,
} from "@mui/material";
import { Box, Grid, Stack } from "@mui/system";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useMutation, useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import "dayjs/locale/fr";
import { ChangeEvent, SyntheticEvent, useEffect, useState } from "react";
type AutocompleteValue = string | City | null;
export function SettingsDialog({
    isOpen,
    onClose,
    settings,
}: Readonly<{ isOpen: boolean; onClose: () => void; settings: Settings }>) {
    const { data: methods } = useQuery({
        queryKey: ["methods"],
        queryFn: getMethods,
    });

    const { data: azanList } = useQuery({
        queryKey: ["azanList"],
        queryFn: getAzanList,
    });

    const citiesMutation = useMutation({
        mutationFn: ({ name }: { name: string }) => getCitiesByName(name),
    });

    const [method, setMethod] = useState<string>(settings.selected_method);
    const [volume, setVolume] = useState<number>(settings.volume);
    const [audioFile, setAudioFile] = useState<AudioFile | null>(settings.audio ?? null);
    const [enableScheduler, setEnableScheduler] = useState(settings.enable_scheduler);
    const [cityName, setCityName] = useState(settings.city?.name ?? "");
    const [selectedCity, setSelectedCity] = useState<City | null>(settings.city ?? null);

    useEffect(() => {
        if (settings?.audio) setAudioFile(settings.audio);
    }, [settings]);

    const mutateSettings = useMutation({
        mutationFn: (s: Settings) => saveSetting(s),
        onSuccess: () => onClose(),
    });

    const handleMethodChange = (event: { target: { value: string } }) => setMethod(event.target.value);
    const handleAzanChange = (event: { target: { value: number } }) => {
        const selectedId = event.target.value;
        const azan = azanList?.find((a) => a.id === selectedId);
        setAudioFile(azan ?? null);
    };
    const handleVolumeChange = (_: Event, newValue: number | number[]) => setVolume(newValue as number);
    const handleSchedulerChange = (event: ChangeEvent<HTMLInputElement>) => setEnableScheduler(event.target.checked);
    const handleSearchCity = (name: string) => citiesMutation.mutate({ name });

    const handleSave = () => {
        const updatedSettings: Settings = {
            ...settings,
            selected_method: method,
            volume,
            audio_id: audioFile?.id ?? settings.audio_id,
            enable_scheduler: enableScheduler,
            city_id: selectedCity?.id ?? settings.city_id,
        };
        mutateSettings.mutate(updatedSettings);
    };

    return (
        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="fr-FR">
            <Dialog open={isOpen} onClose={onClose} maxWidth="md" fullWidth>
                <Box sx={{ p: 2 }}>
                    <Grid container justifyContent="space-between" sx={{ p: 2 }}>
                        <Typography variant="h4">Paramètres</Typography>
                        <IconButton onClick={onClose}>
                            <CloseOutlined />
                        </IconButton>
                    </Grid>

                    <Grid container direction="column" spacing={2} sx={{ p: 2 }}>
                        <Autocomplete
                            freeSolo
                            value={selectedCity}
                            inputValue={cityName}
                            onChange={(_: SyntheticEvent<Element, Event>, newValue: AutocompleteValue) => {
                                setSelectedCity(newValue as City | null);
                                setCityName((newValue as City)?.name ?? "");
                            }}
                            onInputChange={(_, newInputValue) => {
                                setCityName(newInputValue);
                                if (newInputValue.length > 2) handleSearchCity(newInputValue);
                            }}
                            options={citiesMutation.data ?? []}
                            getOptionLabel={(city) => `${(city as City).name}, ${(city as City).country}`}
                            isOptionEqualToValue={(option, value) => (option as City).id === (value as City).id}
                            renderInput={(params) => <TextField {...params} label="Ville" variant="outlined" />}
                            sx={{ width: 300 }}
                        />

                        <FormControl fullWidth sx={{ m: 1 }} variant="standard">
                            <InputLabel>Coordonnées</InputLabel>
                            <Input
                                startAdornment={
                                    <InputAdornment position="start">
                                        <LocationPinIcon />
                                    </InputAdornment>
                                }
                                value={`${selectedCity?.lat ?? ""}, ${selectedCity?.lon ?? ""}`}
                                readOnly
                            />
                        </FormControl>

                        {methods && (
                            <FormControl fullWidth>
                                <InputLabel>Méthode de calcul</InputLabel>
                                <Select value={method} onChange={(event) => { handleMethodChange(event); }}>
                                    {methods.map((m: { method: string; description: string }) => (
                                        <MenuItem key={m.method} value={m.method}>
                                            {m.description}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        )}

                        <DatePicker defaultValue={dayjs(settings.force_date)} label="Date" />

                        <Stack spacing={2} direction="row" sx={{ alignItems: "center", mb: 1 }}>
                            <VolumeDown />
                            <Slider value={volume} onChange={handleVolumeChange} valueLabelDisplay="auto" />
                            <VolumeUp />
                        </Stack>

                        <FormControlLabel
                            control={<Checkbox checked={enableScheduler} onChange={handleSchedulerChange} />}
                            label="Activer l'appel à la prière"
                        />

                        {azanList && (
                            <FormControl fullWidth>
                                <InputLabel>Audio d'appel à la prière</InputLabel>
                                <Select value={audioFile?.id} onChange={(event) => { handleAzanChange(event); }}>
                                    {azanList.map((azan: AudioFile) => (
                                        <MenuItem key={azan.id} value={azan.id}>
                                            {azan.name}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        )}

                        {audioFile && (
                            <audio src={`data:audio/mpeg;base64,${audioFile.blob?.toString()}`} controls>
                                <track kind="captions" />
                            </audio>
                        )}

                        <Box sx={{ p: 2, display: "flex", justifyContent: "flex-end" }}>
                            <Button variant="contained" onClick={handleSave} disabled={mutateSettings.isPending}>
                                {mutateSettings.isPending ? "Enregistrement..." : "Enregistrer"}
                            </Button>
                        </Box>
                    </Grid>
                </Box>
            </Dialog>
        </LocalizationProvider>
    );
}
