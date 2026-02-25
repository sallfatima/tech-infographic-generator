/**
 * DiagramCanvas — SVG container principal avec rendu Rough.js.
 *
 * Phase 2 : utilise RoughNode, RoughEdge, ZoneBox, StepNumber.
 * Prend InfographicData → calcule le layout → dessine le SVG hand-drawn.
 */

import { useMemo, useRef, useState, useEffect } from "react";
import type { RoughSVG } from "roughjs/bin/svg";
import type { InfographicData } from "../../types/infographic";
import { layoutNodes } from "../../lib/layoutEngine";
import { createRoughSvg } from "../../lib/roughRenderer";
import { getTheme } from "../../lib/themes";
import RoughNode from "./RoughNode";
import RoughEdge from "./RoughEdge";
import ZoneBox from "./ZoneBox";

/** Dimensions du canvas SVG. */
const CANVAS_W = 1400;
const CANVAS_H = 900;

interface DiagramCanvasProps {
  data: InfographicData;
  themeName?: string;
}

export default function DiagramCanvas({
  data,
  themeName = "whiteboard",
}: DiagramCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [rc, setRc] = useState<RoughSVG | null>(null);
  const theme = useMemo(() => getTheme(themeName), [themeName]);

  // Initialiser Rough.js quand le SVG est monté
  useEffect(() => {
    if (svgRef.current) {
      setRc(createRoughSvg(svgRef.current));
    }
  }, []);

  // Calcul du layout — mémorisé pour éviter les re-calculs inutiles
  const positions = useMemo(
    () => layoutNodes(data, CANVAS_W, CANVAS_H),
    [data],
  );

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${CANVAS_W} ${CANVAS_H}`}
      className="w-full h-full rounded-xl shadow-lg"
      style={{ maxHeight: "80vh", backgroundColor: theme.bg }}
    >
      {/* Bordure extérieure dashed (style SwirlAI) */}
      <rect
        x={10}
        y={10}
        width={CANVAS_W - 20}
        height={CANVAS_H - 20}
        rx={12}
        fill="none"
        stroke={theme.outerBorderColor}
        strokeWidth={2}
        strokeDasharray={theme.dashedBorder ? "8 4" : undefined}
        opacity={0.3}
      />

      {/* Titre */}
      <text
        x={CANVAS_W / 2}
        y={45}
        textAnchor="middle"
        fill={theme.text}
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
          fill={theme.textMuted}
          fontSize={14}
        >
          {data.subtitle}
        </text>
      )}

      {/* Zones de groupement (dessiner AVANT tout pour qu'elles soient derrière) */}
      {data.zones.map((zone, i) => {
        // Calculer le bounding box de la zone
        const zoneNodeIds = zone.nodes ?? [];
        const zonePositions = zoneNodeIds
          .map((id: string) => positions.get(id))
          .filter(Boolean);

        if (zonePositions.length === 0) return null;

        const minX = Math.min(...zonePositions.map((p) => p!.x)) - 20;
        const minY = Math.min(...zonePositions.map((p) => p!.y)) - 30;
        const maxX = Math.max(...zonePositions.map((p) => p!.x + p!.w)) + 20;
        const maxY = Math.max(...zonePositions.map((p) => p!.y + p!.h)) + 20;

        const sc = theme.sectionColors[i % theme.sectionColors.length];

        return (
          <ZoneBox
            key={`zone-${i}`}
            x={minX}
            y={minY}
            w={maxX - minX}
            h={maxY - minY}
            title={zone.name ?? `Zone ${i + 1}`}
            borderColor={sc.border}
            fillColor={sc.fill}
            fillOpacity={0.15}
            dashed={theme.dashedBorder}
          />
        );
      })}

      {/* Connections (dessiner AVANT les nodes pour qu'elles soient derrière) */}
      {rc &&
        data.connections.map((conn, i) => {
          const fromPos = positions.get(conn.from_node);
          const toPos = positions.get(conn.to_node);
          if (!fromPos || !toPos) return null;

          const sc = theme.sectionColors[i % theme.sectionColors.length];

          return (
            <RoughEdge
              key={`edge-${i}`}
              rc={rc}
              fromPos={fromPos}
              toPos={toPos}
              label={conn.label}
              style={conn.style}
              index={i}
              theme={theme}
              borderColor={sc.border}
            />
          );
        })}

      {/* Nodes */}
      {rc &&
        data.nodes.map((node, i) => {
          const pos = positions.get(node.id);
          if (!pos) return null;

          const sc = theme.sectionColors[i % theme.sectionColors.length];

          return (
            <RoughNode
              key={node.id}
              rc={rc}
              nodeId={node.id}
              label={node.label}
              description={node.description}
              shape={node.shape}
              icon={node.icon}
              pos={pos}
              fillColor={node.color ?? sc.fill}
              borderColor={sc.border}
              theme={theme}
            />
          );
        })}
    </svg>
  );
}
