/**
 * ExportButton — Menu d'export (SVG, PNG, GIF).
 *
 * Phase 4 : dropdown avec 3 options + toast de feedback.
 * SVG = client-side, PNG/GIF = via backend.
 */

import { useState, useRef, useEffect, useCallback } from "react";
import { useDiagramState } from "../../hooks/useDiagramState";
import { useExport } from "../../hooks/useExport";
import { Download, Loader2, ChevronDown, CheckCircle, XCircle } from "lucide-react";

type ToastState = { type: "success" | "error"; message: string } | null;

export default function ExportButton() {
  const data = useDiagramState((s) => s.data);
  const themeName = useDiagramState((s) => s.themeName);
  const { exportSvg, exportToPng, exportToGif, isExporting } = useExport();
  const [isOpen, setIsOpen] = useState(false);
  const [toast, setToast] = useState<ToastState>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Fermer le menu au clic extérieur
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Auto-masquer le toast après 4s
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(t);
  }, [toast]);

  const showToast = useCallback((type: "success" | "error", message: string) => {
    setToast({ type, message });
  }, []);

  const handleSvg = useCallback(() => {
    try {
      exportSvg();
      setIsOpen(false);
      showToast("success", "SVG téléchargé ✓");
    } catch {
      showToast("error", "Erreur export SVG");
    }
  }, [exportSvg, showToast]);

  const handlePng = useCallback(async () => {
    if (!data) return;
    setIsOpen(false);
    try {
      await exportToPng(data, themeName);
      showToast("success", "PNG téléchargé ✓");
    } catch (e) {
      showToast("error", e instanceof Error ? e.message : "Erreur export PNG");
    }
  }, [data, themeName, exportToPng, showToast]);

  const handleGif = useCallback(async () => {
    if (!data) return;
    setIsOpen(false);
    try {
      await exportToGif(data, themeName);
      showToast("success", "GIF téléchargé ✓");
    } catch (e) {
      showToast("error", e instanceof Error ? e.message : "Erreur export GIF");
    }
  }, [data, themeName, exportToGif, showToast]);

  if (!data) return null;

  return (
    <>
      {/* Toast notification — position fixe en bas à droite */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-[100] flex items-center gap-2 px-4 py-3
                      rounded-lg shadow-lg text-sm font-medium animate-in fade-in slide-in-from-bottom-2
                      ${toast.type === "success"
                        ? "bg-emerald-600 text-white"
                        : "bg-red-600 text-white"}`}
        >
          {toast.type === "success"
            ? <CheckCircle size={16} />
            : <XCircle size={16} />}
          {toast.message}
        </div>
      )}

      {/* Bouton + dropdown */}
      <div className="relative" ref={menuRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          disabled={isExporting}
          aria-label="Menu d'export"
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium
                     bg-emerald-600 text-white rounded-md
                     hover:bg-emerald-700 disabled:bg-slate-300
                     transition-colors cursor-pointer"
        >
          {isExporting ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              Export...
            </>
          ) : (
            <>
              <Download size={14} />
              Export
              <ChevronDown size={12} />
            </>
          )}
        </button>

        {/* Dropdown menu */}
        {isOpen && (
          <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 py-1 z-50">
            <button
              onClick={handleSvg}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-200
                         hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >
              <span className="w-5 h-5 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 text-[10px] font-bold flex items-center justify-center">
                SVG
              </span>
              Export SVG
              <span className="ml-auto text-[10px] text-slate-400">Client</span>
            </button>

            <button
              onClick={handlePng}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-200
                         hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >
              <span className="w-5 h-5 rounded bg-green-100 dark:bg-green-900/40 text-green-600 dark:text-green-400 text-[10px] font-bold flex items-center justify-center">
                PNG
              </span>
              Export PNG
              <span className="ml-auto text-[10px] text-slate-400">Backend</span>
            </button>

            <button
              onClick={handleGif}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-200
                         hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >
              <span className="w-5 h-5 rounded bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 text-[10px] font-bold flex items-center justify-center">
                GIF
              </span>
              Export GIF
              <span className="ml-auto text-[10px] text-slate-400">Backend</span>
            </button>
          </div>
        )}
      </div>
    </>
  );
}
