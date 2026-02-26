/**
 * Zustand store — state global du diagramme.
 *
 * Phase 3 : ajoute undo/redo (zundo), positions draggables,
 * sélection de node, thème, et layout.
 * PAS de localStorage — tout est en mémoire (règle CLAUDE.md).
 */

import { create } from "zustand";
import { temporal } from "zundo";
import type {
  InfographicData,
  NodePosition,
  LayoutResult,
  Node,
  GenerateMode,
  OutputFormat,
  OutputSize,
  PipelineSummary,
  PipelineStatus,
  ViewMode,
} from "../types/infographic";
import { analyzeText, generateStandard, generatePro } from "../api/client";
import { layoutNodes } from "../lib/layoutEngine";

/** Dimensions du canvas par défaut. */
const CANVAS_W = 1400;
const CANVAS_H = 900;

// ─── State shape ────────────────────────────────────────────────────

interface DiagramState {
  /** Données structurées du diagramme (null = pas encore généré). */
  data: InfographicData | null;

  /** Texte brut saisi par l'utilisateur. */
  inputText: string;

  /** Indicateur de chargement (appel API en cours). */
  isLoading: boolean;

  /** Message d'erreur si l'analyse échoue. */
  error: string | null;

  /** Positions des nodes (draggables). Map sérialisée en objet. */
  positions: Record<string, NodePosition>;

  /** ID du node sélectionné (null = aucun). */
  selectedNodeId: string | null;

  /** Thème actif. */
  themeName: string;

  /** Layout actif. */
  layoutMode: "auto" | "vertical" | "horizontal" | "radial";

  /** Zoom level (1 = 100%). */
  zoom: number;

  /** Pan offset pour le canvas. */
  panOffset: { x: number; y: number };

  // ─── Generate / Pipeline ──────────────────────────────────────

  /** Mode de generation : standard (LLM+PIL) ou pro (multi-agent). */
  generateMode: GenerateMode;

  /** Type d'infographie (null = auto-detect). */
  infographicType: string | null;

  /** Format de sortie. */
  outputFormat: OutputFormat;

  /** Taille de sortie. */
  outputSize: OutputSize;

  /** Statut du pipeline Pro. */
  pipelineStatus: PipelineStatus;

  /** Resume du pipeline Pro apres generation. */
  pipelineSummary: PipelineSummary | null;

  /** URL de l'image generee par le backend. */
  generatedImageUrl: string | null;

  /** Nom du fichier genere. */
  generatedFilename: string | null;

  /** Temps de generation (secondes). */
  generationTime: number | null;

  /** Vue active : SVG interactif ou image PIL. */
  viewMode: ViewMode;

  /** Afficher la vue JSON. */
  showJsonView: boolean;

  /** Theme sombre pour l'app shell. */
  darkAppTheme: boolean;

  /** Afficher la legende dans le canvas. */
  showLegend: boolean;

  // ─── Actions ────────────────────────────────────────────────────

  setInputText: (text: string) => void;
  analyze: (text: string) => Promise<void>;
  setData: (data: InfographicData) => void;

  /** Recalcule les positions depuis les données actuelles. */
  recalcPositions: () => void;

  /** Met à jour la position d'un seul node (drag). */
  updateNodePosition: (nodeId: string, x: number, y: number) => void;

  /** Sélectionne un node. */
  selectNode: (nodeId: string | null) => void;

  /** Met à jour le label d'un node. */
  updateNodeLabel: (nodeId: string, label: string) => void;

  /** Met à jour la description d'un node. */
  updateNodeDescription: (nodeId: string, description: string) => void;

  /** Met à jour la shape d'un node. */
  updateNodeShape: (nodeId: string, shape: string) => void;

  /** Met à jour la couleur d'un node. */
  updateNodeColor: (nodeId: string, color: string) => void;

  /** Met à jour l'icône d'un node. */
  updateNodeIcon: (nodeId: string, icon: string | undefined) => void;

  /** Supprime un node et ses connections. */
  deleteNode: (nodeId: string) => void;

  /** Change le thème. */
  setThemeName: (name: string) => void;

  /** Change le layout. */
  setLayoutMode: (mode: "auto" | "vertical" | "horizontal" | "radial") => void;

  /** Change le zoom. */
  setZoom: (zoom: number) => void;

  /** Zoom in/out par facteur. */
  zoomBy: (factor: number) => void;

  /** Fit to screen (reset zoom + pan). */
  fitToScreen: () => void;

  /** Réinitialise le state. */
  reset: () => void;

  // ─── Generate / Pipeline actions ────────────────────────────────

  setGenerateMode: (mode: GenerateMode) => void;
  setInfographicType: (type: string | null) => void;
  setOutputFormat: (format: OutputFormat) => void;
  setOutputSize: (size: OutputSize) => void;
  setViewMode: (mode: ViewMode) => void;
  setShowJsonView: (show: boolean) => void;
  setDarkAppTheme: (dark: boolean) => void;
  setShowLegend: (show: boolean) => void;

  /** Generation complete : analyse LLM + rendu PIL → image URL. */
  generate: (text: string) => Promise<void>;
}

// ─── Helpers ────────────────────────────────────────────────────────

/** Convertit un Map → objet sérialisable. */
function layoutResultToRecord(map: LayoutResult): Record<string, NodePosition> {
  const obj: Record<string, NodePosition> = {};
  map.forEach((pos, id) => {
    obj[id] = pos;
  });
  return obj;
}

/** Helper pour mettre à jour un node dans le data. */
function updateNode(
  data: InfographicData,
  nodeId: string,
  updater: (node: Node) => Node,
): InfographicData {
  return {
    ...data,
    nodes: data.nodes.map((n) => (n.id === nodeId ? updater(n) : n)),
  };
}

// ─── Store avec undo/redo (zundo temporal) ──────────────────────────

export const useDiagramState = create<DiagramState>()(
  temporal(
    (set, get) => ({
      data: null,
      inputText: "",
      isLoading: false,
      error: null,
      positions: {},
      selectedNodeId: null,
      themeName: "whiteboard",
      layoutMode: "auto" as const,
      zoom: 1,
      panOffset: { x: 0, y: 0 },

      // Generate / Pipeline defaults
      generateMode: "standard" as GenerateMode,
      infographicType: null,
      outputFormat: "png" as OutputFormat,
      outputSize: "1400x900" as OutputSize,
      pipelineStatus: "idle" as PipelineStatus,
      pipelineSummary: null,
      generatedImageUrl: null,
      generatedFilename: null,
      generationTime: null,
      viewMode: "svg" as ViewMode,
      showJsonView: false,
      darkAppTheme: false,
      showLegend: false,

      setInputText: (text) => set({ inputText: text }),

      analyze: async (text) => {
        set({ isLoading: true, error: null });
        try {
          const data = await analyzeText(text);
          const { layoutMode } = get();
          const posMap = layoutNodes(data, CANVAS_W, CANVAS_H, layoutMode);
          set({
            data,
            isLoading: false,
            inputText: text,
            positions: layoutResultToRecord(posMap),
            selectedNodeId: null,
          });
        } catch (e) {
          const message = e instanceof Error ? e.message : "Erreur inconnue";
          set({ isLoading: false, error: message });
        }
      },

      setData: (data) => {
        const { layoutMode } = get();
        const posMap = layoutNodes(data, CANVAS_W, CANVAS_H, layoutMode);
        set({
          data,
          error: null,
          positions: layoutResultToRecord(posMap),
          selectedNodeId: null,
        });
      },

      recalcPositions: () => {
        const { data, layoutMode } = get();
        if (!data) return;
        const posMap = layoutNodes(data, CANVAS_W, CANVAS_H, layoutMode);
        set({ positions: layoutResultToRecord(posMap) });
      },

      updateNodePosition: (nodeId, x, y) => {
        const { positions } = get();
        const old = positions[nodeId];
        if (!old) return;
        set({
          positions: {
            ...positions,
            [nodeId]: { ...old, x, y },
          },
        });
      },

      selectNode: (nodeId) => set({ selectedNodeId: nodeId }),

      updateNodeLabel: (nodeId, label) => {
        const { data } = get();
        if (!data) return;
        set({ data: updateNode(data, nodeId, (n) => ({ ...n, label })) });
      },

      updateNodeDescription: (nodeId, description) => {
        const { data } = get();
        if (!data) return;
        set({
          data: updateNode(data, nodeId, (n) => ({ ...n, description })),
        });
      },

      updateNodeShape: (nodeId, shape) => {
        const { data } = get();
        if (!data) return;
        set({
          data: updateNode(data, nodeId, (n) => ({
            ...n,
            shape: shape as Node["shape"],
          })),
        });
      },

      updateNodeColor: (nodeId, color) => {
        const { data } = get();
        if (!data) return;
        set({ data: updateNode(data, nodeId, (n) => ({ ...n, color })) });
      },

      updateNodeIcon: (nodeId, icon) => {
        const { data } = get();
        if (!data) return;
        set({
          data: updateNode(data, nodeId, (n) => ({
            ...n,
            icon: icon as Node["icon"],
          })),
        });
      },

      deleteNode: (nodeId) => {
        const { data, positions, selectedNodeId } = get();
        if (!data) return;
        const newPositions = { ...positions };
        delete newPositions[nodeId];
        set({
          data: {
            ...data,
            nodes: data.nodes.filter((n) => n.id !== nodeId),
            connections: data.connections.filter(
              (c) => c.from_node !== nodeId && c.to_node !== nodeId,
            ),
          },
          positions: newPositions,
          selectedNodeId: selectedNodeId === nodeId ? null : selectedNodeId,
        });
      },

      setThemeName: (name) => set({ themeName: name }),

      setLayoutMode: (mode) => {
        set({ layoutMode: mode });
        const { data } = get();
        if (data) {
          const posMap = layoutNodes(data, CANVAS_W, CANVAS_H, mode);
          set({ positions: layoutResultToRecord(posMap) });
        }
      },

      setZoom: (zoom) => set({ zoom: Math.max(0.25, Math.min(3, zoom)) }),

      zoomBy: (factor) => {
        const { zoom } = get();
        set({ zoom: Math.max(0.25, Math.min(3, zoom * factor)) });
      },

      fitToScreen: () => set({ zoom: 1, panOffset: { x: 0, y: 0 } }),

      reset: () =>
        set({
          data: null,
          inputText: "",
          error: null,
          isLoading: false,
          positions: {},
          selectedNodeId: null,
          zoom: 1,
          panOffset: { x: 0, y: 0 },
          pipelineStatus: "idle" as PipelineStatus,
          pipelineSummary: null,
          generatedImageUrl: null,
          generatedFilename: null,
          generationTime: null,
        }),

      // ─── Generate / Pipeline actions ──────────────────────────────

      setGenerateMode: (mode) => set({ generateMode: mode }),
      setInfographicType: (type) => set({ infographicType: type }),
      setOutputFormat: (format) => set({ outputFormat: format }),
      setOutputSize: (size) => set({ outputSize: size }),
      setViewMode: (mode) => set({ viewMode: mode }),
      setShowJsonView: (show) => set({ showJsonView: show }),
      setDarkAppTheme: (dark) => set({ darkAppTheme: dark }),
      setShowLegend: (show) => set({ showLegend: show }),

      generate: async (text) => {
        const {
          generateMode,
          infographicType,
          outputFormat,
          outputSize,
          themeName,
        } = get();

        // Parse outputSize → width/height
        const [w, h] = outputSize.split("x").map(Number);
        const width = w ?? CANVAS_W;
        const height = h ?? CANVAS_H;

        set({
          isLoading: true,
          error: null,
          generatedImageUrl: null,
          generatedFilename: null,
          generationTime: null,
          pipelineStatus: generateMode === "pro" ? "researching" : "idle",
          pipelineSummary: null,
        });

        try {
          if (generateMode === "pro") {
            // Mode Pro : pipeline multi-agent
            set({ pipelineStatus: "researching" });
            const result = await generatePro({
              text,
              infographic_type: infographicType ?? undefined,
              theme: themeName,
              width,
              height,
              format: outputFormat,
              enable_research: true,
            });

            const data = result.infographic_data;
            const { layoutMode: lm } = get();
            const posMap = layoutNodes(data, CANVAS_W, CANVAS_H, lm);

            set({
              data,
              isLoading: false,
              inputText: text,
              positions: layoutResultToRecord(posMap),
              selectedNodeId: null,
              generatedImageUrl: result.image_url,
              generatedFilename: result.filename,
              generationTime: result.generation_time,
              pipelineStatus: "completed",
              pipelineSummary: result.pipeline_summary,
              viewMode: "image",
            });
          } else {
            // Mode Standard : LLM + PIL render
            const result = await generateStandard({
              text,
              infographic_type: infographicType ?? undefined,
              theme: themeName,
              width,
              height,
              format: outputFormat,
            });

            const data = result.infographic_data;
            const { layoutMode: lm2 } = get();
            const posMap = layoutNodes(data, CANVAS_W, CANVAS_H, lm2);

            set({
              data,
              isLoading: false,
              inputText: text,
              positions: layoutResultToRecord(posMap),
              selectedNodeId: null,
              generatedImageUrl: result.image_url,
              generatedFilename: result.filename,
              generationTime: result.generation_time,
              pipelineStatus: "completed",
              viewMode: "image",
            });
          }
        } catch (e) {
          const message = e instanceof Error ? e.message : "Erreur inconnue";
          set({
            isLoading: false,
            error: message,
            pipelineStatus: "failed",
          });
        }
      },
    }),
    {
      partialize: (state) => {
        const { isLoading, error, inputText, ...rest } = state;
        void isLoading; void error; void inputText;
        const dataOnly: Record<string, unknown> = {};
        for (const [key, value] of Object.entries(rest)) {
          if (typeof value !== "function") {
            dataOnly[key] = value;
          }
        }
        return dataOnly;
      },
      limit: 50,
    },
  ),
);

// ─── Undo / Redo helpers ────────────────────────────────────────────

export function useTemporalStore() {
  return useDiagramState.temporal;
}
