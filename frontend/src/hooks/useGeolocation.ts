import { logger } from "@/utils/logger";
import { useCallback, useEffect, useState } from "react";

export interface GeoCoords {
  lat: number;
  lon: number;
}

interface GeolocationState {
  coords: GeoCoords | null;
  status: "idle" | "locating" | "granted" | "denied" | "unavailable";
  request: () => void;
}

/**
 * Browser geolocation. Auto-requests once on mount so prayer times can be
 * computed from the device's real position — no manual city selection needed.
 * Coordinates alone drive the prayer calculation; a city is only for display.
 */
export function useGeolocation(auto = true): GeolocationState {
  const [coords, setCoords] = useState<GeoCoords | null>(null);
  const [status, setStatus] = useState<GeolocationState["status"]>("idle");

  const request = useCallback(() => {
    if (!("geolocation" in navigator)) {
      setStatus("unavailable");
      return;
    }
    setStatus("locating");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        setStatus("granted");
      },
      (err) => {
        logger.warn("Geolocation denied/unavailable:", err.message);
        setStatus(err.code === err.PERMISSION_DENIED ? "denied" : "unavailable");
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 },
    );
  }, []);

  useEffect(() => {
    if (!auto) return;
    // Defer out of the synchronous effect body to avoid cascading renders.
    const id = setTimeout(request, 0);
    return () => clearTimeout(id);
  }, [auto, request]);

  return { coords, status, request };
}
