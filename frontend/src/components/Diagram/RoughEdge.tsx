/**
 * RoughEdge — Flèche courbe bézier hand-drawn (style SwirlAI).
 *
 * Remplace les <line> basiques de Phase 1 par des paths SVG courbés.
 * La courbure est DÉTERMINISTE (hash des IDs, pas Math.random()).
 */

import { useEffect, useRef } from "react";
import type { RoughSVG } from "roughjs/bin/svg";
import type { NodePosition } from "../../types/infographic";
import type { DiagramTheme } from "../../lib/themes";
import { getNodeCenter, getEdgePoint } from "../../lib/layoutEngine";
import StepNumber from "./StepNumber";

interface RoughEdgeProps {
  rc: RoughSVG;
  fromPos: NodePosition;
  toPos: NodePosition;
  label?: string;
  style?: string;
  index: number;
  theme: DiagramTheme;
  borderColor: string;
}

/** Hash déterministe pour la direction de courbure. */
function simpleHash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

export default function RoughEdge({
  rc,
  fromPos,
  toPos,
  label,
  style = "arrow",
  index,
  theme,
  borderColor,
}: RoughEdgeProps) {
  const gRef = useRef<SVGGElement>(null);

  const fromCenter = getNodeCenter(fromPos);
  const toCenter = getNodeCenter(toPos);

  // Points de départ/arrivée sur le bord des nodes
  const start = getEdgePoint(fromPos, toCenter.cx, toCenter.cy);
  const end = getEdgePoint(toPos, fromCenter.cx, fromCenter.cy);

  // Point de contrôle bézier (courbure perpendiculaire)
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const curvature = 0.25;

  // Direction DÉTERMINISTE via hash
  const hashKey = `${Math.round(fromPos.x)}-${Math.round(toPos.x)}`;
  const direction = simpleHash(hashKey) % 2 === 0 ? 1 : -1;

  const mx = (start.x + end.x) / 2;
  const my = (start.y + end.y) / 2;
  const nx = -dy / (dist || 1);
  const ny = dx / (dist || 1);
  const offset = curvature * dist * direction;
  const qx = mx + nx * offset;
  const qy = my + ny * offset;

  // Angle de la flèche au point d'arrivée
  const t = 0.95;
  const endTangentX = 2 * (1 - t) * (qx - start.x) + 2 * t * (end.x - qx);
  const endTangentY = 2 * (1 - t) * (qy - start.y) + 2 * t * (end.y - qy);
  const angle = Math.atan2(endTangentY, endTangentX);

  const isDashed = style === "dashed_arrow" || style === "curved_dashed";
  const pathD = `M ${start.x},${start.y} Q ${qx},${qy} ${end.x},${end.y}`;

  // Point médian de la courbe (t=0.5) pour le label
  const midX = 0.25 * start.x + 0.5 * qx + 0.25 * end.x;
  const midY = 0.25 * start.y + 0.5 * qy + 0.25 * end.y;

  // Rough.js path
  useEffect(() => {
    if (!gRef.current || !rc) return;

    const roughChildren = gRef.current.querySelectorAll("[data-rough]");
    roughChildren.forEach((el) => el.remove());

    const pathEl = rc.path(pathD, {
      stroke: borderColor,
      strokeWidth: 1.5,
      roughness: theme.roughness * 0.6,
      bowing: theme.bowing * 0.5,
      fill: "none",
    });
    pathEl.setAttribute("data-rough", "true");

    if (isDashed) {
      // Appliquer le dashed sur tous les path enfants
      const paths = pathEl.querySelectorAll("path");
      paths.forEach((p) => p.setAttribute("stroke-dasharray", "8 5"));
    }

    gRef.current.insertBefore(pathEl, gRef.current.firstChild);
  }, [rc, pathD, borderColor, isDashed, theme]);

  // Arrowhead
  const arrowSize = 8;
  const a1x = end.x - arrowSize * Math.cos(angle - 0.4);
  const a1y = end.y - arrowSize * Math.sin(angle - 0.4);
  const a2x = end.x - arrowSize * Math.cos(angle + 0.4);
  const a2y = end.y - arrowSize * Math.sin(angle + 0.4);

  return (
    <g ref={gRef}>
      {/* Rough.js path injecté via useEffect */}

      {/* Arrowhead (triangle SVG classique pour netteté) */}
      <polygon
        points={`${end.x},${end.y} ${a1x},${a1y} ${a2x},${a2y}`}
        fill={borderColor}
      />

      {/* Numéro cerclé au milieu */}
      <StepNumber
        cx={midX}
        cy={midY - 14}
        number={index + 1}
        bgColor={theme.bg}
        borderColor={borderColor}
        textColor={borderColor}
        radius={10}
      />

      {/* Label sur la connection */}
      {label && (
        <g>
          <rect
            x={midX - label.length * 3.2}
            y={midY + 2}
            width={label.length * 6.4}
            height={16}
            rx={4}
            fill={theme.bg}
            opacity={0.9}
          />
          <text
            x={midX}
            y={midY + 13}
            textAnchor="middle"
            fill={theme.textMuted}
            fontSize={10}
            fontStyle="italic"
          >
            {label}
          </text>
        </g>
      )}
    </g>
  );
}
