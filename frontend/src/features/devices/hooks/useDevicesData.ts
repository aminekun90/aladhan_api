import {
    getConnectedBluetooth,
    getDevices,
    getSoCoDevices,
    scanBluetooth,
    scheduleAllDevices,
} from "@/features/devices/api/apiDevice";
import { useToast } from "@aminekun90/react-toast";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

/**
 * All device-related server state: the DB devices, the live Sonos/Freebox scan,
 * connected Bluetooth speakers, plus the "schedule prayers" and "scan bluetooth"
 * actions (with their toasts). Keeps data concerns out of the page component.
 */
export function useDevicesData() {
    const { t } = useTranslation();
    const { show } = useToast();
    const queryClient = useQueryClient();

    const notifySuccess = (title: string, message: string) =>
        show({ type: "success", title, message, position: "top-right", duration: 3000, progressBar: true });

    const devicesQuery = useQuery({ queryKey: ["devices"], queryFn: getDevices });
    const socoQuery = useQuery({ queryKey: ["socoDevices"], queryFn: getSoCoDevices });
    const connectedBtQuery = useQuery({
        queryKey: ["connectedBluetooth"],
        queryFn: getConnectedBluetooth,
        refetchInterval: 30000,
    });

    const scheduleAllMutation = useMutation({
        mutationFn: () => scheduleAllDevices(),
        onSuccess: () => notifySuccess(t("toast.scheduled.title"), t("toast.scheduled.message")),
    });
    const syncPrayers = () => {
        notifySuccess(t("toast.synced.title"), t("toast.synced.message"));
        scheduleAllMutation.mutate();
    };

    const scanBluetoothMutation = useMutation({
        mutationFn: () => scanBluetooth(),
        onSuccess: (found) => {
            if (found.length > 0) {
                notifySuccess(t("toast.bluetooth"), t("bluetooth.found", { count: found.length }));
                queryClient.invalidateQueries({ queryKey: ["devices"] });
            } else {
                show({
                    type: "info", title: t("toast.bluetooth"), message: t("bluetooth.noneFound"),
                    position: "top-right", duration: 5000, progressBar: true,
                });
            }
        },
        onError: () => show({
            type: "error", title: t("toast.bluetooth"), message: t("bluetooth.scanFailed"),
            position: "top-right", duration: 5000, progressBar: true,
        }),
    });

    return { devicesQuery, socoQuery, connectedBtQuery, syncPrayers, scanBluetoothMutation };
}
