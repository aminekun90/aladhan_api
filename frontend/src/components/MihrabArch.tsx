import { Box } from "@mui/material";

/** Decorative pointed (ogival) arch — the mihrab motif framing the hero. */
export function MihrabArch() {
  return (
    <Box
      component="svg"
      viewBox="0 0 200 280"
      aria-hidden
      sx={{
        position: "absolute",
        top: { xs: -8, md: -28 },
        left: "50%",
        transform: "translateX(-50%)",
        width: { xs: 300, sm: 380, md: 460 },
        height: "auto",
        zIndex: 0,
        pointerEvents: "none",
        opacity: 0.45,
      }}
    >
      <defs>
        <linearGradient id="archStroke" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ecca7e" stopOpacity="0.9" />
          <stop offset="55%" stopColor="#d4ad5f" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#d4ad5f" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path
        d="M28 280 L28 130 A 86 116 0 0 1 100 14 A 86 116 0 0 1 172 130 L172 280"
        fill="none"
        stroke="url(#archStroke)"
        strokeWidth="1.5"
      />
      <circle cx="100" cy="30" r="2.5" fill="#ecca7e" opacity="0.8" />
    </Box>
  );
}
