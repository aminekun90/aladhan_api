import { BrassRule } from "@/components/ui";
import { Stack, Typography } from "@mui/material";
import { ReactNode } from "react";

/** Centered overline title flanked by gilded divider lines. */
export function SectionHeading({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <Stack direction="row" alignItems="center" spacing={2} sx={{ width: "100%", maxWidth: 900, mx: "auto", mb: 3 }}>
      <BrassRule />
      <Typography variant="overline" sx={{ color: "var(--brass)", fontSize: "0.72rem", whiteSpace: "nowrap" }}>
        {children}
      </Typography>
      <BrassRule flip />
    </Stack>
  );
}
