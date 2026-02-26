/**
 * Toolbar — Barre d'outils horizontale au-dessus du canvas.
 *
 * Inclut : theme, layout, undo/redo, zoom, view toggles (SVG/Image/JSON),
 * download direct, et ExportButton.
 */

import { useState } from "react";
import { useDiagramState, useTemporalStore } from "../../hooks/useDiagramState";
import { listThemeNames } from "../../lib/themes";
import ExportButton from "../Export/ExportButton";
import SharePanel from "../Export/SharePanel";
import {
  Undo2, Redo2, ZoomIn, ZoomOut, Maximize2, Download, Info, Share2,
} from "lucide-react";

const THEME_NAMES = listThemeNames();

const LAYOUT_OPTIONS = [
  { value: "auto", label: "Auto" },
  { value: "vertical", label: "Vertical" },
  { value: "horizontal", label: "Horizontal" },
  { value: "radial", label: "Radial" },
] as const;

/** Tooltip wrapper reutilisable. */
function Tip({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <span className="group relative inline-flex">
      {children}
      <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 px-2 py-0.5
                        text-[10px] bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-800
                        rounded opacity-0 group-hover:opacity-100 transition-opacity
                        pointer-events-none whitespace-nowrap z-50 shadow-sm">
        {label}
      </span>
    </span>
  );
}

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
  const showLegend = useDiagramState((s) => s.showLegend);
  const setShowLegend = useDiagramState((s) => s.setShowLegend);

  const [shareOpen, setShareOpen] = useState(false);

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
      {/* --- Theme --- */}
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

      {/* --- Layout --- */}
      <div className="flex items-center gap-1.5">
        <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Layout</span>
        <select
          value={layoutMode}
          onChange={(e) =>
            setLayoutMode(
              e.target.value as "auto" | "vertical" | "horizontal" | "radial",
            )
          }
          aria-label="Mode de layout"
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

      {/* --- View Mode Toggle --- */}
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

      {/* --- Undo / Redo --- */}
      <div className="flex items-center gap-1">
        <Tip label="Annuler (Ctrl+Z)">
          <button
            onClick={handleUndo}
            aria-label="Annuler"
            className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
          >
            <Undo2 size={16} />
          </button>
        </Tip>
        <Tip label="Retablir (Ctrl+Shift+Z)">
          <button
            onClick={handleRedo}
            aria-label="Retablir"
            className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
          >
            <Redo2 size={16} />
          </button>
        </Tip>
      </div>

      <div className="w-px h-5 bg-slate-200 dark:bg-slate-600" />

      {/* --- Zoom --- */}
      <div className="flex items-center gap-1">
        <Tip label="Zoom arriere">
          <button
            onClick={() => zoomBy(0.8)}
            aria-label="Zoom arriere"
            className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
          >
            <ZoomOut size={16} />
          </button>
        </Tip>
        <span className="text-xs text-slate-500 dark:text-slate-400 w-10 text-center tabular-nums">
          {Math.round(zoom * 100)}%
        </span>
        <Tip label="Zoom avant">
          <button
            onClick={() => zoomBy(1.25)}
            aria-label="Zoom avant"
            className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
          >
            <ZoomIn size={16} />
          </button>
        </Tip>
        <Tip label="Ajuster a l'ecran">
          <button
            onClick={fitToScreen}
            aria-label="Ajuster a l'ecran"
            className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
          >
            <Maximize2 size={16} />
          </button>
        </Tip>
      </div>

      <div className="w-px h-5 bg-slate-200 dark:bg-slate-600" />

      {/* --- Legend toggle --- */}
      <Tip label="Legende">
        <button
          onClick={() => setShowLegend(!showLegend)}
          aria-label="Toggle legende"
          className={`p-1.5 rounded transition-colors cursor-pointer ${
            showLegend
              ? "bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400"
              : "hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400"
          }`}
        >
          <Info size={16} />
        </button>
      </Tip>

      {/* --- Share --- */}
      <Tip label="Partager">
        <button
          onClick={() => setShareOpen(true)}
          aria-label="Partager"
          className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer"
        >
          <Share2 size={16} />
        </button>
      </Tip>

      {/* Spacer */}
      <div className="flex-1" />

      {/* --- Download (si image generee) --- */}
      {generatedImageUrl && (
        <Tip label="Telecharger l'image">
          <button
            onClick={handleDownload}
            aria-label="Telecharger l'image"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 transition-colors cursor-pointer"
          >
            <Download size={14} />
            Download
          </button>
        </Tip>
      )}

      {/* --- Export --- */}
      <ExportButton />

      {/* --- SharePanel modal --- */}
      <SharePanel isOpen={shareOpen} onClose={() => setShareOpen(false)} />
    </div>
  );
}
