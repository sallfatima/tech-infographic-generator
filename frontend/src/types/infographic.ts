/**
 * Types TypeScript — miroir exact des Pydantic models Python.
 * Source : backend/models/infographic.py
 *
 * RÈGLE : chaque modification de infographic.py doit être reflétée ici.
 */

// ─── Enums ──────────────────────────────────────────────────────────

export const InfographicType = {
  ARCHITECTURE: "architecture",
  FLOWCHART: "flowchart",
  COMPARISON: "comparison",
  PROCESS: "process",
  CONCEPT_MAP: "concept_map",
  INFOGRAPHIC: "infographic",
  PIPELINE: "pipeline",
  TIMELINE: "timeline",
  MULTI_AGENT: "multi_agent",
  RAG_PIPELINE: "rag_pipeline",
} as const;
export type InfographicType =
  (typeof InfographicType)[keyof typeof InfographicType];

export const ConnectionStyle = {
  ARROW: "arrow",
  DASHED_ARROW: "dashed_arrow",
  BIDIRECTIONAL: "bidirectional",
  LINE: "line",
  CURVED_ARROW: "curved_arrow",
  CURVED_DASHED: "curved_dashed",
} as const;
export type ConnectionStyle =
  (typeof ConnectionStyle)[keyof typeof ConnectionStyle];

export const NodeShape = {
  ROUNDED_RECT: "rounded_rect",
  RECTANGLE: "rectangle",
  CIRCLE: "circle",
  DIAMOND: "diamond",
  CYLINDER: "cylinder",
  HEXAGON: "hexagon",
  CLOUD: "cloud",
  PARALLELOGRAM: "parallelogram",
  PERSON: "person",
} as const;
export type NodeShape = (typeof NodeShape)[keyof typeof NodeShape];

export const IconName = {
  DATABASE: "database",
  SERVER: "server",
  CLOUD: "cloud",
  USER: "user",
  LOCK: "lock",
  API: "api",
  NETWORK: "network",
  CODE: "code",
  BRAIN: "brain",
  CHART: "chart",
  GEAR: "gear",
  LIGHTNING: "lightning",
  CONTAINER: "container",
  QUEUE: "queue",
  CACHE: "cache",
  MONITOR: "monitor",
  SHIELD: "shield",
  GLOBE: "globe",
  ARROW_RIGHT: "arrow_right",
  CHECK: "check",
  STAR: "star",
  FOLDER: "folder",
  CPU: "cpu",
  MEMORY: "memory",
  SEARCH: "search",
  FILTER: "filter",
  LAYERS: "layers",
  WORKFLOW: "workflow",
  DOCUMENT: "document",
  PLAY: "play",
  AGENT: "agent",
  RAG: "rag",
  PROMPT: "prompt",
  FINETUNE: "finetune",
  EMBEDDING: "embedding",
  VECTOR_DB: "vector_db",
  LLM: "llm",
  TRANSFORMER: "transformer",
  EVALUATION: "evaluation",
  GUARDRAILS: "guardrails",
  CONTEXT: "context",
  TOOL_USE: "tool_use",
  MCP: "mcp",
  MULTI_AGENT: "multi_agent",
  REASONING: "reasoning",
  PERSON_LAPTOP: "person_laptop",
  CHAT: "chat",
  PIPELINE_ICON: "pipeline_icon",
} as const;
export type IconName = (typeof IconName)[keyof typeof IconName];

// ─── Interfaces ─────────────────────────────────────────────────────

export interface Node {
  id: string;
  label: string;
  description?: string;
  icon?: IconName;
  shape?: NodeShape;
  color?: string;
  layer?: number;
  group?: string;
  zone?: string;
  size?: "small" | "medium" | "large";
}

export interface Connection {
  from_node: string;
  to_node: string;
  label?: string;
  style?: ConnectionStyle;
}

export interface Layer {
  name: string;
  color?: string;
  nodes: string[];
}

export interface ZoneDef {
  name: string;
  color?: string;
  nodes: string[];
}

export interface InfographicData {
  title: string;
  subtitle?: string;
  type: InfographicType;
  nodes: Node[];
  connections: Connection[];
  layers: Layer[];
  zones: ZoneDef[];
  color_scheme: string;
  footer?: string;
  metadata: Record<string, unknown>;
}

// ─── Layout helpers ─────────────────────────────────────────────────

/** Position calculée d'un node sur le canvas SVG. */
export interface NodePosition {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** Map nodeId → position calculée par le layout engine. */
export type LayoutResult = Map<string, NodePosition>;
