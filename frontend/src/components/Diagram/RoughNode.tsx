/**
 * RoughNode — Node rendu avec Rough.js (style hand-drawn Excalidraw).
 *
 * Phase 3 : ajout sélection, drag-drop et double-clic inline edit.
 * Chaque node.shape détermine la forme : rounded_rect, circle, cylinder, etc.
 */

import { useEffect, useRef } from "react";
import type { RoughSVG } from "roughjs/bin/svg";
import type { NodePosition } from "../../types/infographic";
import type { DiagramTheme } from "../../lib/themes";
import {
  drawRoughRect,
  drawRoughCircle,
  drawRoughCylinder,
  drawRoughHexagon,
  drawRoughCloud,
  drawRoughDiamond,
} from "../../lib/roughRenderer";
import IconBadge from "./IconBadge";

interface RoughNodeProps {
  rc: RoughSVG;
  nodeId: string;
  label: string;
  description?: string;
  shape?: string;
  icon?: string;
  pos: NodePosition;
  fillColor: string;
  borderColor: string;
  theme: DiagramTheme;
  /** Phase 3 : sélection */
  isSelected?: boolean;
  onSelect?: (nodeId: string) => void;
  onDragStart?: (nodeId: string, e: React.MouseEvent) => void;
  onDoubleClick?: (nodeId: string) => void;
}

export default function RoughNode({
  rc,
  nodeId,
  label,
  description,
  shape = "rounded_rect",
  icon,
  pos,
  fillColor,
  borderColor,
  theme,
  isSelected = false,
  onSelect,
  onDragStart,
  onDoubleClick,
}: RoughNodeProps) {
  const gRef = useRef<SVGGElement>(null);

  // Dessiner la shape Rough.js dans le <g> via DOM direct
  useEffect(() => {
    if (!gRef.current || !rc) return;

    // Nettoyer les enfants rough précédents (garde les textes/icônes React)
    const roughChildren = gRef.current.querySelectorAll("[data-rough]");
    roughChildren.forEach((el) => el.remove());

    const opts = {
      fill: fillColor,
      fillStyle: theme.fillStyle,
      stroke: borderColor,
      strokeWidth: 2,
      roughness: theme.roughness,
      bowing: theme.bowing,
    };

    let shapeEl: SVGGElement;
    const cx = pos.x + pos.w / 2;
    const cy = pos.y + pos.h / 2;

    switch (shape) {
      case "circle":
        shapeEl = drawRoughCircle(rc, cx, cy, Math.min(pos.w, pos.h), opts);
        break;
      case "cylinder":
        shapeEl = drawRoughCylinder(rc, pos.x, pos.y, pos.w, pos.h, opts);
        break;
      case "hexagon":
        shapeEl = drawRoughHexagon(rc, cx, cy, Math.min(pos.w, pos.h) / 2, opts);
        break;
      case "cloud":
        shapeEl = drawRoughCloud(rc, pos.x, pos.y, pos.w, pos.h, opts);
        break;
      case "diamond":
        shapeEl = drawRoughDiamond(rc, cx, cy, pos.w, pos.h, opts);
        break;
      default:
        // rounded_rect, rectangle, et défaut
        shapeEl = drawRoughRect(rc, pos.x, pos.y, pos.w, pos.h, opts);
        break;
    }

    shapeEl.setAttribute("data-rough", "true");
    // Insérer en premier enfant (derrière le texte)
    gRef.current.insertBefore(shapeEl, gRef.current.firstChild);
  }, [rc, pos, fillColor, borderColor, shape, theme]);

  const cx = pos.x + pos.w / 2;
  const hasIcon = !!icon;
  const iconOffset = hasIcon ? 20 : 0;

  // Calcul vertical du texte
  const labelLines = wrapText(label, 20);
  const descLines = description ? wrapText(description, 26) : [];
  const totalTextH = labelLines.length * 16 + descLines.length * 13;
  const textStartY = pos.y + (pos.h - totalTextH) / 2 + iconOffset / 2;

  return (
    <g
      ref={gRef}
      className="cursor-pointer"
      onMouseDown={(e) => {
        e.stopPropagation();
        onSelect?.(nodeId);
        onDragStart?.(nodeId, e);
      }}
      onDoubleClick={(e) => {
        e.stopPropagation();
        onDoubleClick?.(nodeId);
      }}
    >
      {/* Le shape Rough.js est injecté via useEffect (data-rough) */}

      {/* Halo de sélection */}
      {isSelected && (
        <rect
          x={pos.x - 4}
          y={pos.y - 4}
          width={pos.w + 8}
          height={pos.h + 8}
          rx={8}
          fill="none"
          stroke="#3b82f6"
          strokeWidth={2}
          strokeDasharray="6 3"
          opacity={0.7}
        />
      )}

      {/* Icône badge si présente */}
      {icon && (
        <IconBadge
          cx={cx}
          cy={pos.y + 18}
          icon={icon}
          bgColor={borderColor}
          size={16}
        />
      )}

      {/* Label */}
      {labelLines.map((line, i) => (
        <text
          key={`l-${i}`}
          x={cx}
          y={textStartY + 12 + i * 16}
          textAnchor="middle"
          fill={theme.text}
          fontSize={13}
          fontWeight={600}
          style={{ pointerEvents: "none" }}
        >
          {line}
        </text>
      ))}

      {/* Description */}
      {descLines.map((line, i) => (
        <text
          key={`d-${i}`}
          x={cx}
          y={textStartY + 12 + labelLines.length * 16 + 4 + i * 13}
          textAnchor="middle"
          fill={theme.textMuted}
          fontSize={10}
          style={{ pointerEvents: "none" }}
        >
          {line}
        </text>
      ))}
    </g>
  );
}

/** Coupe un texte en lignes. */
function wrapText(text: string, maxChars: number): string[] {
  const words = text.split(" ");
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    if (current.length + word.length + 1 > maxChars && current.length > 0) {
      lines.push(current);
      current = word;
    } else {
      current = current.length > 0 ? `${current} ${word}` : word;
    }
  }
  if (current) lines.push(current);
  return lines;
}
