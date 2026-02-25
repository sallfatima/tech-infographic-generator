/**
 * Themes frontend — miroir des themes Python backend.
 * Source : backend/renderer/themes.py
 *
 * Chaque theme configure : couleurs, roughness Rough.js, fillStyle.
 */

export interface SectionColor {
  fill: string;
  border: string;
  text: string;
}

export interface DiagramTheme {
  name: string;
  bg: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  border: string;
  accent: string;
  accent2: string;
  sectionColors: SectionColor[];
  nodeColors: string[];
  /** Rough.js roughness (0 = clean, 2+ = very rough) */
  roughness: number;
  /** Rough.js fill style */
  fillStyle: "hachure" | "solid" | "cross-hatch" | "zigzag";
  /** Rough.js bowing (waviness of lines) */
  bowing: number;
  /** Use dashed borders */
  dashedBorder: boolean;
  /** Outer border color */
  outerBorderColor: string;
}

export const THEMES: Record<string, DiagramTheme> = {
  whiteboard: {
    name: "Whiteboard",
    bg: "#FFFFFF",
    text: "#1A1A2E",
    textSecondary: "#3D3D5C",
    textMuted: "#5A6B7D",
    border: "#2B7DE9",
    accent: "#2B7DE9",
    accent2: "#E8833A",
    sectionColors: [
      { fill: "#E3F2FD", border: "#2B7DE9", text: "#1565C0" },
      { fill: "#FFF3E0", border: "#E8833A", text: "#BF360C" },
      { fill: "#E8F5E9", border: "#4CAF50", text: "#2E7D32" },
      { fill: "#FCE4EC", border: "#E53935", text: "#C62828" },
      { fill: "#F3E5F5", border: "#9C27B0", text: "#6A1B9A" },
      { fill: "#E0F7FA", border: "#00ACC1", text: "#006064" },
      { fill: "#FFF9C4", border: "#F9A825", text: "#F57F17" },
      { fill: "#F1F8E9", border: "#689F38", text: "#33691E" },
    ],
    nodeColors: [
      "#2B7DE9", "#E8833A", "#4CAF50", "#E53935",
      "#9C27B0", "#00ACC1", "#F9A825", "#689F38",
    ],
    roughness: 1.5,
    fillStyle: "hachure",
    bowing: 2,
    dashedBorder: true,
    outerBorderColor: "#2B7DE9",
  },

  guidebook: {
    name: "AI Guidebook",
    bg: "#FAFBFE",
    text: "#1A1A2E",
    textSecondary: "#3D3D5C",
    textMuted: "#6B7B8D",
    border: "#D8E2F0",
    accent: "#5B8DEF",
    accent2: "#FF7B54",
    sectionColors: [
      { fill: "#EBF3FF", border: "#5B8DEF", text: "#2B5EA7" },
      { fill: "#FFF0EB", border: "#FF7B54", text: "#C44D2B" },
      { fill: "#E8FBF9", border: "#4ECDC4", text: "#2A8A83" },
      { fill: "#F3EEFF", border: "#7C5CFC", text: "#5039B0" },
      { fill: "#FFF8E6", border: "#FFB946", text: "#A07020" },
      { fill: "#FFE8F0", border: "#FF6B9D", text: "#B03A60" },
    ],
    nodeColors: [
      "#5B8DEF", "#FF7B54", "#4ECDC4", "#7C5CFC", "#FFB946", "#FF6B9D",
    ],
    roughness: 0.3,
    fillStyle: "solid",
    bowing: 0.5,
    dashedBorder: false,
    outerBorderColor: "#5B8DEF",
  },

  dark: {
    name: "Dark Modern",
    bg: "#18181B",
    text: "#FAFAFA",
    textSecondary: "#D4D4D8",
    textMuted: "#A1A1AA",
    border: "#3F3F46",
    accent: "#F97316",
    accent2: "#EC4899",
    sectionColors: [
      { fill: "#2D2520", border: "#F97316", text: "#FDBA74" },
      { fill: "#2A2028", border: "#EC4899", text: "#F9A8D4" },
      { fill: "#261F2E", border: "#A855F7", text: "#C4B5FD" },
      { fill: "#1F2028", border: "#38BDF8", text: "#7DD3FC" },
      { fill: "#1F2820", border: "#4ADE80", text: "#86EFAC" },
      { fill: "#282420", border: "#FBBF24", text: "#FDE68A" },
    ],
    nodeColors: [
      "#F97316", "#EC4899", "#A855F7", "#4ADE80", "#FBBF24", "#38BDF8",
    ],
    roughness: 0.8,
    fillStyle: "cross-hatch",
    bowing: 1,
    dashedBorder: false,
    outerBorderColor: "#3F3F46",
  },
};

export function getTheme(name: string): DiagramTheme {
  return THEMES[name] ?? THEMES.whiteboard;
}

export function listThemeNames(): string[] {
  return Object.keys(THEMES);
}
