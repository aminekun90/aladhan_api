import {
    deleteAudio,
    getAzanList,
    getCitiesByName,
    getMethods,
    saveSetting,
    uploadAudio,
} from "@/api/apiPrayer";
import { logger } from "@/utils/logger";
import { City } from "@/models/City";
import { AudioFile, Settings } from "@/models/Settings";
import { useToast } from "@aminekun90/react-toast";
import {
    CloseOutlined,
    DeleteOutline,
    UploadFile,
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
    Tooltip,
    Typography,
} from "@mui/material";
import { Box, Grid, Stack } from "@mui/system";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import "dayjs/locale/fr";
import { ChangeEvent, SyntheticEvent, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
type AutocompleteValue = string | City | null;
export function SettingsDialog({
    isOpen,
    onClose,
    settings,
}: Readonly<{ isOpen: boolean; onClose: () => void; settings: Settings }>) {
    const { t, i18n } = useTranslation();
    const { data: methods } = useQuery({
        queryKey: ["methods"],
        queryFn: getMethods,
    });

    const queryClient = useQueryClient();
    const fileInputRef = useRef<HTMLInputElement>(null);

    const { data: azanList } = useQuery({
        queryKey: ["azanList"],
        queryFn: getAzanList,
    });

    const citiesMutation = useMutation({
        mutationFn: ({ name, coutry }: { name: string; coutry?: string }) => getCitiesByName(name, coutry),
    });

    const uploadMutation = useMutation({
        mutationFn: (file: File) => uploadAudio(file),
        onSuccess: (uploaded) => {
            queryClient.invalidateQueries({ queryKey: ["azanList"] });
            if (uploaded) setAudioFile(uploaded);
            show({ type: 'success', title: t('toast.audioAdded.title'), message: uploaded?.name ?? '', position: 'top-right', duration: 3000 });
        },
        onError: (err) => logger.error("Audio upload failed:", err),
    });

    const deleteMutation = useMutation({
        mutationFn: (name: string) => deleteAudio(name),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["azanList"] }),
        onError: (err) => logger.error("Audio delete failed:", err),
    });

    const [method, setMethod] = useState<string>(settings.selected_method);
    const [volume, setVolume] = useState<number>(settings.volume);
    const [audioFile, setAudioFile] = useState<AudioFile | null>(settings.audio ?? null);
    const [enableScheduler, setEnableScheduler] = useState(settings.enable_scheduler);
    const [cityName, setCityName] = useState(settings.city?.name ?? "");
    const [selectedCity, setSelectedCity] = useState<City | null>(settings.city ?? null);
    const [forceDate, setForceDate] = useState<Date | undefined>(settings.force_date ?? undefined);
    const { show } = useToast();

    const mutateSettings = useMutation({
        mutationFn: (s: Settings) => saveSetting(s),
        onSuccess: () => {
            show({
                type: 'success',
                title: 'Settings Saved',
                message: 'Settings have been saved !',
                position: 'top-right',
                duration: 3000,
                progressBar: true
            })
            onClose();
        },
    });

    const handleMethodChange = (event: { target: { value: string } }) => setMethod(event.target.value);
    const handleAzanChange = (event: { target: { value: number } }) => {
        const selectedId = event.target.value;
        const azan = azanList?.find((a) => a.id === selectedId);
        setAudioFile(azan ?? null);
    };
    const handleVolumeChange = (_: Event, newValue: number | number[]) => setVolume(newValue as number);
    const handleSchedulerChange = (event: ChangeEvent<HTMLInputElement>) => setEnableScheduler(event.target.checked);
    const handleSearchCity = (name: string, coutry?: string) => citiesMutation.mutate({ name, coutry });

    const handleSave = () => {
        const updatedSettings: Settings = {
            ...settings,
            selected_method: method,
            volume,
            audio_id: audioFile?.id ?? settings.audio_id,
            enable_scheduler: enableScheduler,
            city_id: selectedCity?.id ?? settings.city_id,
            force_date: forceDate,
        };
        mutateSettings.mutate(updatedSettings);
    };

    return (
        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale={i18n.resolvedLanguage}>
            <Dialog open={isOpen} onClose={onClose} maxWidth="md" fullWidth>
                <Box sx={{ p: 2 }}>
                    <Grid container justifyContent="space-between" sx={{ p: 2 }}>
                        <Typography variant="h4">{t('settings.title')}</Typography>
                        <IconButton onClick={onClose}>
                            <CloseOutlined />
                        </IconButton>
                    </Grid>

                    <Grid container direction="column" spacing={2} sx={{ p: 2 }}>
                        <Autocomplete
                            freeSolo
                            value={selectedCity}
                            disablePortal
                            inputValue={cityName}
                            onChange={(_: SyntheticEvent<Element, Event>, newValue: AutocompleteValue) => {
                                setSelectedCity(newValue as City | null);
                                setCityName((newValue as City)?.name ?? "");
                            }}
                            onInputChange={(_, newInputValue) => {
                                setCityName(newInputValue);
                                if (newInputValue.length > 2) {
                                    const name = newInputValue.split(",").shift()?.trim();
                                    const country = newInputValue.split(",").pop()?.trim();
                                    if (name) {
                                        handleSearchCity(name, country);
                                    }
                                }
                            }}
                            options={citiesMutation.data ?? []}
                            getOptionLabel={(city) => `${(city as City).name}, ${(city as City).country}`}
                            isOptionEqualToValue={(option, value) => (option as City).id === (value as City).id}
                            renderInput={(params) => <TextField {...params} label={t('settings.city')} variant="outlined" />}
                            sx={{ width: "100%", maxWidth: 360 }}
                        />

                        <FormControl fullWidth sx={{ m: 1 }} variant="standard">
                            <InputLabel>{t('settings.coordinates')}</InputLabel>
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
                                <InputLabel>{t('settings.method')}</InputLabel>
                                <Select value={method} onChange={(event) => { handleMethodChange(event); }}>
                                    {methods.map((m: { method: string; description: string }) => (
                                        <MenuItem key={m.method} value={m.method}>
                                            {m.description}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        )}

                        <DatePicker defaultValue={dayjs(settings.force_date)} label={t('settings.date')} onChange={(newValue) => { setForceDate(newValue?.toDate()); }} />

                        <Stack spacing={2} direction="row" sx={{ alignItems: "center", mb: 1 }}>
                            <VolumeDown />
                            <Slider value={volume} onChange={handleVolumeChange} valueLabelDisplay="auto" />
                            <VolumeUp />
                        </Stack>

                        <FormControlLabel
                            control={<Checkbox checked={enableScheduler} onChange={handleSchedulerChange} />}
                            label={t('settings.enableScheduler')}
                        />

                        {azanList && (
                            <Stack direction="row" spacing={1} alignItems="center">
                                <FormControl fullWidth>
                                    <InputLabel>{t('settings.audio')}</InputLabel>
                                    <Select value={audioFile?.id ?? ""} onChange={(event) => { handleAzanChange(event); }}>
                                        {azanList.map((azan: AudioFile) => (
                                            <MenuItem key={azan.id} value={azan.id}>
                                                {azan.name}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="audio/mpeg,.mp3"
                                    hidden
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) uploadMutation.mutate(file);
                                        e.target.value = "";
                                    }}
                                />
                                <Tooltip title={t('settings.importMp3')}>
                                    <span>
                                        <IconButton onClick={() => fileInputRef.current?.click()} disabled={uploadMutation.isPending}>
                                            <UploadFile />
                                        </IconButton>
                                    </span>
                                </Tooltip>
                                <Tooltip title={t('settings.deleteAudio')}>
                                    <span>
                                        <IconButton
                                            color="error"
                                            disabled={!audioFile?.name || deleteMutation.isPending}
                                            onClick={() => {
                                                if (audioFile?.name) {
                                                    deleteMutation.mutate(audioFile.name);
                                                    setAudioFile(null);
                                                }
                                            }}
                                        >
                                            <DeleteOutline />
                                        </IconButton>
                                    </span>
                                </Tooltip>
                            </Stack>
                        )}

                        {audioFile && (
                            <audio src={`data:audio/mpeg;base64,${audioFile.blob?.toString()}`} controls>
                                <track kind="captions" />
                            </audio>
                        )}

                        <Box sx={{ p: 2, display: "flex", justifyContent: "flex-end" }}>
                            <Button variant="contained" onClick={handleSave} disabled={mutateSettings.isPending}>
                                {mutateSettings.isPending ? t('settings.saving') : t('settings.save')}
                            </Button>
                        </Box>
                    </Grid>
                </Box>
            </Dialog>
        </LocalizationProvider>
    );
}
