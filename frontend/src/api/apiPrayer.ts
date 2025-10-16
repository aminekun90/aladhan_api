
import api from "@/api/apiConfig";
import { CONFIG } from "@/const";
import { City } from "@/models/City";
import { Device, ResponseDevice } from "@/models/device";
import { Prayer } from "@/models/prayer";
import { AudioFile, Settings } from "@/models/Settings";
import { Timing } from "@/models/Timing";

export async function getAzanList(): Promise<AudioFile[]> {
    const azanList = await api.get<AudioFile[]>(`${CONFIG.getAzanList}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (azanList)
        return azanList;
    return [];
}

export async function getMethods(): Promise<{ method: string, description: string }[]> {
    const methods = await api.get<{ method: string, description: string }[]>(`${CONFIG.methods}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (methods)
        return methods;
    return [];
}

export async function getPrayers(): Promise<{ prayers: Prayer[], date: string, hijri_date: string }> {
    const prayers = await api.get<Timing>(`${CONFIG.getPrayers}?lat=47.23999925644779&lon=-1.5304936560937061`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const prayerOrder = ["Imsak", "Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"];
    const date = prayers.date;
    const hijri_date = prayers.hijri_date;
    return { date, hijri_date, prayers: prayerOrder.map((key: string) => Prayer.fromJson({ prayerName: key, time: prayers.times[key] })) };
}


export async function getSettings(): Promise<Settings[] | void> {
    const settingsResp = await api.get<Array<Settings>>(`${CONFIG.getSettings}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (settingsResp) {
        console.log("API response settings", settingsResp);
        return settingsResp.map((setting) => ({
            ...setting,
            device: Device.fromResponse(setting.device as unknown as ResponseDevice)
        }));
    }

}

export async function saveSetting(settings: Settings) {
    // Save settings to backend transform a dict of {key: string, value: string}

    const response = await api.put(CONFIG.saveSettings, [{
        id: settings.id,
        volume: settings.volume,
        enable_scheduler: settings.enable_scheduler,
        selected_method: settings.selected_method,
        force_date: settings.force_date,
        city_id: settings.city_id,
        device_id: settings.device_id,
        audio_id: settings.audio_id,
    }], {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (response) {
        return response;
    }
}

export async function allTimings(month?: number, year?: number): Promise<Timing[]> {

    const currentDate = new Date();
    const finalMonth = month ?? (currentDate.getMonth() + 1).toString();
    const finalYear = year ?? currentDate.getFullYear().toString();

    const finalUrl = `${CONFIG.allTimings}?month=${finalMonth}&year=${finalYear}&lat=47.23999925644779&lon=-1.5304936560937061`;

    const response = await api.get<Timing[]>(finalUrl, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    return response;

}


export async function getCitiesByName(name: string, country?: string): Promise<City[]> {

    const response = await api.get<City[]>(`${CONFIG.getCitiesByName}?name=${name}${country ? 'country=' + country : ''}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return response;
}