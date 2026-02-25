/**
 * Client API pour communiquer avec le backend FastAPI.
 *
 * En dev, le proxy Vite redirige /api → http://localhost:8000.
 * En prod, les requêtes vont directement au même domaine.
 */

import type { InfographicData } from "../types/infographic";

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
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      (err as { detail?: string }).detail ?? "Erreur analyse API",
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
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      (err as { detail?: string }).detail ?? "Erreur export PNG",
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
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      (err as { detail?: string }).detail ?? "Erreur export GIF",
    );
  }

  return res.blob();
}
