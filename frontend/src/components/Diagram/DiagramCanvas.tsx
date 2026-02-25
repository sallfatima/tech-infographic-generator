/**
 * DiagramCanvas — SVG container principal.
 *
 * Phase 1 : rendu basique avec <rect> + <text> + <line>.
 * Phase 2 : remplacé par Rough.js (RoughNode, RoughEdge, etc.).
 *
 * Prend InfographicData → calcule le layout → dessine le SVG.
 */

import { useMemo } from "react";
import type { InfographicData, NodePosition } from "../../types/infographic";
import { layoutNodes, getNodeCenter, getEdgePoint } from "../../lib/layoutEngine";

/** Dimensions du canvas SVG. */
const CANVAS_W = 1400;
const CANVAS_H = 900;

/** Couleurs par défaut pour les nodes (palette SwirlAI/ByteByteGo). */
const NODE_COLORS = [
  "#E3F2FD", // bleu clair
  "#FFF3E0", // orange clair
  "#E8F5E9", // vert clair
  "#F3E5F5", // violet clair
  "#FFF9C4", // jaune clair
  "#E0F7FA", // cyan clair
  "#FCE4EC", // rose clair
  "#F1F8E9", // vert menthe
];

const BORDER_COLORS = [
  "#2B7DE9", // bleu
  "#E8833A", // orange
  "#4CAF50", // vert
  "#9C27B0", // violet
  "#F9A825", // jaune
  "#00ACC1", // cyan
  "#E53935", // rouge
  "#7CB342", // vert clair
];

interface DiagramCanvasProps {
  data: InfographicData;
}

export default function DiagramCanvas({ data }: DiagramCanvasProps) {
  // Calcul du layout — mémorisé pour éviter les re-calculs inutiles
  const positions = useMemo(
    () => layoutNodes(data, CANVAS_W, CANVAS_H),
    [data],
  );

  return (
    <svg
      viewBox={`0 0 ${CANVAS_W} ${CANVAS_H}`}
      className="w-full h-full bg-white rounded-xl shadow-lg"
      style={{ maxHeight: "80vh" }}
    >
      {/* Bordure extérieure dashed (style SwirlAI) */}
      <rect
        x={10}
        y={10}
        width={CANVAS_W - 20}
        height={CANVAS_H - 20}
        rx={12}
        fill="none"
        stroke="#2B7DE9"
        strokeWidth={2}
        strokeDasharray="8 4"
        opacity={0.3}
      />

      {/* Titre */}
      <text
        x={CANVAS_W / 2}
        y={45}
        textAnchor="middle"
        className="text-xl font-bold"
        fill="#1e293b"
        fontSize={22}
        fontWeight={700}
      >
        {data.title}
      </text>

      {/* Sous-titre */}
      {data.subtitle && (
        <text
          x={CANVAS_W / 2}
          y={68}
          textAnchor="middle"
          fill="#64748b"
          fontSize={14}
        >
          {data.subtitle}
        </text>
      )}

      {/* Connections (dessiner AVANT les nodes pour qu'elles soient derrière) */}
      {data.connections.map((conn, i) => {
        const fromPos = positions.get(conn.from_node);
        const toPos = positions.get(conn.to_node);
        if (!fromPos || !toPos) return null;

        const fromCenter = getNodeCenter(fromPos);
        const toCenter = getNodeCenter(toPos);
        const start = getEdgePoint(fromPos, toCenter.cx, toCenter.cy);
        const end = getEdgePoint(toPos, fromCenter.cx, fromCenter.cy);

        const isDashed =
          conn.style === "dashed_arrow" || conn.style === "curved_dashed";

        return (
          <g key={`conn-${i}`}>
            {/* Ligne */}
            <line
              x1={start.x}
              y1={start.y}
              x2={end.x}
              y2={end.y}
              stroke="#64748b"
              strokeWidth={1.5}
              strokeDasharray={isDashed ? "6 3" : undefined}
              markerEnd="url(#arrowhead)"
            />
            {/* Label sur la connection */}
            {conn.label && (
              <>
                <rect
                  x={(start.x + end.x) / 2 - conn.label.length * 3.5}
                  y={(start.y + end.y) / 2 - 10}
                  width={conn.label.length * 7}
                  height={18}
                  rx={4}
                  fill="white"
                  opacity={0.9}
                />
                <text
                  x={(start.x + end.x) / 2}
                  y={(start.y + end.y) / 2 + 3}
                  textAnchor="middle"
                  fill="#64748b"
                  fontSize={11}
                  fontStyle="italic"
                >
                  {conn.label}
                </text>
              </>
            )}
          </g>
        );
      })}

      {/* Nodes */}
      {data.nodes.map((node, i) => {
        const pos = positions.get(node.id);
        if (!pos) return null;
        return (
          <NodeRect
            key={node.id}
            node={node}
            pos={pos}
            fillColor={node.color ?? NODE_COLORS[i % NODE_COLORS.length]}
            borderColor={BORDER_COLORS[i % BORDER_COLORS.length]}
            index={i}
          />
        );
      })}

      {/* Définition du marker flèche */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth={10}
          markerHeight={7}
          refX={9}
          refY={3.5}
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
        </marker>
      </defs>
    </svg>
  );
}

// ─── Sous-composant NodeRect ────────────────────────────────────────

interface NodeRectProps {
  node: { id: string; label: string; description?: string; icon?: string };
  pos: NodePosition;
  fillColor: string;
  borderColor: string;
  index: number;
}

function NodeRect({ node, pos, fillColor, borderColor }: NodeRectProps) {
  const labelLines = wrapText(node.label, 22);
  const descLines = node.description ? wrapText(node.description, 28) : [];

  return (
    <g>
      {/* Rectangle arrondi */}
      <rect
        x={pos.x}
        y={pos.y}
        width={pos.w}
        height={pos.h}
        rx={8}
        fill={fillColor}
        stroke={borderColor}
        strokeWidth={2}
      />

      {/* Label (centré verticalement) */}
      {labelLines.map((line, i) => (
        <text
          key={`label-${i}`}
          x={pos.x + pos.w / 2}
          y={
            pos.y +
            (descLines.length > 0 ? 22 : pos.h / 2) +
            i * 16
          }
          textAnchor="middle"
          fill="#1e293b"
          fontSize={13}
          fontWeight={600}
        >
          {line}
        </text>
      ))}

      {/* Description (sous le label, plus petite) */}
      {descLines.map((line, i) => (
        <text
          key={`desc-${i}`}
          x={pos.x + pos.w / 2}
          y={
            pos.y +
            22 +
            labelLines.length * 16 +
            4 +
            i * 14
          }
          textAnchor="middle"
          fill="#64748b"
          fontSize={10}
        >
          {line}
        </text>
      ))}
    </g>
  );
}

// ─── Utilitaire wrapping texte ──────────────────────────────────────

/**
 * Coupe un texte en lignes de maxChars caractères max.
 * Simple wrapping par mots.
 */
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
