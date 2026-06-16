import { Box, styled } from "@mui/material";

/** Brand accents (mirror of the CSS custom properties in index.css). */
export const BRASS = "#d4ad5f";
export const BRASS_BRIGHT = "#ecca7e";

/** Gilded glass surface — the recurring card/panel background. */
export const Surface = styled(Box)({
  background: "var(--surface)",
  backdropFilter: "blur(10px)",
  border: "1px solid var(--line)",
  borderRadius: "1.5rem",
});

/** Thin gilded divider line used on either side of a section heading.
 * `flip` reverses the gradient direction for the right-hand side. */
export const BrassRule = styled(Box, {
  shouldForwardProp: (prop) => prop !== "flip",
})<{ flip?: boolean }>(({ flip }) => ({
  flex: 1,
  height: "1px",
  background: `linear-gradient(90deg, ${flip ? "var(--line), transparent" : "transparent, var(--line)"})`,
}));
