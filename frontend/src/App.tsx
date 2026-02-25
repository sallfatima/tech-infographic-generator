/**
 * App.tsx — Layout principal de l'application.
 *
 * Layout : TextInput à gauche (1/3) | DiagramCanvas à droite (2/3).
 * Quand aucun diagramme n'est généré, affiche un placeholder.
 */

import { useDiagramState } from "./hooks/useDiagramState";
import TextInput from "./components/Editor/TextInput";
import DiagramCanvas from "./components/Diagram/DiagramCanvas";

function App() {
  const { data } = useDiagramState();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b border-slate-200 bg-white">
        <div className="flex items-center gap-2">
          <svg className="w-7 h-7 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M9 9h6M9 13h4M9 17h2" />
          </svg>
          <h1 className="text-lg font-bold text-slate-800">
            Tech Infographic Generator
          </h1>
        </div>
        <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
          Phase 1 — SVG basique
        </span>
      </header>

      {/* Main content */}
      <main className="flex flex-1 overflow-hidden">
        {/* Panneau gauche — TextInput */}
        <aside className="w-[380px] min-w-[320px] border-r border-slate-200 bg-slate-50 p-4 overflow-y-auto">
          <TextInput />
        </aside>

        {/* Panneau droit — DiagramCanvas */}
        <section className="flex-1 p-6 overflow-auto bg-slate-100/50 flex items-center justify-center">
          {data ? (
            <DiagramCanvas data={data} />
          ) : (
            <EmptyState />
          )}
        </section>
      </main>
    </div>
  );
}

/** Placeholder quand aucun diagramme n'a été généré. */
function EmptyState() {
  return (
    <div className="flex flex-col items-center gap-4 text-center max-w-md">
      {/* Icône placeholder */}
      <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
        <svg className="w-12 h-12 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2" y="2" width="20" height="20" rx="3" strokeDasharray="4 2" />
          <circle cx="8" cy="8" r="2" />
          <circle cx="16" cy="8" r="2" />
          <circle cx="12" cy="16" r="2" />
          <path d="M8 10v4l4 2M16 10v4l-4 2" />
        </svg>
      </div>

      <h2 className="text-lg font-semibold text-slate-600">
        Pas encore de diagramme
      </h2>

      <p className="text-sm text-slate-400 leading-relaxed">
        Décris un concept technique dans le panneau de gauche et clique
        &quot;Générer&quot; pour créer une infographie interactive.
      </p>

      <div className="flex flex-wrap gap-2 justify-center mt-2">
        {["Kubernetes", "RAG Pipeline", "System Design", "LLM Training"].map(
          (tag) => (
            <span
              key={tag}
              className="px-3 py-1 bg-white text-xs text-slate-500 rounded-full border border-slate-200"
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
