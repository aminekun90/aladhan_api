import dayjs from "dayjs";
import "dayjs/locale/fr";
import "dayjs/locale/de";
import "dayjs/locale/es";
import "dayjs/locale/nl";
import "dayjs/locale/ar";
import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import ar from "./locales/ar.json";
import de from "./locales/de.json";
import en from "./locales/en.json";
import es from "./locales/es.json";
import fr from "./locales/fr.json";
import nl from "./locales/nl.json";

/**
 * Supported languages. To add one: drop a `locales/<code>.json`, import it,
 * and add an entry here (set `dir: "rtl"` for right-to-left scripts).
 * `dayjsLocale` maps to the dayjs locale used for Gregorian date formatting.
 */
export interface LanguageDef {
  code: string;
  label: string;   // shown in its own language
  flag: string;
  dir: "ltr" | "rtl";
  dayjsLocale: string;
}

export const LANGUAGES: LanguageDef[] = [
  { code: "en", label: "English", flag: "🇬🇧", dir: "ltr", dayjsLocale: "en" },
  { code: "fr", label: "Français", flag: "🇫🇷", dir: "ltr", dayjsLocale: "fr" },
  { code: "de", label: "Deutsch", flag: "🇩🇪", dir: "ltr", dayjsLocale: "de" },
  { code: "es", label: "Español", flag: "🇪🇸", dir: "ltr", dayjsLocale: "es" },
  { code: "nl", label: "Nederlands", flag: "🇳🇱", dir: "ltr", dayjsLocale: "nl" },
  { code: "ar", label: "العربية", flag: "🇸🇦", dir: "rtl", dayjsLocale: "ar" },
];

const resources = { en, fr, de, es, nl, ar } as const;

export function dirFor(code: string): "ltr" | "rtl" {
  return LANGUAGES.find((l) => l.code === code)?.dir ?? "ltr";
}

export function dayjsLocaleFor(code: string): string {
  return LANGUAGES.find((l) => l.code === code)?.dayjsLocale ?? "en";
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    supportedLngs: LANGUAGES.map((l) => l.code),
    nonExplicitSupportedLngs: true, // "fr-FR" -> "fr"
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "lang",
    },
  });

// Keep <html dir/lang> and the dayjs locale in sync with the active language.
const applyLocale = (lng: string) => {
  document.documentElement.lang = lng;
  document.documentElement.dir = dirFor(lng);
  dayjs.locale(dayjsLocaleFor(lng));
};
applyLocale(i18n.resolvedLanguage ?? "en");
i18n.on("languageChanged", applyLocale);

export default i18n;
