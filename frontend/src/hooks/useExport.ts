/**
 * useExport — Hook pour exporter le diagramme en PNG, SVG ou GIF.
 *
 * - Export SVG : capture directement le DOM SVG
 * - Export PNG : envoie InfographicData au backend PIL
 * - Export GIF : envoie InfographicData au backend PIL (animé)
 */

import { useState, useCallback } from "react";
import type { InfographicData } from "../types/infographic";
import { exportPng, exportGif } from "../api/client";

interface UseExportReturn {
  /** Exporte le SVG du DOM directement. */
  exportSvg: () => void;

  /** Exporte en PNG via le backend. */
  exportToPng: (data: InfographicData, theme?: string) => Promise<void>;

  /** Exporte en GIF via le backend. */
  exportToGif: (data: InfographicData, theme?: string) => Promise<void>;

  /** Indicateur de chargement. */
  isExporting: boolean;

  /** Erreur d'export. */
  exportError: string | null;
}

export function useExport(): UseExportReturn {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // ─── Export SVG (client-side) ─────────────────────────────────────
  const exportSvg = useCallback(() => {
    try {
      const svgEl = document.querySelector<SVGSVGElement>(
        "svg[viewBox]",
      );
      if (!svgEl) {
        setExportError("Aucun SVG trouvé");
        return;
      }

      // Clone pour nettoyer les attributs Rough.js temporaires
      const clone = svgEl.cloneNode(true) as SVGSVGElement;

      // Ajouter xmlns si manquant
      if (!clone.getAttribute("xmlns")) {
        clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      }

      const svgString = new XMLSerializer().serializeToString(clone);
      const blob = new Blob([svgString], { type: "image/svg+xml" });
      downloadBlob(blob, "infographic.svg");
      setExportError(null);
    } catch (e) {
      setExportError(e instanceof Error ? e.message : "Erreur export SVG");
    }
  }, []);

  // ─── Export PNG (via backend) ─────────────────────────────────────
  const exportToPng = useCallback(
    async (data: InfographicData, theme = "whiteboard") => {
      setIsExporting(true);
      setExportError(null);
      try {
        const blob = await exportPng(data, theme);
        downloadBlob(blob, "infographic.png");
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Erreur export PNG";
        setExportError(msg);
        throw new Error(msg); // re-throw pour que l'appelant puisse afficher un toast
      } finally {
        setIsExporting(false);
      }
    },
    [],
  );

  // ─── Export GIF (via backend) ─────────────────────────────────────
  const exportToGif = useCallback(
    async (data: InfographicData, theme = "whiteboard") => {
      setIsExporting(true);
      setExportError(null);
      try {
        const blob = await exportGif(data, theme);
        downloadBlob(blob, "infographic.gif");
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Erreur export GIF";
        setExportError(msg);
        throw new Error(msg); // re-throw pour que l'appelant puisse afficher un toast
      } finally {
        setIsExporting(false);
      }
    },
    [],
  );

  return { exportSvg, exportToPng, exportToGif, isExporting, exportError };
}

// ─── Helper ─────────────────────────────────────────────────────────

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  // Délai avant revocation — Chrome doit avoir le temps de lancer le dl
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 1000);
}
