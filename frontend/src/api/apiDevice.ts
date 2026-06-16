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

const JSON_HEADERS = { headers: { 'Content-Type': 'application/json' } };

export type PlayerAction = "play" | "pause" | "stop" | "next" | "previous" | "mute" | "unmute";

export interface PlayerState {
    device_id?: number;
    name: string;
    ip: string;
    type?: string;
    transport_state: string;
    volume?: number;
    muted?: boolean;
    track_title?: string;
    online: boolean;
}

export interface ControlResult {
    status: string;
    message: string;
    state?: PlayerState;
}

export async function controlDevice(deviceId: number, action: PlayerAction): Promise<ControlResult> {
    return api.post<ControlResult>(`device/${deviceId}/control/${action}`, {}, JSON_HEADERS);
}

export async function setDeviceVolume(deviceId: number, volume: number): Promise<ControlResult> {
    return api.post<ControlResult>(`device/${deviceId}/volume/${volume}`, {}, JSON_HEADERS);
}

export async function getDeviceState(deviceId: number): Promise<PlayerState> {
    return api.get<PlayerState>(`device/${deviceId}/state`, JSON_HEADERS);
}

export async function playDeviceAzan(deviceId: number): Promise<{ status: string; message: string }> {
    return api.post(`device/play/${deviceId}`, {}, JSON_HEADERS);
}

export interface BluetoothStatus {
    available: boolean;
    platform: string;
    bluetoothctl: boolean;
    player: string | null;
}

export async function getBluetoothStatus(): Promise<BluetoothStatus> {
    return api.get<BluetoothStatus>("bluetooth/status", JSON_HEADERS);
}

export async function scanBluetooth(timeout = 8): Promise<Device[]> {
    const result = await api.get<ResponseDevice[]>(`bluetooth/scan?timeout=${timeout}`, JSON_HEADERS);
    return (result || []).map((d) => Device.fromResponse(d));
}

export async function connectBluetooth(mac: string): Promise<{ status: string; mac: string }> {
    return api.post(`bluetooth/${mac}/connect`, {}, JSON_HEADERS);
}

export async function getConnectedBluetooth(): Promise<string[]> {
    const result = await api.get<{ connected: string[] }>("bluetooth/connected", JSON_HEADERS);
    return result?.connected ?? [];
}