/**
 * Thin logging wrapper so the app never calls `console.*` directly.
 * In production builds, debug/info are suppressed; warnings and errors are kept.
 */
const isDev = import.meta.env.DEV;

export const logger = {
  debug: (...args: unknown[]): void => {
    if (isDev) console.debug(...args);
  },
  info: (...args: unknown[]): void => {
    if (isDev) console.info(...args);
  },
  warn: (...args: unknown[]): void => {
    console.warn(...args);
  },
  error: (...args: unknown[]): void => {
    console.error(...args);
  },
};
