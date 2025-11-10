import * as api from "@/api/apiConfig";
import { CONFIG } from "@/const";
import { Device, RawData, ResponseDevice } from "@/models/device";
import { Settings } from "@/models/Settings";


export async function getSoCoDevices(): Promise<Device[]> {
    const result = await api.get<RawData[]>(`${CONFIG.getSoCoDevice}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });

    return result.map((device) => Device.fromJson(device));
}

export async function getDevices(): Promise<Device[]> {
    const result = await api.get<ResponseDevice[]>(`${CONFIG.getDevices}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });

    return result.map((device) => Device.fromResponse(device)) || [];
}

export async function createDeviceSettings(deviceId?: number): Promise<Settings | null> {
    if (!deviceId) {
        return null;
    }
    const result = await api.put<Settings>(CONFIG.createDeviceSettings, { device_id: deviceId }, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return result;
}

export async function scheduleAllDevices(): Promise<void> {
    await api.get<void>(CONFIG.scheduleAllDevices, {
        headers: {
            'Content-Type': 'application/json'
        }
    });
}