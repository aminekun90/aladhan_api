import { DEFAULT_COORD } from "@/const";
import { getNearestCity } from "@/features/prayers/api/apiPrayer";
import { useGeolocation } from "@/hooks/useGeolocation";
import { Settings } from "@/models/Settings";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

/**
 * Resolves the coordinate + display label that drive prayer calculations.
 * Precedence: an explicitly configured city wins; else the device GPS position;
 * else the default location.
 */
export function usePrayerLocation(currentSetting: Settings | null) {
    const { t } = useTranslation();
    const { coords: geoCoords, status: geoStatus, request: requestLocation } = useGeolocation();

    const { data: nearestCity } = useQuery({
        queryKey: ["nearestCity", geoCoords?.lat, geoCoords?.lon],
        queryFn: () => getNearestCity(geoCoords!.lat, geoCoords!.lon),
        enabled: !!geoCoords,
    });

    const hasCity = currentSetting?.city?.lat != null && currentSetting?.city?.lon != null;
    const coord = hasCity
        ? { lat: currentSetting!.city!.lat, lon: currentSetting!.city!.lon }
        : (geoCoords ?? DEFAULT_COORD);
    const locationLabel = hasCity
        ? `${currentSetting?.city?.name ?? ""} · ${currentSetting?.city?.country ?? ""}`
        : geoCoords
            ? (nearestCity ? `${nearestCity.name} · ${nearestCity.country}` : t("location.myPosition"))
            : t("location.default");

    return { coord, locationLabel, geoCoords, geoStatus, requestLocation };
}
