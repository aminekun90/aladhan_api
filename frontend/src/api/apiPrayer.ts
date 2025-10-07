
import * as api from "@/api/apiConfig";
import { CONFIG } from "@/const";
import { DateInfo, Prayer } from "@/models/prayer";
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

export async function getPrayers(): Promise<{ prayers: Prayer[], date: DateInfo }> {
    const prayers = await api.get<{ status: boolean, result: { timings: string[], date: DateInfo } }>(`${CONFIG.getPrayers}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (prayers.status) {
        const finalPrayers: Prayer[] = [];
        const prayerData = prayers.result.timings;
        const date = prayers.result.date;
        for (const prayerName in prayerData) {
            if (Object.hasOwn(prayerData, prayerName)) {
                const time = prayerData[prayerName];
                const prayer = Prayer.fromJson({ prayerName, time });
                finalPrayers.push(prayer);
            }
        }
        const sortedPrayers = finalPrayers.sort((a, b) => a.getTime().getTime() - b.getTime().getTime());
        return { date, prayers: sortedPrayers };
    }
    return { prayers: [], date: { hijri: { weekday: { ar: "" }, day: "", month: { ar: "" }, year: "" } } };
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

    const finalUrl = `${CONFIG.allTimings}/${finalMonth}/${finalYear}`;

    const response = await api.get<{ status: boolean, result: { timings: Timing[] } }>(finalUrl, {
        headers: {
            'Content-Type': 'application/json',
        },
    });
    return response.result.timings;

}