# Speakers & playback architecture

How the adhan is sent to each kind of device, and the decisions behind it.

## Backend matrix

| Device type (`Device.type`) | Transport | Volume | Transport ctrl | State |
|-|-|-|-|-|
| `sonos_player` | **UPnP** via SoCo (`play_uri`) | ✅ | play/pause/stop/next/prev/mute | ✅ full |
| `freebox_player` | Freebox **Player API** (`control/open`), **AirMedia fallback** | ✅ | play/pause/stop/mute | best-effort |
| `freebox_airmedia` | Freebox **AirMedia** push | ❌ | **stop only** | minimal |
| `bluetooth_speaker` | BlueZ (host `bluetoothctl` over D-Bus) | host mixer | — | — |
| `local_player` ("Cet appareil") | ALSA on the host (`mpg123`) | host mixer | — | — |
| `airplay_player` | *planned* — see [airplay.md](./airplay.md) | — | — | — |

All playback is dispatched from one place: `DeviceService._play_on_device`.

## How each backend works

### Sonos — UPnP (SoCo)
Discovered via SSDP and controlled with [SoCo](https://github.com/SoCo/SoCo):
`play_uri(url)`, `volume`, and full transport/state. The app serves the adhan
audio at `http://<host-ip>:8000/api/v1/audio/<file>` and Sonos fetches it.

> **Why not AirPlay for Sonos?** Modern Sonos *are* AirPlay-2 receivers, but
> UPnP already gives us complete control (playback, volume, transport, state),
> while pushing via AirPlay would require the app to become an AirPlay sender and
> would expose *less* control. So Sonos stays on UPnP. AirPlay is reserved for
> AirPlay-only receivers (HomePod / Apple TV) — tracked in [airplay.md](./airplay.md).

### Freebox — Player API + AirMedia fallback
- **Primary**: the Freebox Player media API (`/api/v{N}/player/{id}/api/v{M}/control/open`).
- **Fallback**: if the Player is unreachable or rejects the command, the same URL
  is pushed via **AirMedia** (`/api/v{N}/airmedia/receivers/{name}/`). This is
  automatic inside `FreeboxService.play_media`.
- **Dynamic API version**: the box major version comes from `GET /api_version`
  (`api_base_url` + `api_version`), and each player's embedded API version comes
  from the player list — nothing is hardcoded to `v8`/`v6`, so Freebox OS
  upgrades don't break playback.
- **Auth**: pairing (press the RIGHT arrow on the box) → `app_token`, then
  challenge-response login (`HMAC-SHA1`) → `session_token`. Token persisted on disk.

#### AirMedia as a first-class device
AirMedia receivers are also exposed as `freebox_airmedia` devices (identified by
their name) so they can be targeted directly via the unified API. Limitations:
AirMedia is push-only, so it supports **stop** but not pause/seek/volume, and has
no status endpoint. Audio is sent as `media_type: "video"` (AirMedia exposes only
`photo`/`video`).

REST endpoints:
- `GET  /api/v1/freebox/airmedia/receivers`
- `POST /api/v1/freebox/airmedia/{receiver_name}/play` — body `{ media_url, password? }`
- `POST /api/v1/freebox/airmedia/{receiver_name}/stop`

### Bluetooth & local
Bluetooth speakers are driven through the host's BlueZ stack over the system
D-Bus; the local device plays through ALSA on the host. Both require the
container to reach host hardware (see deployment below).

## Discovery & networking
Sonos (SSDP) and Freebox (mDNS `_fbx-api._tcp`) discovery rely on **multicast**,
which only reaches the app when it shares the host network. In Docker that's
`network_mode: host`; in Kubernetes it's `hostNetwork: true` +
`dnsPolicy: ClusterFirstWithHostNet`. The pod must run on the Pi that has the
sound card / Bluetooth adapter — pin it with the chart `nodeSelector`
(or `ADHAN_NODE=<hostname> ./deploy.sh`). See the `k8s-project` repo.

## Decision summary
- **Sonos → UPnP** (don't add AirPlay; it's redundant and weaker).
- **Freebox → Player API, with automatic AirMedia fallback** + dynamic API version.
- **AirMedia → also a standalone device type** (`freebox_airmedia`), stop-only.
- **AirPlay-only receivers (HomePod/Apple TV) → future**, via `pyatv` ([airplay.md](./airplay.md)).
