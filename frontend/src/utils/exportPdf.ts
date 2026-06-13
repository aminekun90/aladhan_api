import { logger } from "@/utils/logger";

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

  try {
    await document.fonts.ready; // ensure Amiri/Fraunces are loaded before capture
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

  const imgWidth = pageWidth;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  const imgData = canvas.toDataURL("image/jpeg", 0.92);

  if (imgHeight <= pageHeight) {
    pdf.addImage(imgData, "JPEG", 0, 0, imgWidth, imgHeight);
  } else {
    // Slice the tall canvas across multiple pages.
    let remaining = imgHeight;
    let position = 0;
    while (remaining > 0) {
      pdf.addImage(imgData, "JPEG", 0, position, imgWidth, imgHeight);
      remaining -= pageHeight;
      if (remaining > 0) {
        pdf.addPage();
        position -= pageHeight;
      }
    }
  }

  pdf.save(filename.endsWith(".pdf") ? filename : `${filename}.pdf`);
  logger.info("Calendar PDF exported:", filename);
}
