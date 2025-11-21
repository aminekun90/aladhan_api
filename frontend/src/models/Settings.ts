import { Device } from "./device";

export type Settings = {
    id: number,
    selected_method: string,
    force_date?: Date | null,
    city?: {
        readonly id: number,
        readonly name: string
        readonly lat: number,
        readonly lon: number,
        readonly country: string
    },
    audio_id: number,
    device_id: number,
    city_id: number,
    device?: Device | null,
    audio?: AudioFile | null,
    volume: number,
    enable_scheduler: boolean
}

export type AudioFile = { id: number, blob: Blob, name: string };