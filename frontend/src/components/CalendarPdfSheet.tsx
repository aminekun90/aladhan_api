import { Timing } from "@/models/Timing";
import dayjs from "dayjs";
import { forwardRef } from "react";
import { useTranslation } from "react-i18next";

const PRAYER_COLUMNS = ["Imsak", "Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"] as const;

/** "06:06:18 (CEST)" -> "06:06". */
function hhmm(value?: string): string {
  if (!value) return "—";
  const time = value.split(" ")[0];
  return time.slice(0, 5);
}

/** Gregorian day in the active locale (the global dayjs locale is set by i18n). */
function gregorianDay(iso: string): string {
  const d = dayjs(iso).format("ddd DD");
  return d.charAt(0).toUpperCase() + d.slice(1);
}

const ARABIC_INDIC = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"];

/** Convert Western digits to Arabic-Indic so the whole Hijri date is uniform
 * RTL (Western digits get reordered by the bidi algorithm inside Arabic). */
function toArabicDigits(value: string): string {
  return value.replace(/[0-9]/g, (d) => ARABIC_INDIC[Number(d)]);
}

/** Drop the leading Arabic weekday (already shown in the Gregorian column) and
 * use Arabic-Indic numerals for correct right-to-left reading. */
function hijriDayMonthYear(hijri: string): string {
  const parts = hijri.trim().split(/\s+/);
  const withoutWeekday = parts.length > 1 ? parts.slice(1).join(" ") : hijri;
  return toArabicDigits(withoutWeekday);
}

interface CalendarPdfSheetProps {
  events: Timing[];
  monthLabel: string;
  hijriLabel: string;
  location: string;
  method: string;
}

/** Off-screen, print-styled calendar sheet rasterized into the PDF. */
export const CalendarPdfSheet = forwardRef<HTMLDivElement, CalendarPdfSheetProps>(
  ({ events, monthLabel, hijriLabel, location, method }, ref) => {
    const { t } = useTranslation();
    return (
      <div ref={ref} className="pdf-sheet">
        <header className="pdf-header">
          <svg className="pdf-arch" width="48" height="56" viewBox="0 0 48 56" aria-hidden>
            <path
              d="M8 56 L8 26 A 16 22 0 0 1 24 4 A 16 22 0 0 1 40 26 L40 56"
              fill="none"
              stroke="#b3893f"
              strokeWidth="1.6"
            />
            <circle cx="24" cy="9" r="2" fill="#b3893f" />
          </svg>
          <h1 className="pdf-wordmark">Aladhan</h1>
          <p className="pdf-title">{t('pdf.title')} · {monthLabel}</p>
          {hijriLabel && <p className="pdf-hijri-head">{hijriLabel}</p>}
          <p className="pdf-meta">{location} · {t('pdf.method')} {method}</p>
        </header>

        <div className="pdf-rule" />

        <table className="pdf-table">
          <thead>
            <tr>
              <th>{t('pdf.date')}</th>
              <th>{t('pdf.hijri')}</th>
              {PRAYER_COLUMNS.map((p) => (
                <th key={p}>{p}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.date}>
                <td>{gregorianDay(event.date)}</td>
                <td className="pdf-hijri-cell">
                  <span className="pdf-hijri">{hijriDayMonthYear(event.hijri_date)}</span>
                </td>
                {PRAYER_COLUMNS.map((p) => (
                  <td key={p}>{hhmm(event.times[p])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        <footer className="pdf-footer">
          <span>github.com/aminekun90/aladhan_api</span>
          <span>{t('pdf.generatedOn', { date: dayjs().format("DD/MM/YYYY") })}</span>
        </footer>
      </div>
    );
  },
);

CalendarPdfSheet.displayName = "CalendarPdfSheet";
