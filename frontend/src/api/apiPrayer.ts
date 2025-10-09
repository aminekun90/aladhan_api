
import * as api from "@/api/apiConfig";
import { CONFIG } from "@/const";
import { Prayer } from "@/models/prayer";
import { Settings } from "@/models/Settings";
import { Timing } from "@/models/Timing";
export type AudioFilePath = { id: string; description: string };
export async function getAzanList(): Promise<AudioFilePath[]> {
    const azanList = await api.get<{ status: boolean, result: AudioFilePath[] }>(`${CONFIG.getAzanList}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (azanList.status) {
        return azanList.result;
    }
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


export async function getSettings(): Promise<Settings | void> {
    const settingsResp = await api.get<{ status: boolean, result: Settings }>(`${CONFIG.getSettings}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (settingsResp.status) {
        return settingsResp.result;
    }
}

export async function saveSetting(settings: Settings) {
    const response = await api.post(CONFIG.saveSettings, settings, {
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