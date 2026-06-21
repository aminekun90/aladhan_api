# Feature to explore: AirPlay output

Status: **not implemented** — planned. Lets the adhan play on **AirPlay-only**
receivers (HomePod, Apple TV) alongside Sonos / Freebox / Bluetooth / local.

> **Scope note:** this is *only* for receivers that have no other control path.
> **Sonos is already handled via UPnP/SoCo** (full playback + volume + transport
> + state), so AirPlay is **not** used for Sonos — it would be redundant and give
> less control. The Freebox is handled via its Player API + AirMedia fallback.
> See [speakers.md](./speakers.md) for the full backend matrix.

## Approach — `pyatv`

[`pyatv`](https://pyatv.dev) is a mature, ARM-friendly Python library that does
both halves we need:

- **Discovery** via mDNS (`_airplay._tcp` / `_raop._tcp`) — same LAN mechanism
  as Freebox discovery; works with the existing `hostNetwork` setup.
- **Playback** by streaming an audio file to a receiver over **RAOP**
  (`stream_file(adhan.mp3)`).

It slots into the existing device architecture:

- New device type `airplay_player`.
- `AirPlayService` with `scan()` and `play_file(host, path)`, dispatched in
  `device_service` exactly like the Bluetooth/Freebox backends.
- Endpoints: `GET /airplay/scan`, connection/availability check, and reuse the
  unified `/device/{id}/control` + scheduling paths.

## Open questions / tradeoffs

1. **Async**: `pyatv` is asyncio; the APScheduler jobs are sync, so playback
   runs via `asyncio.run(...)` inside the job (straightforward, but noted).
2. **Pairing/credentials**: plain AirPlay speakers stream without pairing, but
   **HomePod / Apple TV usually require AirPlay-2 pairing credentials** — a
   pairing flow similar to the Freebox button-press, persisting credentials.
   Phase 1 = credential-free receivers; Phase 2 = add pairing.
3. **New dependency** (`pyatv` + deps). Verify the ARM64 wheel/build on the Pi.
4. **Availability** = receiver currently discoverable (mirror the Sonos/Freebox
   "live scan" availability model).

## Why not the `mdns-listener-advanced` npm lib

It can *discover* AirPlay services, but it's Node (the backend is Python) and it
does **not** stream audio (no RAOP). `pyatv` covers discovery **and** streaming
in-stack, so it's the better fit here.

## Phasing

1. Discover + stream to credential-free AirPlay/RAOP receivers.
2. AirPlay-2 pairing (HomePod / Apple TV) with stored credentials.
3. Per-receiver volume + grouped playback (optional).
