/**
 * SharePanel — Modal de partage avec copie JSON / URL / SVG.
 *
 * 3 boutons de copie :
 * - Copier JSON : serialize InfographicData → clipboard
 * - Copier URL : base64 encode les data en param URL (warning si > 2000 chars)
 * - Copier SVG : capture le DOM SVG du canvas → clipboard
 *
 * Feedback "Copie !" avec state local + setTimeout 2s.
 * Dark mode aware, ferme au clic sur le backdrop ou bouton X.
 */

import { useState, useCallback, useEffect } from "react";
import { Copy, Link, Code, Check, X } from "lucide-react";
import { useDiagramState } from "../../hooks/useDiagramState";

interface SharePanelProps {
  isOpen: boolean;
  onClose: () => void;
}

type CopiedKey = "json" | "url" | "svg" | null;

export default function SharePanel({ isOpen, onClose }: SharePanelProps) {
  const data = useDiagramState((s) => s.data);
  const [copied, setCopied] = useState<CopiedKey>(null);

  // Reset copied state quand le panel s'ouvre
  useEffect(() => {
    if (isOpen) setCopied(null);
  }, [isOpen]);

  // Fermer avec Escape
  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  const showCopied = useCallback((key: CopiedKey) => {
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  }, []);

  // ─── Copy JSON ──────────────────────────────────────────────────

  const copyJson = useCallback(async () => {
    if (!data) return;
    try {
      const json = JSON.stringify(data, null, 2);
      await navigator.clipboard.writeText(json);
      showCopied("json");
    } catch {
      // Fallback si clipboard API echoue
      console.error("Clipboard write failed");
    }
  }, [data, showCopied]);

  // ─── Copy URL ───────────────────────────────────────────────────

  const copyUrl = useCallback(async () => {
    if (!data) return;
    try {
      const json = JSON.stringify(data);
      const encoded = btoa(unescape(encodeURIComponent(json)));
      const url = `${window.location.origin}${window.location.pathname}?data=${encoded}`;

      await navigator.clipboard.writeText(url);
      showCopied("url");
    } catch {
      console.error("Clipboard write failed");
    }
  }, [data, showCopied]);

  // ─── Copy SVG ───────────────────────────────────────────────────

  const copySvg = useCallback(async () => {
    try {
      const svgEl = document.querySelector("svg");
      if (!svgEl) return;
      const svgString = new XMLSerializer().serializeToString(svgEl);
      await navigator.clipboard.writeText(svgString);
      showCopied("svg");
    } catch {
      console.error("Clipboard write failed");
    }
  }, [showCopied]);

  if (!isOpen) return null;

  // Calcul warning pour URL longue
  const jsonLen = data ? JSON.stringify(data).length : 0;
  const estimatedUrlLen = Math.ceil(jsonLen * 1.37); // base64 overhead
  const urlTooLong = estimatedUrlLen > 2000;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 z-40"
        onClick={onClose}
        aria-hidden
      />

      {/* Modal */}
      <div
        role="dialog"
        aria-label="Panneau de partage"
        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                   w-[360px] bg-white dark:bg-slate-800 rounded-xl
                   shadow-2xl border border-slate-200 dark:border-slate-700
                   z-50 p-5"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">
            Partager
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700
                       text-slate-400 hover:text-slate-600 dark:hover:text-slate-200
                       transition-colors cursor-pointer"
            aria-label="Fermer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Boutons de copie */}
        <div className="space-y-2">
          {/* Copier JSON */}
          <button
            onClick={copyJson}
            disabled={!data}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg
                       border border-slate-200 dark:border-slate-600
                       hover:bg-slate-50 dark:hover:bg-slate-700
                       disabled:opacity-40 disabled:cursor-not-allowed
                       transition-colors cursor-pointer"
          >
            <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/40
                          flex items-center justify-center flex-shrink-0">
              {copied === "json" ? (
                <Check size={16} className="text-green-600 dark:text-green-400" />
              ) : (
                <Copy size={16} className="text-blue-600 dark:text-blue-400" />
              )}
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-slate-700 dark:text-slate-200">
                {copied === "json" ? "Copie !" : "Copier JSON"}
              </div>
              <div className="text-[11px] text-slate-400 dark:text-slate-500">
                Donnees structurees InfographicData
              </div>
            </div>
          </button>

          {/* Copier URL */}
          <button
            onClick={copyUrl}
            disabled={!data}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg
                       border border-slate-200 dark:border-slate-600
                       hover:bg-slate-50 dark:hover:bg-slate-700
                       disabled:opacity-40 disabled:cursor-not-allowed
                       transition-colors cursor-pointer"
          >
            <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/40
                          flex items-center justify-center flex-shrink-0">
              {copied === "url" ? (
                <Check size={16} className="text-green-600 dark:text-green-400" />
              ) : (
                <Link size={16} className="text-purple-600 dark:text-purple-400" />
              )}
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-slate-700 dark:text-slate-200">
                {copied === "url" ? "Copie !" : "Copier URL"}
              </div>
              <div className="text-[11px] text-slate-400 dark:text-slate-500">
                Lien partageable avec data en base64
              </div>
            </div>
          </button>

          {urlTooLong && (
            <p className="text-[10px] text-amber-600 dark:text-amber-400 px-1">
              Attention : l&apos;URL estimee depasse 2000 caracteres
              (~{estimatedUrlLen} car.) et pourrait ne pas fonctionner dans
              tous les navigateurs.
            </p>
          )}

          {/* Copier SVG */}
          <button
            onClick={copySvg}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg
                       border border-slate-200 dark:border-slate-600
                       hover:bg-slate-50 dark:hover:bg-slate-700
                       transition-colors cursor-pointer"
          >
            <div className="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/40
                          flex items-center justify-center flex-shrink-0">
              {copied === "svg" ? (
                <Check size={16} className="text-green-600 dark:text-green-400" />
              ) : (
                <Code size={16} className="text-green-600 dark:text-green-400" />
              )}
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-slate-700 dark:text-slate-200">
                {copied === "svg" ? "Copie !" : "Copier SVG"}
              </div>
              <div className="text-[11px] text-slate-400 dark:text-slate-500">
                Code SVG brut du canvas actuel
              </div>
            </div>
          </button>
        </div>
      </div>
    </>
  );
}
