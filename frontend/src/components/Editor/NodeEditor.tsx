/**
 * NodeEditor — Panneau de propriétés pour le node sélectionné.
 *
 * Phase 3 : édition label, description, shape, icon, couleur, suppression.
 * S'affiche en sidebar droite quand selectedNodeId !== null.
 */

import { useDiagramState } from "../../hooks/useDiagramState";

/** Shapes disponibles avec label et emoji. */
const SHAPES = [
  { value: "rounded_rect", label: "Rectangle", icon: "▭" },
  { value: "circle", label: "Cercle", icon: "◯" },
  { value: "cylinder", label: "Cylindre", icon: "⌓" },
  { value: "hexagon", label: "Hexagone", icon: "⬡" },
  { value: "cloud", label: "Cloud", icon: "☁" },
  { value: "diamond", label: "Losange", icon: "◇" },
] as const;

/** Icônes disponibles (subset des plus utilisées). */
const ICONS = [
  { value: "", label: "Aucune" },
  { value: "database", label: "Database" },
  { value: "server", label: "Server" },
  { value: "cloud", label: "Cloud" },
  { value: "user", label: "User" },
  { value: "brain", label: "Brain" },
  { value: "api", label: "API" },
  { value: "code", label: "Code" },
  { value: "gear", label: "Gear" },
  { value: "lightning", label: "Lightning" },
  { value: "container", label: "Container" },
  { value: "lock", label: "Lock" },
  { value: "shield", label: "Shield" },
  { value: "search", label: "Search" },
  { value: "chart", label: "Chart" },
  { value: "llm", label: "LLM" },
  { value: "agent", label: "Agent" },
  { value: "workflow", label: "Workflow" },
  { value: "document", label: "Document" },
  { value: "network", label: "Network" },
] as const;

/** Couleurs prédéfinies. */
const COLORS = [
  "#E3F2FD",
  "#FFF3E0",
  "#E8F5E9",
  "#FCE4EC",
  "#F3E5F5",
  "#E0F7FA",
  "#FFF9C4",
  "#F1F8E9",
  "#FFCDD2",
  "#D1C4E9",
  "#B2EBF2",
  "#DCEDC8",
];

export default function NodeEditor() {
  const selectedNodeId = useDiagramState((s) => s.selectedNodeId);
  const data = useDiagramState((s) => s.data);
  const selectNode = useDiagramState((s) => s.selectNode);
  const updateNodeLabel = useDiagramState((s) => s.updateNodeLabel);
  const updateNodeDescription = useDiagramState((s) => s.updateNodeDescription);
  const updateNodeShape = useDiagramState((s) => s.updateNodeShape);
  const updateNodeColor = useDiagramState((s) => s.updateNodeColor);
  const updateNodeIcon = useDiagramState((s) => s.updateNodeIcon);
  const deleteNode = useDiagramState((s) => s.deleteNode);

  if (!selectedNodeId || !data) return null;

  const node = data.nodes.find((n) => n.id === selectedNodeId);
  if (!node) return null;

  return (
    <aside className="w-[280px] min-w-[240px] border-l border-slate-200 bg-white p-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-700">
          Propriétés du node
        </h3>
        <button
          onClick={() => selectNode(null)}
          className="p-1 rounded hover:bg-slate-100 text-slate-400 cursor-pointer"
          title="Fermer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex flex-col gap-4">
        {/* ─── Label ─── */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Label
          </label>
          <input
            type="text"
            value={node.label}
            onChange={(e) => updateNodeLabel(node.id, e.target.value)}
            className="w-full px-3 py-1.5 text-sm rounded border border-slate-200
                       focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
          />
        </div>

        {/* ─── Description ─── */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Description
          </label>
          <textarea
            value={node.description ?? ""}
            onChange={(e) =>
              updateNodeDescription(node.id, e.target.value)
            }
            rows={3}
            className="w-full px-3 py-1.5 text-sm rounded border border-slate-200 resize-none
                       focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
          />
        </div>

        {/* ─── Shape ─── */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Forme
          </label>
          <div className="grid grid-cols-3 gap-1.5">
            {SHAPES.map((s) => (
              <button
                key={s.value}
                onClick={() => updateNodeShape(node.id, s.value)}
                className={`flex flex-col items-center gap-0.5 p-2 rounded border text-xs transition-colors cursor-pointer ${
                  (node.shape ?? "rounded_rect") === s.value
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                <span className="text-base">{s.icon}</span>
                <span className="text-[10px]">{s.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* ─── Icon ─── */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Icône
          </label>
          <select
            value={node.icon ?? ""}
            onChange={(e) =>
              updateNodeIcon(node.id, e.target.value || undefined)
            }
            className="w-full px-3 py-1.5 text-sm rounded border border-slate-200
                       focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400
                       cursor-pointer"
          >
            {ICONS.map((ic) => (
              <option key={ic.value} value={ic.value}>
                {ic.label}
              </option>
            ))}
          </select>
        </div>

        {/* ─── Couleur ─── */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Couleur
          </label>
          <div className="grid grid-cols-6 gap-1.5">
            {COLORS.map((color) => (
              <button
                key={color}
                onClick={() => updateNodeColor(node.id, color)}
                className={`w-8 h-8 rounded-md border-2 transition-all cursor-pointer ${
                  node.color === color
                    ? "border-blue-500 scale-110"
                    : "border-slate-200 hover:scale-105"
                }`}
                style={{ backgroundColor: color }}
                title={color}
              />
            ))}
          </div>
          {/* Custom color input */}
          <input
            type="color"
            value={node.color ?? "#E3F2FD"}
            onChange={(e) => updateNodeColor(node.id, e.target.value)}
            className="mt-2 w-full h-8 rounded border border-slate-200 cursor-pointer"
          />
        </div>

        {/* ─── Supprimer ─── */}
        <button
          onClick={() => {
            deleteNode(node.id);
            selectNode(null);
          }}
          className="flex items-center justify-center gap-2 px-4 py-2 mt-2
                     bg-red-50 text-red-600 text-sm font-medium rounded-lg
                     border border-red-200 hover:bg-red-100
                     transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18M8 6V4h8v2M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6" />
            <path d="M10 11v6M14 11v6" />
          </svg>
          Supprimer ce node
        </button>
      </div>
    </aside>
  );
}
