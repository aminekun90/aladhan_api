
export class Device {
  private readonly id?: number;
  private readonly name: string;
  private readonly ip?: string | number;
  type?: string;
  private currentlyPlayingTitle: {
    title?: string,
  };
  private readonly isPlaying: boolean;
  private volume: number;
  private rawAttributes: RawData;
  constructor(id?: number, name: string = "", ip?: string | number) {
    this.id = id;
    this.name = name;
    this.ip = ip;
    this.currentlyPlayingTitle = {};
    this.isPlaying = false;
    this.volume = 0;
    this.rawAttributes = {} as RawData;
  }

  getId(): number | undefined {
    return this.id;
  }

  setVolume(volume: number): void {
    this.volume = volume;
  }
  getVolume(): number {
    return this.volume;
  }
  getName(): string {
    return this.name;
  }

  getIp(): string | number | undefined {
    return this.ip;
  }

  getPlayingTitle(): { title: string } {
    return { title: this.currentlyPlayingTitle?.title ?? "" };
  }

  setPlayingTitle(playingTitle: object): void {
    this.currentlyPlayingTitle = playingTitle;
  }

  isCurrentlyPlaying(): boolean {
    return this.isPlaying;
  }
  getRawAttributes() {
    return this.rawAttributes;
  }
  static fromJson(json: RawData): Device {
    const device = new Device(undefined, json.name, json.ip_address || json.id);
    device.setPlayingTitle(json.track_info);
    device.setVolume(json.volume);

    device.rawAttributes = json;
    return device;
  }
  static fromResponse(response: ResponseDevice): Device {
    const device = new Device(response.id, response.name, response.ip);
    device.setPlayingTitle(response.raw_data.track_info);
    device.setVolume(response.raw_data.volume);
    device.rawAttributes = response.raw_data;
    device.type = response.type

    return device;
  }
}
export interface ResponseDevice {
  id: number,
  name: string,
  ip: string | number,
  raw_data: RawData,
  type: string
}


export interface RawData {
  "id"?: number,
  "name": string,
  "track_info": { title?: string },
  "current_transport_state": string,
  "ip_address": string,
  "volume": number,
  "uid": string,
  "household_id": string,
  "is_visible": boolean,
  "is_bridge": boolean,
  "is_coordinator": boolean,
  "is_soundbar": boolean,
  "is_satellite": boolean,
  "has_satellites": boolean,
  "sub_enabled": boolean,
  "sub_gain": number,
  "is_subwoofer": boolean,
  "has_subwoofer": boolean,
  "channel": string,
  "bass": number,
  "treble": number,
  "loudness": boolean,
  "balance": number,
  "audio_delay": number,
  "night_mode": boolean,
  "dialog_mode": boolean,
  "surround_enabled": boolean,
  "surround_full_volume_enabled": boolean,
  "surround_volume_tv": number,
  "surround_volume_music": number,
  "supports_fixed_volume": boolean,
  "fixed_volume": boolean,
  "soundbar_audio_input_format": string,
  "soundbar_audio_input_format_code": number,
  "trueplay": boolean,
  "status_light": boolean,
  "buttons_enabled": boolean,
  "voice_service_configured": boolean,
  "mic_enabled": boolean,
  "device_name"?: string,
  "device_model"?: string,
};
/**
 * Backend JSON structure
{
        "name": device.player_name,
        "track_info": device.get_current_track_info(),
        "current_transport_state": device.get_current_transport_info().get('current_transport_state', ''),
        "ip_adress": device.ip_address,
        "volume": device.volume,
        "uid": device.uid,
        "household_id": device.household_id,
        "is_visible": device.is_visible,
        "is_bridge": device.is_bridge,
        "is_coordinator": device.is_bridge,
        "is_soundbar": device.is_soundbar,
        "is_satellite": device.is_satellite,
        "has_satellites": device.has_satellites,
        "sub_enabled": device.sub_enabled,
        "sub_gain": device.sub_gain,
        "is_subwoofer": device.is_subwoofer,
        "has_subwoofer": device.has_subwoofer,
        "channel": device.channel,
        "bass": device.bass,
        "treble": device.treble,
        "loudness": device.loudness,
        "balance": device.balance,
        "audio_delay": device.audio_delay,
        "night_mode": device.night_mode,
        "dialog_mode": device.dialog_mode,
        "surround_enabled": device.surround_enabled,
        "surround_full_volume_enabled": device.surround_full_volume_enabled,
        "surround_volume_tv": device.surround_volume_tv,
        "surround_volume_music": device.surround_volume_music,
        "supports_fixed_volume": device.supports_fixed_volume,
        "fixed_volume": device.fixed_volume,
        "soundbar_audio_input_format": device.soundbar_audio_input_format,
        "soundbar_audio_input_format_code": device.soundbar_audio_input_format_code,
        "trueplay": device.trueplay,
        "status_light": device.status_light,
        "buttons_enabled": device.buttons_enabled,
        "voice_service_configured": device.voice_service_configured,
        "mic_enabled": device.mic_enabled,
    }
 */