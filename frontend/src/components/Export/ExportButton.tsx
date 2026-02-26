/**
 * ExportButton — Menu d'export (SVG, PNG, GIF).
 *
 * Phase 4 : dropdown avec 3 options d'export.
 * SVG = client-side, PNG/GIF = via backend.
 */

import { useState, useRef, useEffect } from "react";
import { useDiagramState } from "../../hooks/useDiagramState";
import { useExport } from "../../hooks/useExport";
import { Download, Loader2, ChevronDown } from "lucide-react";

export default function ExportButton() {
  const data = useDiagramState((s) => s.data);
  const themeName = useDiagramState((s) => s.themeName);
  const { exportSvg, exportToPng, exportToGif, isExporting, exportError } =
    useExport();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Fermer le menu au clic exterieur
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!data) return null;

  return (
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
            onClick={() => {
              exportSvg();
              setIsOpen(false);
            }}
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
            onClick={() => {
              exportToPng(data, themeName);
              setIsOpen(false);
            }}
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
            onClick={() => {
              exportToGif(data, themeName);
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-200
                       hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors cursor-pointer"
          >
            <span className="w-5 h-5 rounded bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 text-[10px] font-bold flex items-center justify-center">
              GIF
            </span>
            Export GIF
            <span className="ml-auto text-[10px] text-slate-400">Backend</span>
          </button>

          {exportError && (
            <div className="px-3 py-2 text-xs text-red-500 border-t border-slate-100 dark:border-slate-700">
              {exportError}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
