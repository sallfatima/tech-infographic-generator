/**
 * Toolbar — Barre d'outils horizontale au-dessus du canvas.
 *
 * Phase 4 : thème, layout, undo/redo, zoom, fit + ExportButton.
 * Style compact : icônes + labels courts.
 */

import { useDiagramState, useTemporalStore } from "../../hooks/useDiagramState";
import { listThemeNames } from "../../lib/themes";
import ExportButton from "../Export/ExportButton";

const THEME_NAMES = listThemeNames();

const LAYOUT_OPTIONS = [
  { value: "auto", label: "Auto" },
  { value: "vertical", label: "Vertical" },
  { value: "horizontal", label: "Horizontal" },
  { value: "radial", label: "Radial" },
] as const;

export default function Toolbar() {
  const themeName = useDiagramState((s) => s.themeName);
  const setThemeName = useDiagramState((s) => s.setThemeName);
  const layoutMode = useDiagramState((s) => s.layoutMode);
  const setLayoutMode = useDiagramState((s) => s.setLayoutMode);
  const zoom = useDiagramState((s) => s.zoom);
  const zoomBy = useDiagramState((s) => s.zoomBy);
  const fitToScreen = useDiagramState((s) => s.fitToScreen);
  const data = useDiagramState((s) => s.data);

  const temporal = useTemporalStore();

  const handleUndo = () => temporal.getState().undo();
  const handleRedo = () => temporal.getState().redo();

  if (!data) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-white border-b border-slate-200 text-sm">
      {/* ─── Theme ─── */}
      <div className="flex items-center gap-1.5">
        <span className="text-slate-500 text-xs font-medium">Thème</span>
        <div className="flex rounded-md overflow-hidden border border-slate-200">
          {THEME_NAMES.map((name) => (
            <button
              key={name}
              onClick={() => setThemeName(name)}
              className={`px-2.5 py-1 text-xs capitalize transition-colors cursor-pointer ${
                themeName === name
                  ? "bg-blue-600 text-white"
                  : "bg-white text-slate-600 hover:bg-slate-50"
              }`}
            >
              {name}
            </button>
          ))}
        </div>
      </div>

      <div className="w-px h-5 bg-slate-200" />

      {/* ─── Layout ─── */}
      <div className="flex items-center gap-1.5">
        <span className="text-slate-500 text-xs font-medium">Layout</span>
        <select
          value={layoutMode}
          onChange={(e) =>
            setLayoutMode(
              e.target.value as "auto" | "vertical" | "horizontal" | "radial",
            )
          }
          className="px-2 py-1 text-xs rounded border border-slate-200 bg-white text-slate-700 cursor-pointer"
        >
          {LAYOUT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="w-px h-5 bg-slate-200" />

      {/* ─── Undo / Redo ─── */}
      <div className="flex items-center gap-1">
        <button
          onClick={handleUndo}
          title="Undo (Ctrl+Z)"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-500 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 10h10a5 5 0 015 5v2" />
            <path d="M3 10l4-4M3 10l4 4" />
          </svg>
        </button>
        <button
          onClick={handleRedo}
          title="Redo (Ctrl+Shift+Z)"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-500 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10H11a5 5 0 00-5 5v2" />
            <path d="M21 10l-4-4M21 10l-4 4" />
          </svg>
        </button>
      </div>

      <div className="w-px h-5 bg-slate-200" />

      {/* ─── Zoom ─── */}
      <div className="flex items-center gap-1">
        <button
          onClick={() => zoomBy(0.8)}
          title="Zoom out"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-500 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35M8 11h6" />
          </svg>
        </button>
        <span className="text-xs text-slate-500 w-10 text-center tabular-nums">
          {Math.round(zoom * 100)}%
        </span>
        <button
          onClick={() => zoomBy(1.25)}
          title="Zoom in"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-500 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35M8 11h6M11 8v6" />
          </svg>
        </button>
        <button
          onClick={fitToScreen}
          title="Fit to screen"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-500 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 3H5a2 2 0 00-2 2v3M21 8V5a2 2 0 00-2-2h-3M3 16v3a2 2 0 002 2h3M16 21h3a2 2 0 002-2v-3" />
          </svg>
        </button>
      </div>

      {/* Spacer → pousse l'export à droite */}
      <div className="flex-1" />

      {/* ─── Export ─── */}
      <ExportButton />
    </div>
  );
}
