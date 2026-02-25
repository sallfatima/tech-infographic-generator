/**
 * App.tsx — Layout principal de l'application.
 *
 * Feature/full-frontend : integre toutes les fonctionnalites
 * de l'ancien frontend (mode Standard/Pro, pipeline progress,
 * image preview, JSON view, dark theme).
 */

import { useEffect } from "react";
import { useDiagramState, useTemporalStore } from "./hooks/useDiagramState";
import { useExport } from "./hooks/useExport";
import TextInput from "./components/Editor/TextInput";
import DiagramCanvas from "./components/Diagram/DiagramCanvas";
import Toolbar from "./components/Editor/Toolbar";
import NodeEditor from "./components/Editor/NodeEditor";
import { PipelineProgress } from "./components/Pipeline/PipelineProgress";

function App() {
  const data = useDiagramState((s) => s.data);
  const selectedNodeId = useDiagramState((s) => s.selectedNodeId);
  const selectNode = useDiagramState((s) => s.selectNode);
  const deleteNode = useDiagramState((s) => s.deleteNode);
  const darkAppTheme = useDiagramState((s) => s.darkAppTheme);
  const setDarkAppTheme = useDiagramState((s) => s.setDarkAppTheme);
  const viewMode = useDiagramState((s) => s.viewMode);
  const showJsonView = useDiagramState((s) => s.showJsonView);
  const generatedImageUrl = useDiagramState((s) => s.generatedImageUrl);
  const generatedFilename = useDiagramState((s) => s.generatedFilename);
  const generationTime = useDiagramState((s) => s.generationTime);
  const temporal = useTemporalStore();
  const { exportSvg } = useExport();

  // ─── Raccourcis clavier globaux ──────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      if ((e.ctrlKey || e.metaKey) && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        temporal.getState().undo();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "z" && e.shiftKey) {
        e.preventDefault();
        temporal.getState().redo();
      }
      if ((e.key === "Delete" || e.key === "Backspace") && selectedNodeId) {
        e.preventDefault();
        deleteNode(selectedNodeId);
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        exportSvg();
      }
      if (e.key === "Escape") {
        selectNode(null);
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [selectedNodeId, selectNode, deleteNode, temporal, exportSvg]);

  // ─── Decide what to show in the right panel ──────────────────────
  const renderRightPanel = () => {
    // Vue JSON
    if (showJsonView && data) {
      return <JsonView />;
    }
    // Vue image PIL
    if (viewMode === "image" && generatedImageUrl) {
      return (
        <ImagePreview
          imageUrl={generatedImageUrl}
          filename={generatedFilename}
          generationTime={generationTime}
        />
      );
    }
    // Vue SVG interactive
    if (data) {
      return <DiagramCanvas />;
    }
    // Etat vide
    return <EmptyState />;
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkAppTheme ? "dark" : ""}`}>
      <div className="min-h-screen flex flex-col bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 transition-colors">
        {/* Header */}
        <header className="flex items-center gap-3 px-6 py-3 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
          <div className="flex items-center gap-2">
            <svg className="w-7 h-7 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M9 9h6M9 13h4M9 17h2" />
            </svg>
            <h1 className="text-lg font-bold">
              Tech Infographic Generator
            </h1>
          </div>
          <span className="text-xs text-slate-400 bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded-full">
            v2.0
          </span>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Dark theme toggle */}
          <button
            onClick={() => setDarkAppTheme(!darkAppTheme)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title={darkAppTheme ? "Mode clair" : "Mode sombre"}
          >
            {darkAppTheme ? (
              <svg className="w-5 h-5 text-yellow-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="5" />
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
              </svg>
            )}
          </button>
        </header>

        {/* Pipeline Progress (visible en mode Pro) */}
        <PipelineProgress />

        {/* Toolbar */}
        <Toolbar />

        {/* Main content */}
        <main className="flex flex-col md:flex-row flex-1 overflow-hidden">
          {/* Panneau gauche — TextInput + NodeEditor */}
          <aside className="w-full md:w-[380px] md:min-w-[320px] border-b md:border-b-0 md:border-r border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-4 overflow-y-auto">
            <TextInput />
            {selectedNodeId && data && <NodeEditor />}
          </aside>

          {/* Panneau droit — DiagramCanvas / ImagePreview / JsonView */}
          <section className="flex-1 p-4 md:p-6 overflow-auto bg-slate-100/50 dark:bg-slate-900 flex items-center justify-center">
            {renderRightPanel()}
          </section>
        </main>
      </div>
    </div>
  );
}

// ─── ImagePreview (inline) ───────────────────────────────────────────

interface ImagePreviewProps {
  imageUrl: string;
  filename: string | null;
  generationTime: number | null;
}

function ImagePreview({ imageUrl, filename, generationTime }: ImagePreviewProps) {
  const handleDownload = () => {
    const a = document.createElement("a");
    a.href = imageUrl;
    a.download = filename ?? "infographic.png";
    a.click();
  };

  return (
    <div className="flex flex-col items-center gap-4 w-full max-w-4xl">
      {/* Image */}
      <div className="rounded-xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <img
          src={imageUrl}
          alt="Generated infographic"
          className="max-w-full h-auto"
        />
      </div>

      {/* Info bar */}
      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
        {filename && <span>{filename}</span>}
        {generationTime != null && <span>{generationTime}s</span>}
        <button
          onClick={handleDownload}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs font-medium"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
          </svg>
          Telecharger
        </button>
      </div>
    </div>
  );
}

// ─── JsonView (inline) ───────────────────────────────────────────────

function JsonView() {
  const data = useDiagramState((s) => s.data);

  const handleCopy = () => {
    if (data) {
      navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    }
  };

  if (!data) return null;

  return (
    <div className="w-full max-w-4xl">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-300">
          InfographicData JSON
        </h3>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="9" y="9" width="13" height="13" rx="2" />
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
          </svg>
          Copier
        </button>
      </div>
      <pre className="p-4 rounded-lg bg-slate-800 dark:bg-slate-950 text-green-400 text-xs font-mono overflow-auto max-h-[70vh] border border-slate-700">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

// ─── EmptyState ──────────────────────────────────────────────────────

function EmptyState() {
  return (
    <div className="flex flex-col items-center gap-4 text-center max-w-md">
      <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 flex items-center justify-center">
        <svg className="w-12 h-12 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2" y="2" width="20" height="20" rx="3" strokeDasharray="4 2" />
          <circle cx="8" cy="8" r="2" />
          <circle cx="16" cy="8" r="2" />
          <circle cx="12" cy="16" r="2" />
          <path d="M8 10v4l4 2M16 10v4l-4 2" />
        </svg>
      </div>

      <h2 className="text-lg font-semibold text-slate-600 dark:text-slate-300">
        Pas encore de diagramme
      </h2>

      <p className="text-sm text-slate-400 leading-relaxed">
        Decris un concept technique dans le panneau de gauche et clique
        &quot;Generer&quot; pour creer une infographie interactive.
      </p>

      <div className="flex flex-wrap gap-2 justify-center mt-2">
        {["Kubernetes", "RAG Pipeline", "System Design", "LLM Training"].map(
          (tag) => (
            <span
              key={tag}
              className="px-3 py-1 bg-white dark:bg-slate-800 text-xs text-slate-500 dark:text-slate-400 rounded-full border border-slate-200 dark:border-slate-700"
            >
              {tag}
            </span>
          ),
        )}
      </div>
    </div>
  );
}

export default App;
