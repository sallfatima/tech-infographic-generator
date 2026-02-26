/**
 * Client API pour communiquer avec le backend FastAPI.
 *
 * En dev, le proxy Vite redirige /api → http://localhost:8000.
 * En prod, les requêtes vont directement au même domaine.
 */

import type {
  InfographicData,
  GenerateResponse,
  ProGenerateResponse,
} from "../types/infographic";

const API_BASE = "/api";

// ─── Analyze ────────────────────────────────────────────────────────

interface AnalyzeResponse {
  data: InfographicData;
  analysis_time: number;
}

/**
 * Envoie du texte brut au backend → reçoit InfographicData JSON.
 * Le LLM (Claude/OpenAI) parse le texte et génère la structure.
 */
export async function analyzeText(
  text: string,
  infographicType?: string,
): Promise<InfographicData> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, infographic_type: infographicType }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = (err as { detail?: string } | null)?.detail;
    throw new Error(
      detail ?? `Erreur analyse API (HTTP ${res.status})`,
    );
  }

  const json = (await res.json()) as AnalyzeResponse;
  return json.data;
}

// ─── Export PNG ──────────────────────────────────────────────────────

/**
 * Envoie InfographicData au backend → reçoit un PNG en Blob.
 * Utilisé pour le téléchargement de l'infographie finale.
 */
export async function exportPng(
  data: InfographicData,
  theme: string = "whiteboard",
  width: number = 1400,
  height: number = 900,
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/png`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      infographic_data: data,
      theme,
      width,
      height,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = (err as { detail?: string } | null)?.detail;
    throw new Error(
      detail ?? `Erreur export PNG (HTTP ${res.status})`,
    );
  }

  return res.blob();
}

// ─── Export GIF ──────────────────────────────────────────────────────

/**
 * Envoie InfographicData au backend → reçoit un GIF animé en Blob.
 */
export async function exportGif(
  data: InfographicData,
  theme: string = "whiteboard",
  width: number = 1400,
  height: number = 900,
  frameDuration: number = 500,
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/export/gif`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      infographic_data: data,
      theme,
      width,
      height,
      frame_duration: frameDuration,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = (err as { detail?: string } | null)?.detail;
    throw new Error(
      detail ?? `Erreur export GIF (HTTP ${res.status})`,
    );
  }

  return res.blob();
}

// ─── Generate Standard ───────────────────────────────────────────────

export interface GenerateParams {
  text: string;
  infographic_type?: string;
  theme?: string;
  width?: number;
  height?: number;
  format?: "png" | "gif";
  frame_duration?: number;
}

/**
 * Mode Standard : Analyse LLM + rendu PIL en une seule requete.
 * Retourne l'URL de l'image generee + InfographicData.
 */
export async function generateStandard(
  params: GenerateParams,
): Promise<GenerateResponse> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = (err as { detail?: string } | null)?.detail;
    throw new Error(
      detail ?? `Erreur generation standard (HTTP ${res.status})`,
    );
  }

  return (await res.json()) as GenerateResponse;
}

// ─── Generate Pro (Multi-Agent) ──────────────────────────────────────

export interface ProGenerateParams extends GenerateParams {
  enable_research?: boolean;
  enable_quality_check?: boolean;
}

/**
 * Mode Pro : Pipeline multi-agent (Research → Structure → Render).
 * Retourne l'URL de l'image + resume pipeline.
 */
export async function generatePro(
  params: ProGenerateParams,
): Promise<ProGenerateResponse> {
  const res = await fetch(`${API_BASE}/generate-pro`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = (err as { detail?: string } | null)?.detail;
    throw new Error(
      detail ?? `Erreur generation pro (HTTP ${res.status})`,
    );
  }

  return (await res.json()) as ProGenerateResponse;
}
