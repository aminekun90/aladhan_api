import * as api from "@/api/apiConfig";
import { CONFIG } from "@/const";
import { Device, RawData } from "@/models/device";

function parseJsonStr(value: string): object | string {
    try {
        return JSON.parse(value);
    } catch (e) {
        console.error("Error parsing JSON string:", e);
        return value;
    }
}
export async function getSoCoDevices(): Promise<Device[]> {
    const result = await api.get<{ success: boolean, devices: string }>(`${CONFIG.getSoCoDevice}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (result.success && result.devices) {
        const devices = result.devices;
        return (parseJsonStr(devices) as Array<Device>).map(device => Device.fromJson(device as unknown as RawData));
    } else { return []; }
}