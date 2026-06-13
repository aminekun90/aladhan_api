import { logger } from "@/utils/logger";

const MARGIN_MM = 12;

/**
 * Render a DOM element into a paginated A4 PDF and trigger a download.
 *
 * We rasterize the DOM (rather than drawing text with jsPDF) so Arabic Hijri
 * dates are shaped correctly by the browser using the loaded Amiri font.
 * html2canvas + jspdf are heavy, so they are loaded on demand.
 */
export async function exportElementToPdf(element: HTMLElement, filename: string): Promise<void> {
  const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
    import("html2canvas"),
    import("jspdf"),
  ]);

  // Make sure the Arabic (Amiri) and display fonts are actually loaded before
  // the capture, otherwise Arabic falls back to a non-shaping font.
  try {
    await Promise.all([
      document.fonts.load('400 16px "Amiri"'),
      document.fonts.load('700 16px "Amiri"'),
      document.fonts.ready,
    ]);
  } catch {
    /* fonts API unavailable — proceed anyway */
  }

  const canvas = await html2canvas(element, {
    scale: 2,
    backgroundColor: "#fbf8f1",
    useCORS: true,
    logging: false,
  });

  const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();

  // Fit the whole sheet onto a single page, preserving aspect ratio.
  const maxWidth = pageWidth - MARGIN_MM * 2;
  const maxHeight = pageHeight - MARGIN_MM * 2;
  const ratio = canvas.height / canvas.width;

  let imgWidth = maxWidth;
  let imgHeight = imgWidth * ratio;
  if (imgHeight > maxHeight) {
    imgHeight = maxHeight;
    imgWidth = imgHeight / ratio;
  }
  const x = (pageWidth - imgWidth) / 2;

  pdf.addImage(canvas.toDataURL("image/jpeg", 0.95), "JPEG", x, MARGIN_MM, imgWidth, imgHeight);
  pdf.save(filename.endsWith(".pdf") ? filename : `${filename}.pdf`);
  logger.info("Calendar PDF exported:", filename);
}
