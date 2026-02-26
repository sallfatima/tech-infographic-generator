/**
 * NodeEditor — Panneau de propriétés pour le node sélectionné.
 *
 * Phase 3 : édition label, description, shape, icon, couleur, suppression.
 * S'affiche en sidebar quand selectedNodeId !== null.
 */

import { useState } from "react";
import { useDiagramState } from "../../hooks/useDiagramState";
import {
  X, Trash2, Square, Circle, Hexagon, Cloud, Diamond, Database,
  Server, User, Brain, Zap, Code, Settings, Lock, Shield, Search,
  BarChart3, Bot, GitBranch, FileText, Network, Globe, Monitor,
  Container, HardDrive, Cpu, MemoryStick, Filter, Layers, Play,
  Star, Folder, ChevronDown, MessageSquare, Target, BookOpen,
  Plug, Users, Lightbulb, ArrowRight, CircleCheck, Cylinder,
} from "lucide-react";
import type { ComponentType } from "react";

/** Map icon name → lucide-react component (closest match). */
const LUCIDE_MAP: Record<string, ComponentType<{ size?: number }>> = {
  database: Database,
  server: Server,
  cloud: Cloud,
  user: User,
  brain: Brain,
  api: Zap,
  code: Code,
  gear: Settings,
  lightning: Zap,
  container: Container,
  lock: Lock,
  shield: Shield,
  search: Search,
  chart: BarChart3,
  llm: Brain,
  agent: Bot,
  workflow: GitBranch,
  document: FileText,
  network: Network,
  globe: Globe,
  monitor: Monitor,
  cache: HardDrive,
  queue: Layers,
  cpu: Cpu,
  memory: MemoryStick,
  filter: Filter,
  layers: Layers,
  play: Play,
  star: Star,
  folder: Folder,
  arrow_right: ArrowRight,
  check: CircleCheck,
  prompt: MessageSquare,
  finetune: Target,
  embedding: Layers,
  vector_db: Database,
  transformer: GitBranch,
  evaluation: BarChart3,
  guardrails: Shield,
  context: BookOpen,
  tool_use: Settings,
  mcp: Plug,
  multi_agent: Users,
  reasoning: Lightbulb,
  rag: Search,
};

/** Shapes disponibles avec label et composant lucide. */
const SHAPES: { value: string; label: string; Icon: ComponentType<{ size?: number }> }[] = [
  { value: "rounded_rect", label: "Rectangle", Icon: Square },
  { value: "circle", label: "Cercle", Icon: Circle },
  { value: "cylinder", label: "Cylindre", Icon: Cylinder },
  { value: "hexagon", label: "Hexagone", Icon: Hexagon },
  { value: "cloud", label: "Cloud", Icon: Cloud },
  { value: "diamond", label: "Losange", Icon: Diamond },
];

/** Toutes les icônes disponibles. */
const ICONS: { value: string; label: string }[] = [
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
  { value: "globe", label: "Globe" },
  { value: "monitor", label: "Monitor" },
  { value: "cache", label: "Cache" },
  { value: "cpu", label: "CPU" },
  { value: "memory", label: "Memory" },
  { value: "filter", label: "Filter" },
  { value: "layers", label: "Layers" },
  { value: "play", label: "Play" },
  { value: "star", label: "Star" },
  { value: "folder", label: "Folder" },
  { value: "prompt", label: "Prompt" },
  { value: "finetune", label: "Finetune" },
  { value: "embedding", label: "Embedding" },
  { value: "vector_db", label: "Vector DB" },
  { value: "transformer", label: "Transformer" },
  { value: "evaluation", label: "Evaluation" },
  { value: "guardrails", label: "Guardrails" },
  { value: "context", label: "Context" },
  { value: "tool_use", label: "Tool Use" },
  { value: "mcp", label: "MCP" },
  { value: "multi_agent", label: "Multi-Agent" },
  { value: "reasoning", label: "Reasoning" },
  { value: "rag", label: "RAG" },
];

/** Couleurs prédéfinies. */
const COLORS = [
  "#E3F2FD", "#FFF3E0", "#E8F5E9", "#FCE4EC",
  "#F3E5F5", "#E0F7FA", "#FFF9C4", "#F1F8E9",
  "#FFCDD2", "#D1C4E9", "#B2EBF2", "#DCEDC8",
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

  const [iconExpanded, setIconExpanded] = useState(false);

  if (!selectedNodeId || !data) return null;

  const node = data.nodes.find((n) => n.id === selectedNodeId);
  if (!node) return null;

  // Icônes à afficher : collapsed = 12 premières, expanded = toutes
  const visibleIcons = iconExpanded ? ICONS : ICONS.slice(0, 13);

  return (
    <div className="w-[280px] min-w-[240px] border-l border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
          Proprietes du node
        </h3>
        <button
          onClick={() => selectNode(null)}
          className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-pointer"
          title="Fermer"
          aria-label="Fermer le panneau"
        >
          <X size={16} />
        </button>
      </div>

      <div className="flex flex-col gap-4">
        {/* --- Label --- */}
        <div>
          <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
            Label
          </label>
          <input
            type="text"
            value={node.label}
            onChange={(e) => updateNodeLabel(node.id, e.target.value)}
            className="w-full px-3 py-1.5 text-sm rounded border border-slate-200 dark:border-slate-600
                       bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100
                       focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
          />
        </div>

        {/* --- Description --- */}
        <div>
          <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
            Description
          </label>
          <textarea
            value={node.description ?? ""}
            onChange={(e) => updateNodeDescription(node.id, e.target.value)}
            rows={3}
            className="w-full px-3 py-1.5 text-sm rounded border border-slate-200 dark:border-slate-600
                       bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 resize-none
                       focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400"
          />
        </div>

        {/* --- Shape --- */}
        <div>
          <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
            Forme
          </label>
          <div className="grid grid-cols-3 gap-1.5">
            {SHAPES.map((s) => {
              const ShapeIcon = s.Icon;
              return (
                <button
                  key={s.value}
                  onClick={() => updateNodeShape(node.id, s.value)}
                  className={`flex flex-col items-center gap-0.5 p-2 rounded border text-xs transition-colors cursor-pointer ${
                    (node.shape ?? "rounded_rect") === s.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                      : "border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
                  }`}
                >
                  <ShapeIcon size={18} />
                  <span className="text-[10px]">{s.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* --- Icon (grille visuelle) --- */}
        <div>
          <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
            Icone
          </label>
          <div className="grid grid-cols-4 gap-1.5 max-h-[240px] overflow-y-auto">
            {visibleIcons.map((ic) => {
              const LucideIcon = ic.value ? LUCIDE_MAP[ic.value] : null;
              const isSelected = (node.icon ?? "") === ic.value;
              return (
                <button
                  key={ic.value || "__none__"}
                  onClick={() => updateNodeIcon(node.id, ic.value || undefined)}
                  className={`flex flex-col items-center gap-0.5 p-1.5 rounded border text-xs transition-colors cursor-pointer ${
                    isSelected
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                      : "border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
                  }`}
                  title={ic.label}
                >
                  {LucideIcon ? (
                    <LucideIcon size={16} />
                  ) : (
                    <X size={16} className="text-slate-400" />
                  )}
                  <span className="text-[9px] truncate w-full text-center">
                    {ic.label}
                  </span>
                </button>
              );
            })}
          </div>
          {ICONS.length > 13 && (
            <button
              onClick={() => setIconExpanded(!iconExpanded)}
              className="flex items-center gap-1 mt-1.5 text-[10px] text-blue-500 hover:text-blue-600 dark:text-blue-400 cursor-pointer"
            >
              <ChevronDown
                size={12}
                className={`transition-transform ${iconExpanded ? "rotate-180" : ""}`}
              />
              {iconExpanded
                ? "Voir moins"
                : `Voir les ${ICONS.length - 13} autres`}
            </button>
          )}
        </div>

        {/* --- Couleur --- */}
        <div>
          <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
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
                    : "border-slate-200 dark:border-slate-600 hover:scale-105"
                }`}
                style={{ backgroundColor: color }}
                title={color}
              />
            ))}
          </div>
          <input
            type="color"
            value={node.color ?? "#E3F2FD"}
            onChange={(e) => updateNodeColor(node.id, e.target.value)}
            className="mt-2 w-full h-8 rounded border border-slate-200 dark:border-slate-600 cursor-pointer"
          />
        </div>

        {/* --- Supprimer --- */}
        <button
          onClick={() => {
            deleteNode(node.id);
            selectNode(null);
          }}
          className="flex items-center justify-center gap-2 px-4 py-2 mt-2
                     bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm font-medium rounded-lg
                     border border-red-200 dark:border-red-800 hover:bg-red-100 dark:hover:bg-red-900/40
                     transition-colors cursor-pointer"
        >
          <Trash2 size={16} />
          Supprimer ce node
        </button>
      </div>
    </div>
  );
}
