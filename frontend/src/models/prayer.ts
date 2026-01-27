export class Prayer {
  private prayerName: string = "";
  private time: Date = new Date();
  private timeZone: string = "";
  getTime() {
    return this.time;
  }
  getTimeZone() {
    return this.timeZone;
  }
  getName() {
    return this.prayerName;
  }
  static fromJson(jsonObj: { prayerName: string; time: string; timeZone: string; }): Prayer {
    const prayer = new Prayer();
    prayer.prayerName = jsonObj.prayerName;
    prayer.time = parseTime(jsonObj.time);
    prayer.timeZone = jsonObj.timeZone;

    return prayer;
  }
}

function parseTime(timeString: string): Date {
  const timeParts = timeString.split(' ')[0].split(':');
  const hours = Number.parseInt(timeParts[0], 10);
  const minutes = Number.parseInt(timeParts[1], 10);

  const currentDate = new Date();
  currentDate.setHours(hours, minutes, 0, 0);

  return currentDate;
}

export interface DateInfo { hijri: { weekday: { ar: string; }; day: string; month: { ar: string; }; year: string; } };

export interface PrayerRow {
  id: number;
  date: string;
  hijri: string;
  imsak: string;
  fajr: string;
  dhuhr: string;
  asr: string;
  maghrib: string;
  isha: string;
};
export interface PrayerColumn {
  field: string;
  headerName: string;
  flex: number;
}