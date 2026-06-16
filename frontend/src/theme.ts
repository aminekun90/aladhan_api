import { alpha, createTheme } from "@mui/material/styles";

// "Mihrab at Dawn" palette
const INK = "#080b14";
const NIGHT = "#0d1426";
const PARCHMENT = "#ece6d6";
const MIST = "#9aa1b6";
const BRASS = "#d4ad5f";
const BRASS_BRIGHT = "#ecca7e";
const DAWN = "#e0905a";

const FONT_UI = '"Bricolage Grotesque", system-ui, sans-serif';
const FONT_DISPLAY = '"Fraunces", Georgia, serif';

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: BRASS, light: BRASS_BRIGHT, contrastText: INK },
    secondary: { main: DAWN },
    background: { default: INK, paper: NIGHT },
    text: { primary: PARCHMENT, secondary: MIST },
    divider: alpha(PARCHMENT, 0.1),
  },
  shape: { borderRadius: 18 },
  typography: {
    fontFamily: FONT_UI,
    h1: { fontFamily: FONT_DISPLAY, fontWeight: 400, letterSpacing: "-0.02em" },
    h2: { fontFamily: FONT_DISPLAY, fontWeight: 400, letterSpacing: "-0.02em" },
    h3: { fontFamily: FONT_DISPLAY, fontWeight: 400, letterSpacing: "-0.01em" },
    h4: { fontFamily: FONT_DISPLAY, fontWeight: 400 },
    h5: { fontFamily: FONT_DISPLAY, fontWeight: 500 },
    h6: { fontFamily: FONT_UI, fontWeight: 600 },
    button: { fontFamily: FONT_UI, fontWeight: 600, letterSpacing: "0.02em" },
    overline: { fontFamily: FONT_UI, letterSpacing: "0.32em", fontWeight: 600 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: "transparent" },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          backgroundColor: alpha(NIGHT, 0.7),
          backdropFilter: "blur(12px)",
          border: `1px solid ${alpha(PARCHMENT, 0.08)}`,
        },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 999, textTransform: "none", paddingInline: 20 },
        containedPrimary: {
          background: `linear-gradient(135deg, ${BRASS_BRIGHT}, ${BRASS})`,
          color: INK,
          "&:hover": { background: `linear-gradient(135deg, ${BRASS}, ${DAWN})` },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          color: PARCHMENT,
          transition: "color .2s ease, background-color .2s ease, transform .2s ease",
          "&:hover": { color: BRASS_BRIGHT, backgroundColor: alpha(BRASS, 0.1) },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        outlined: { borderColor: alpha(BRASS, 0.4), color: BRASS_BRIGHT },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: alpha(INK, 0.95),
          border: `1px solid ${alpha(BRASS, 0.3)}`,
          fontFamily: FONT_UI,
          fontSize: "0.75rem",
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: alpha(NIGHT, 0.92),
          backgroundImage: `radial-gradient(120% 80% at 50% 0%, ${alpha(BRASS, 0.08)}, transparent 60%)`,
          border: `1px solid ${alpha(BRASS, 0.18)}`,
        },
      },
    },
  },
});
