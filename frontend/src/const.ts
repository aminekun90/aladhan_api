/** Default location (Nantes, France) used when no city is selected. */
export const DEFAULT_COORD = {
  lat: 47.23999925644779,
  lon: -1.5304936560937061,
} as const;

export const CONFIG = {
  apiURL: "http://localhost/api/v1/",
  getSoCoDevice: "soco/devices",
  getDevices: "devices",
  getBleDevices: "bluetoothScan",
  getPrayers: "prayer-times",
  getAzanList: "audio/list",
  saveSettings: "settings/",
  getSettings: "settings/",
  playEsterEgg: "playEsterEgg",
  allTimings: "prayer-times/month",
  methods: "available-methods",
  getCitiesByName: "cities",
  createDeviceSettings: "settings/create_settings_of_device",
  scheduleAllDevices: "devices/schedule",
  getChangelog: "changelog",
  getBackendVersion: "version",
}

/** localStorage key tracking the last changelog version the user has seen. */
export const LAST_SEEN_VERSION_KEY = "aladhan:lastSeenVersion";
