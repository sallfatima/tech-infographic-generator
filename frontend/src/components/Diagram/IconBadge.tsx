/**
 * IconBadge — Vrai SVG icon blanc sur cercle coloré.
 * Charge les SVG icons depuis /public/icons/ via iconLoader.
 * Fallback vers emojis si le SVG n'est pas disponible.
 */

import { useEffect, useRef, useState } from "react";
import { loadIcon, getIconContent } from "@/lib/iconLoader";

interface IconBadgeProps {
  cx: number;
  cy: number;
  icon: string;
  bgColor: string;
  size?: number;
}

/** Fallback emojis — utilisés seulement si le SVG n'est pas dispo. */
const FALLBACK_SYMBOLS: Record<string, string> = {
  database: "\u{1F5C4}", server: "\u{1F5A5}", cloud: "\u2601", user: "\u{1F464}",
  lock: "\u{1F512}", api: "\u26A1", network: "\u{1F310}", code: "\u{1F4BB}",
  brain: "\u{1F9E0}", chart: "\u{1F4CA}", gear: "\u2699", lightning: "\u26A1",
  container: "\u{1F4E6}", queue: "\u{1F4CB}", cache: "\u{1F4BE}", monitor: "\u{1F4FA}",
  shield: "\u{1F6E1}", globe: "\u{1F30D}", arrow_right: "\u2192", check: "\u2713",
  star: "\u2605", folder: "\u{1F4C1}", cpu: "\u{1F532}", memory: "\u{1F9E9}",
  search: "\u{1F50D}", filter: "\u23CF", layers: "\u{1F4DA}", workflow: "\u{1F504}",
  document: "\u{1F4C4}", play: "\u25B6", agent: "\u{1F916}", rag: "\u{1F4CE}",
  prompt: "\u{1F4AC}", finetune: "\u{1F3AF}", embedding: "\u{1F4D0}",
  vector_db: "\u{1F522}", llm: "\u{1F9E0}", transformer: "\u{1F500}",
  evaluation: "\u{1F4CF}", guardrails: "\u{1F6A7}", context: "\u{1F4D6}",
  tool_use: "\u{1F527}", mcp: "\u{1F50C}", multi_agent: "\u{1F465}",
  reasoning: "\u{1F4A1}",
};

export default function IconBadge({
  cx,
  cy,
  icon,
  bgColor,
  size = 28,
}: IconBadgeProps) {
  const circleR = size * 0.85;
  const iconGRef = useRef<SVGGElement>(null);

  // Essai sync d'abord (cache), puis async
  const [svgContent, setSvgContent] = useState<string | null>(
    () => getIconContent(icon)
  );

  useEffect(() => {
    let cancelled = false;

    // Check cache sync first
    const cached = getIconContent(icon);
    if (cached) {
      setSvgContent(cached);
      return;
    }

    // Async fetch
    loadIcon(icon).then((content) => {
      if (!cancelled && content) {
        setSvgContent(content);
      }
    });

    return () => { cancelled = true; };
  }, [icon]);

  // Injecter le SVG content dans le <g> ref
  useEffect(() => {
    if (iconGRef.current && svgContent) {
      iconGRef.current.innerHTML = svgContent;
    }
  }, [svgContent]);

  // Dimensions du SVG icon (viewBox 0 0 24 24)
  const iconSize = size * 0.9;
  const iconX = cx - iconSize / 2;
  const iconY = cy - iconSize / 2;
  const iconScale = iconSize / 24;

  return (
    <g>
      {/* Cercle coloré de fond */}
      <circle
        cx={cx}
        cy={cy}
        r={circleR}
        fill={bgColor}
        opacity={0.9}
      />

      {svgContent ? (
        /* Vrai SVG icon — blanc sur fond coloré */
        <g
          ref={iconGRef}
          transform={`translate(${iconX}, ${iconY}) scale(${iconScale})`}
          fill="white"
          stroke="none"
        />
      ) : (
        /* Fallback emoji pendant le chargement ou si SVG indisponible */
        <text
          x={cx}
          y={cy + 1}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={size * 0.7}
        >
          {FALLBACK_SYMBOLS[icon] ?? "\u25CF"}
        </text>
      )}
    </g>
  );
}
