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
    SelectChangeEvent,
    Slider,
    TextField,
    Typography,
} from "@mui/material";
import { Box, Grid, Stack } from "@mui/system";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useMutation, useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import "dayjs/locale/fr"; // ✅ Needed if you use adapterLocale="fr-FR"
import { ChangeEvent, useEffect, useState } from "react";

export function SettingsDialog({
    isOpen,
    onClose,
    settings,
}: Readonly<{ isOpen: boolean; onClose: () => void; settings: Settings }>) {
    // ─── Queries ─────────────────────────────────────────────
    const { data: methods, error: methodError, isLoading: methodLoading } =
        useQuery({
            queryKey: ["methods"],
            queryFn: getMethods,
        });

    const { data: azanList, error, isLoading } = useQuery({
        queryKey: ["azanList"],
        queryFn: getAzanList,
    });

    // ─── Mutation for city search ─────────────────────────────
    const citiesMutation = useMutation({
        mutationFn: ({ name, country }: { name: string; country?: string }) =>
            getCitiesByName(name, country),
    });

    // ─── Local state ──────────────────────────────────────────
    const [method, setMethod] = useState<string>(settings.selected_method);
    const [volume, setVolume] = useState<number>(settings.volume);
    const [audioFile, setAudioFile] = useState<AudioFile | null>(null);
    const [enableScheduler, setEnableScheduler] = useState(
        settings.enable_scheduler
    );
    const [cityName, setCityName] = useState(settings.city?.name ?? "");
    const [countryName, setCountryName] = useState(settings.city?.country ?? "");

    useEffect(() => {
        if (settings?.audio) {
            setAudioFile(settings.audio);
        }
        console.log("Selected settings", settings)
    }, [settings]);

    // ─── Save settings mutation ───────────────────────────────
    const mutateSettings = useMutation({
        mutationFn: (s: Settings) => saveSetting(s),
        onSuccess: (data) => {
            console.log("✅ Settings saved successfully:", data);
            onClose();
        },
    });

    // ─── Handlers ─────────────────────────────────────────────
    const handleMethodChange = (event: SelectChangeEvent) => {
        setMethod(event.target.value);
    };

    const handleAzanChange = (event: SelectChangeEvent<number>) => {
        const selectedId = event.target.value;
        const selectedAzan = azanList?.find((a) => a.id === selectedId);
        setAudioFile(selectedAzan ?? null);
    };

    const handleVolumeChange = (_: Event, newValue: number | number[]) => {
        setVolume(newValue as number);
    };

    const handleSchedulerChange = (event: ChangeEvent<HTMLInputElement>) => {
        setEnableScheduler(event.target.checked);
    };

    const handleSave = () => {
        const updatedSettings: Settings = {
            ...settings,
            selected_method: method,
            volume,
            device_id: settings.device_id,
            audio_id: audioFile?.id ?? settings.audio_id,
            enable_scheduler: enableScheduler,
            force_date: null,
        };
        mutateSettings.mutate(updatedSettings);
    };

    const handleSearchCity = (name: string, country?: string) => {
        citiesMutation.mutate({ name, country });
    };

    // ─── Render ───────────────────────────────────────────────
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

                    <Grid
                        container
                        justifyContent="left"
                        sx={{ p: 2 }}
                        spacing={2}
                        direction="column"
                    >
                        {/* City Autocomplete */}
                        <Autocomplete
                            disablePortal
                            freeSolo
                            value={cityName}
                            onChange={(_, newValue) => setCityName(newValue ?? "")}
                            onInputChange={(_, newInputValue) => {
                                setCityName(newInputValue);
                                if (newInputValue.length > 2) handleSearchCity(newInputValue, countryName ?? "");
                            }}
                            options={
                                citiesMutation.data
                                    ? citiesMutation.data.map((city: City) => city.name)
                                    : []
                            }
                            sx={{ width: 300 }}
                            renderInput={(params) => (
                                <TextField {...params} label="Ville" variant="outlined" />
                            )}
                        />

                        <FormControl fullWidth sx={{ m: 1 }} variant="standard">
                            <InputLabel htmlFor="standard-adornment-coordinates">
                                Coordonnées
                            </InputLabel>
                            <Input
                                id="standard-adornment-coordinates"
                                startAdornment={
                                    <InputAdornment position="start">
                                        <LocationPinIcon />
                                    </InputAdornment>
                                }
                                value={`${settings.city?.lat ?? ""}, ${settings.city?.lon ?? ""}`}
                                readOnly
                            />
                        </FormControl>

                        <Autocomplete
                            disablePortal
                            freeSolo
                            value={countryName}
                            onChange={(_, newValue) => {
                                handleSearchCity(cityName, newValue ?? "");
                                setCountryName(newValue ?? "")

                            }}
                            options={[]} // You could populate this from API if available
                            sx={{ width: 300 }}
                            renderInput={(params) => (
                                <TextField {...params} label="Pays" variant="outlined" />
                            )}
                        />

                        {/* Method select */}
                        {!methodLoading && !methodError && (
                            <FormControl fullWidth>
                                <InputLabel id="method-select-label">
                                    Méthode de calcul
                                </InputLabel>
                                <Select
                                    labelId="method-select-label"
                                    id="method-select"
                                    value={method}
                                    label="Méthode de calcul"
                                    onChange={handleMethodChange}

                                >

                                    {methods?.map((m: { method: string, description: string }) => {
                                        //console.log(m.method, settings.selected_method)
                                        return <MenuItem key={m.method} value={m.method} selected={m.method === settings.selected_method}>
                                            {m.description}
                                        </MenuItem>
                                    }


                                    )}
                                </Select>
                            </FormControl>
                        )}

                        <DatePicker
                            defaultValue={dayjs(settings.force_date)}
                            label="Date"
                        />

                        {/* Volume control */}
                        <Stack
                            spacing={2}
                            direction="row"
                            sx={{ alignItems: "center", mb: 1 }}
                        >
                            <VolumeDown />
                            <Slider
                                aria-label="Volume"
                                value={volume}
                                onChange={handleVolumeChange}
                                valueLabelDisplay="auto"
                            />
                            <VolumeUp />
                        </Stack>

                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={enableScheduler}
                                    onChange={handleSchedulerChange}
                                />
                            }
                            label="Activer l'appel à la prière"
                        />

                        {/* Audio selection */}
                        {azanList && azanList.length > 0 && (
                            <FormControl fullWidth>
                                <InputLabel id="audio-select-label">
                                    Audio d'appel à la prière
                                </InputLabel>
                                <Select
                                    labelId="audio-select-label"
                                    id="audio-select"
                                    value={audioFile?.id ?? ""}
                                    label="Audio d'appel à la prière"
                                    onChange={handleAzanChange}
                                >
                                    {!isLoading &&
                                        !error &&
                                        azanList?.map((azan: AudioFile) => (
                                            <MenuItem key={azan.id} value={azan.id}>
                                                {azan.name}
                                            </MenuItem>
                                        ))}
                                </Select>
                            </FormControl>
                        )}

                        {/* Audio preview */}
                        {audioFile && (
                            <audio
                                src={`data:audio/mpeg;base64,${audioFile?.blob?.toString()}`}
                                controls
                            >
                                <track kind="captions" />
                            </audio>
                        )}

                        <Box sx={{ p: 2, display: "flex", justifyContent: "flex-end" }}>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={handleSave}
                                disabled={mutateSettings.isPending}
                            >
                                {mutateSettings.isPending ? "Enregistrement..." : "Enregistrer"}
                            </Button>
                        </Box>
                    </Grid>
                </Box>
            </Dialog>
        </LocalizationProvider>
    );
}
