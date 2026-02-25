/**
 * Zustand store — state global du diagramme.
 *
 * Gère : InfographicData, loading, erreurs, édition des nodes.
 * PAS de localStorage — tout est en mémoire (règle CLAUDE.md).
 */

import { create } from "zustand";
import type { InfographicData } from "../types/infographic";
import { analyzeText } from "../api/client";

interface DiagramState {
  /** Données structurées du diagramme (null = pas encore généré). */
  data: InfographicData | null;

  /** Texte brut saisi par l'utilisateur. */
  inputText: string;

  /** Indicateur de chargement (appel API en cours). */
  isLoading: boolean;

  /** Message d'erreur si l'analyse échoue. */
  error: string | null;

  // ─── Actions ────────────────────────────────────────────────────

  /** Met à jour le texte de saisie. */
  setInputText: (text: string) => void;

  /** Lance l'analyse via /api/analyze. */
  analyze: (text: string) => Promise<void>;

  /** Injecte directement un InfographicData (pour les tests). */
  setData: (data: InfographicData) => void;

  /** Met à jour le label d'un node. */
  updateNodeLabel: (nodeId: string, label: string) => void;

  /** Met à jour la description d'un node. */
  updateNodeDescription: (nodeId: string, description: string) => void;

  /** Réinitialise le state. */
  reset: () => void;
}

export const useDiagramState = create<DiagramState>((set, get) => ({
  data: null,
  inputText: "",
  isLoading: false,
  error: null,

  setInputText: (text) => set({ inputText: text }),

  analyze: async (text) => {
    set({ isLoading: true, error: null });
    try {
      const data = await analyzeText(text);
      set({ data, isLoading: false, inputText: text });
    } catch (e) {
      const message = e instanceof Error ? e.message : "Erreur inconnue";
      set({ isLoading: false, error: message });
    }
  },

  setData: (data) => set({ data, error: null }),

  updateNodeLabel: (nodeId, label) => {
    const { data } = get();
    if (!data) return;
    set({
      data: {
        ...data,
        nodes: data.nodes.map((n) =>
          n.id === nodeId ? { ...n, label } : n,
        ),
      },
    });
  },

  updateNodeDescription: (nodeId, description) => {
    const { data } = get();
    if (!data) return;
    set({
      data: {
        ...data,
        nodes: data.nodes.map((n) =>
          n.id === nodeId ? { ...n, description } : n,
        ),
      },
    });
  },

  reset: () => set({ data: null, inputText: "", error: null, isLoading: false }),
}));
