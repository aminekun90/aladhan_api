export interface Timing {
  date: string;
  hijri_date: string;
  tz: string;
  madhab: string;
  longitude: number;
  latitude: number;
  method: string;
  times: {
    Asr: string;
    Dhuhr: string;
    Fajr: string;
    Firstthird: string;
    Imsak: string;
    Isha: string;
    Lastthird: string;
    Maghrib: string;
    Midnight: string;
    Sunrise: string;
    Sunset: string;
  } & { [key: string]: string };
}
