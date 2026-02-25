/**
 * Toolbar — Barre d'outils horizontale au-dessus du canvas.
 *
 * Inclut : theme, layout, undo/redo, zoom, view toggles (SVG/Image/JSON),
 * download direct, et ExportButton.
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
  const viewMode = useDiagramState((s) => s.viewMode);
  const setViewMode = useDiagramState((s) => s.setViewMode);
  const showJsonView = useDiagramState((s) => s.showJsonView);
  const setShowJsonView = useDiagramState((s) => s.setShowJsonView);
  const generatedImageUrl = useDiagramState((s) => s.generatedImageUrl);
  const generatedFilename = useDiagramState((s) => s.generatedFilename);

  const temporal = useTemporalStore();

  const handleUndo = () => temporal.getState().undo();
  const handleRedo = () => temporal.getState().redo();

  const handleDownload = () => {
    if (!generatedImageUrl) return;
    const a = document.createElement("a");
    a.href = generatedImageUrl;
    a.download = generatedFilename ?? "infographic.png";
    a.click();
  };

  if (!data) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 text-sm flex-wrap">
      {/* ─── Theme ─── */}
      <div className="flex items-center gap-1.5">
        <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Theme</span>
        <div className="flex rounded-md overflow-hidden border border-slate-200 dark:border-slate-600">
          {THEME_NAMES.map((name) => (
            <button
              key={name}
              onClick={() => setThemeName(name)}
              className={`px-2.5 py-1 text-xs capitalize transition-colors cursor-pointer ${
                themeName === name
                  ? "bg-blue-600 text-white"
                  : "bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600"
              }`}
            >
              {name}
            </button>
          ))}
        </div>
      </div>

      <div className="w-px h-5 bg-slate-200 dark:bg-slate-600" />

      {/* ─── Layout ─── */}
      <div className="flex items-center gap-1.5">
        <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Layout</span>
        <select
          value={layoutMode}
          onChange={(e) =>
            setLayoutMode(
              e.target.value as "auto" | "vertical" | "horizontal" | "radial",
            )
          }
          className="px-2 py-1 text-xs rounded border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 cursor-pointer"
        >
          {LAYOUT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="w-px h-5 bg-slate-200 dark:bg-slate-600" />

      {/* ─── View Mode Toggle ─── */}
      <div className="flex items-center gap-1.5">
        <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Vue</span>
        <div className="flex rounded-md overflow-hidden border border-slate-200 dark:border-slate-600">
          <button
            onClick={() => { setViewMode("svg"); setShowJsonView(false); }}
            className={`px-2.5 py-1 text-xs transition-colors cursor-pointer ${
              viewMode === "svg" && !showJsonView
                ? "bg-blue-600 text-white"
                : "bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600"
            }`}
          >
            SVG
          </button>
          {generatedImageUrl && (
            <button
              onClick={() => { setViewMode("image"); setShowJsonView(false); }}
              className={`px-2.5 py-1 text-xs transition-colors cursor-pointer ${
                viewMode === "image" && !showJsonView
                  ? "bg-blue-600 text-white"
                  : "bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600"
              }`}
            >
              Image
            </button>
          )}
          <button
            onClick={() => setShowJsonView(!showJsonView)}
            className={`px-2.5 py-1 text-xs transition-colors cursor-pointer ${
              showJsonView
                ? "bg-blue-600 text-white"
                : "bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600"
            }`}
          >
            JSON
          </button>
        </div>
      </div>

      <div className="w-px h-5 bg-slate-200 dark:bg-slate-600" />

      {/* ─── Undo / Redo ─── */}
      <div className="flex items-center gap-1">
        <button
          onClick={handleUndo}
          title="Undo (Ctrl+Z)"
          className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 10h10a5 5 0 015 5v2" />
            <path d="M3 10l4-4M3 10l4 4" />
          </svg>
        </button>
        <button
          onClick={handleRedo}
          title="Redo (Ctrl+Shift+Z)"
          className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10H11a5 5 0 00-5 5v2" />
            <path d="M21 10l-4-4M21 10l-4 4" />
          </svg>
        </button>
      </div>

      <div className="w-px h-5 bg-slate-200 dark:bg-slate-600" />

      {/* ─── Zoom ─── */}
      <div className="flex items-center gap-1">
        <button
          onClick={() => zoomBy(0.8)}
          title="Zoom out"
          className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35M8 11h6" />
          </svg>
        </button>
        <span className="text-xs text-slate-500 dark:text-slate-400 w-10 text-center tabular-nums">
          {Math.round(zoom * 100)}%
        </span>
        <button
          onClick={() => zoomBy(1.25)}
          title="Zoom in"
          className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35M8 11h6M11 8v6" />
          </svg>
        </button>
        <button
          onClick={fitToScreen}
          title="Fit to screen"
          className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 3H5a2 2 0 00-2 2v3M21 8V5a2 2 0 00-2-2h-3M3 16v3a2 2 0 002 2h3M16 21h3a2 2 0 002-2v-3" />
          </svg>
        </button>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* ─── Download (si image generee) ─── */}
      {generatedImageUrl && (
        <button
          onClick={handleDownload}
          title="Telecharger l'image"
          className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 transition-colors cursor-pointer"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
          </svg>
          Download
        </button>
      )}

      {/* ─── Export ─── */}
      <ExportButton />
    </div>
  );
}
