import { BrassRule } from "@/components/ui";
import { Box, Stack, Typography } from "@mui/material";
import { ReactNode } from "react";

/** Small gilded diamond — a discreet oriental flourish for section titles. */
function Lozenge() {
  return (
    <Box
      sx={{
        width: 6,
        height: 6,
        flexShrink: 0,
        transform: "rotate(45deg)",
        border: "1px solid var(--brass)",
        boxShadow: "0 0 8px rgba(212,173,95,0.45)",
      }}
    />
  );
}

/** Centered overline title flanked by gilded divider lines and lozenges. */
export function SectionHeading({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <Stack direction="row" alignItems="center" spacing={1.5} sx={{ width: "100%", maxWidth: 900, mx: "auto", mb: 3.5 }}>
      <BrassRule />
      <Lozenge />
      <Typography variant="overline" sx={{ color: "var(--brass)", fontSize: "0.72rem", letterSpacing: "0.28em", whiteSpace: "nowrap" }}>
        {children}
      </Typography>
      <Lozenge />
      <BrassRule flip />
    </Stack>
  );
}
