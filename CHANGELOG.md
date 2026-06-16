# Changelog

All notable changes to this project are documented here.

## [0.1.1] — 2026-06-16

Major overhaul: calculation engine, adhan scheduling, multi-backend players,
new UI, multi-language, and Pi/Docker deployment.

### Added
- **Players**: unified transport controls (play/pause/stop/next/prev/mute/volume/state) for Sonos & Freebox; **Bluetooth** (BlueZ) speakers; always-on **"This device"** local player (enabled & selected by default).
- **Audio**: bundled default adhan + MP3 upload/delete from settings.
- **Location**: browser geolocation + reverse-geocoding to a city name.
- **PDF**: branded single-page calendar export with authentic Arabic Hijri dates.
- **i18n**: 6 languages (EN, FR, DE, ES, NL, AR) with RTL for Arabic; one-line to add more.
- **Deploy**: PWA install, optional Caddy HTTPS, Docker audio/Bluetooth passthrough; multi-arch image (amd64 + arm64) on Docker Hub.

### Changed
- **UI**: "Mihrab at Dawn" redesign, fully responsive; clear device selection + per-device settings on the card; `styled()` primitives instead of inline styles.
- **Cities DB**: 1.5 GB → 12 MB (~129k populated places, deduped, population-ranked).

### Fixed
- **Calc**: aligned with the canonical Swift engine — Maghrib config, high-latitude fallback, method-aware midnight/night-thirds.
- **Scheduler**: true singleton + datetime-based scheduling (fixes DST/post-reboot day errors).
- **Devices**: availability reflects live discovery (offline shown correctly); `get_device_by_id/ip` now returns `type`; `raw_data` double-encoding.
- **Freebox**: mDNS discovery, non-blocking pairing, robust playback.
- **API/deploy**: real 404 on SPA fallback; case-correct `Dockerfile`; `.dockerignore`; host networking, persistence volume, healthcheck.
- **CI**: fixed Docker publish workflow, generate `cities.db`, bumped actions.

### Notes
- Hardware-dependent paths (Sonos/Freebox/Bluetooth discovery, mobile geolocation over HTTPS, PDF rendering) should be smoke-tested on the Pi.
