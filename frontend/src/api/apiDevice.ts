import * as api from "@/api/apiConfig";
import { CONFIG } from "@/const";
import { Device, RawData } from "@/models/device";


export async function getSoCoDevices(): Promise<Device[]> {
    const result = await api.get<RawData[]>(`${CONFIG.getSoCoDevice}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    });

    return result.map((device) => Device.fromJson(device));
}