/**
 * ExportButton — Menu d'export (SVG, PNG, GIF).
 *
 * Phase 4 : dropdown avec 3 options d'export.
 * SVG = client-side, PNG/GIF = via backend.
 */

import { useState, useRef, useEffect } from "react";
import { useDiagramState } from "../../hooks/useDiagramState";
import { useExport } from "../../hooks/useExport";

export default function ExportButton() {
  const data = useDiagramState((s) => s.data);
  const themeName = useDiagramState((s) => s.themeName);
  const { exportSvg, exportToPng, exportToGif, isExporting, exportError } =
    useExport();
  const [isOpen, setIsOpen] = useState(false);
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

  if (!data) return null;

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isExporting}
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium
                   bg-emerald-600 text-white rounded-md
                   hover:bg-emerald-700 disabled:bg-slate-300
                   transition-colors cursor-pointer"
      >
        {isExporting ? (
          <>
            <svg
              className="animate-spin h-3.5 w-3.5"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="3"
                className="opacity-25"
              />
              <path
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                fill="currentColor"
                className="opacity-75"
              />
            </svg>
            Export...
          </>
        ) : (
          <>
            <svg
              className="w-3.5 h-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
            </svg>
            Export
            <svg
              className="w-3 h-3"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </>
        )}
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-xl border border-slate-200 py-1 z-50">
          <button
            onClick={() => {
              exportSvg();
              setIsOpen(false);
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700
                       hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <span className="w-5 h-5 rounded bg-blue-100 text-blue-600 text-[10px] font-bold flex items-center justify-center">
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
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700
                       hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <span className="w-5 h-5 rounded bg-green-100 text-green-600 text-[10px] font-bold flex items-center justify-center">
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
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700
                       hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <span className="w-5 h-5 rounded bg-purple-100 text-purple-600 text-[10px] font-bold flex items-center justify-center">
              GIF
            </span>
            Export GIF
            <span className="ml-auto text-[10px] text-slate-400">Backend</span>
          </button>

          {exportError && (
            <div className="px-3 py-2 text-xs text-red-500 border-t border-slate-100">
              {exportError}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
