// Selection state is initialized/synced from async query data (devices +
// settings), which legitimately requires setState inside the effects below.
import { createDeviceSettings } from "@/features/devices/api/apiDevice";
import { Device } from "@/features/devices/types/device";
import { Settings } from "@/models/Settings";
import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";

/**
 * Owns which device is selected and its effective settings. Auto-selects the
 * always-available "this device" player on first load, and provisions default
 * settings when a device without settings is picked.
 */
export function useDeviceSelection(
    devices: Device[] | undefined,
    settings: Settings[] | undefined,
    deviceLoading: boolean,
    settingsLoading: boolean,
) {
    const [currentDeviceIp, setCurrentDeviceIp] = useState<string | number | null | undefined>();
    const [currentSetting, setCurrentSetting] = useState<Settings | null>(null);

    const createSettingMutation = useMutation({
        // Silent: not a user "save", just provisioning defaults.
        mutationFn: (device: Device) => createDeviceSettings(device.getId()),
        onSuccess: (data: Settings | null) => { if (data) setCurrentSetting(data); },
    });

    // Keep the resolved settings in sync with the current selection.
    useEffect(() => {
        if (settings && settings.length > 0 && !settingsLoading) {
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setCurrentSetting(settings.find(s => s.device?.getIp() === currentDeviceIp) || null);
        }
    }, [settings, settingsLoading, currentDeviceIp]);

    // Default to the local "this device" player so the adhan plays out of the box.
    useEffect(() => {
        if (currentDeviceIp != null || deviceLoading || !devices?.length) return;
        const local = devices.find(d => d.type === "local_player");
        if (!local) return;
        const found = settings?.find(s => s.device?.getIp() === local.getIp());
        /* eslint-disable react-hooks/set-state-in-effect */
        setCurrentDeviceIp(local.getIp());
        if (found) setCurrentSetting(found);
        /* eslint-enable react-hooks/set-state-in-effect */
        if (!found) createSettingMutation.mutate(local);
    }, [devices, deviceLoading, settings, currentDeviceIp, createSettingMutation]);

    const selectDevice = (device: Device) => {
        // Toggle: clicking the selected device again deselects it.
        if (currentDeviceIp === device.getIp()) {
            setCurrentDeviceIp(null);
            setCurrentSetting(null);
            return;
        }
        setCurrentDeviceIp(device.getIp());
        const found = settings?.find(s => s.device?.getIp() === device.getIp());
        if (found) setCurrentSetting(found);
        else createSettingMutation.mutate(device);
    };

    return { currentDeviceIp, currentSetting, selectDevice };
}
