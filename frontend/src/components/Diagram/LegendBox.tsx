/**
 * LegendBox — Legende SVG en bas-droite du canvas.
 *
 * Affiche dynamiquement les elements utilises dans le diagramme courant :
 * - Shapes de nodes (preview miniature + label)
 * - Styles de connexions (ligne preview + signification)
 * - Zones/couleurs (cercle couleur + nom)
 *
 * Ne montre QUE ce qui est present — pas de legende generique.
 * Style : bordure dashed comme ZoneBox, titre "Legende" sur la bordure.
 */

import React, { useMemo } from "react";
import type {
  InfographicData,
  NodeShape,
  ConnectionStyle,
} from "../../types/infographic";
import type { DiagramTheme } from "../../lib/themes";

interface LegendBoxProps {
  data: InfographicData;
  theme: DiagramTheme;
  /** Position X du coin superieur droit de la legende. */
  canvasW: number;
  /** Position Y du bas de la legende. */
  canvasH: number;
}

// ─── Shape labels ────────────────────────────────────────────────────

const SHAPE_LABELS: Record<string, string> = {
  rounded_rect: "Rectangle arrondi",
  rectangle: "Rectangle",
  circle: "Cercle",
  diamond: "Losange",
  cylinder: "Cylindre",
  hexagon: "Hexagone",
  cloud: "Cloud",
  parallelogram: "Parallelogramme",
  person: "Personne",
};

// ─── Connection style labels ─────────────────────────────────────────

const CONN_LABELS: Record<string, string> = {
  arrow: "Fleche directe",
  dashed_arrow: "Fleche pointillee",
  bidirectional: "Bidirectionnel",
  line: "Ligne simple",
  curved_arrow: "Fleche courbee",
  curved_dashed: "Courbee pointillee",
};

// ─── Mini shape previews (16x12 SVG) ────────────────────────────────

function ShapePreview({
  shape,
  color,
}: {
  shape: NodeShape;
  color: string;
}) {
  const w = 20;
  const h = 14;
  const cx = w / 2;
  const cy = h / 2;

  switch (shape) {
    case "circle":
      return (
        <circle
          cx={cx}
          cy={cy}
          r={6}
          fill={color}
          fillOpacity={0.3}
          stroke={color}
          strokeWidth={1.2}
        />
      );
    case "diamond":
      return (
        <polygon
          points={`${cx},${cy - 6} ${cx + 7},${cy} ${cx},${cy + 6} ${cx - 7},${cy}`}
          fill={color}
          fillOpacity={0.3}
          stroke={color}
          strokeWidth={1.2}
        />
      );
    case "cylinder":
      return (
        <g>
          <rect
            x={3}
            y={3}
            width={14}
            height={8}
            rx={1}
            fill={color}
            fillOpacity={0.3}
            stroke={color}
            strokeWidth={1.2}
          />
          <ellipse
            cx={cx}
            cy={3}
            rx={7}
            ry={2}
            fill={color}
            fillOpacity={0.3}
            stroke={color}
            strokeWidth={1}
          />
        </g>
      );
    case "hexagon": {
      const pts = [
        `${cx - 4},${cy - 6}`,
        `${cx + 4},${cy - 6}`,
        `${cx + 8},${cy}`,
        `${cx + 4},${cy + 6}`,
        `${cx - 4},${cy + 6}`,
        `${cx - 8},${cy}`,
      ].join(" ");
      return (
        <polygon
          points={pts}
          fill={color}
          fillOpacity={0.3}
          stroke={color}
          strokeWidth={1.2}
        />
      );
    }
    case "cloud":
      return (
        <ellipse
          cx={cx}
          cy={cy}
          rx={9}
          ry={6}
          fill={color}
          fillOpacity={0.3}
          stroke={color}
          strokeWidth={1.2}
        />
      );
    case "rectangle":
      return (
        <rect
          x={2}
          y={2}
          width={16}
          height={10}
          fill={color}
          fillOpacity={0.3}
          stroke={color}
          strokeWidth={1.2}
        />
      );
    default:
      // rounded_rect, parallelogram, person — defaut arrondi
      return (
        <rect
          x={2}
          y={2}
          width={16}
          height={10}
          rx={3}
          fill={color}
          fillOpacity={0.3}
          stroke={color}
          strokeWidth={1.2}
        />
      );
  }
}

// ─── Connection style preview (30x8 SVG) ────────────────────────────

function ConnPreview({
  style,
  color,
}: {
  style: ConnectionStyle;
  color: string;
}) {
  const isDashed =
    style === "dashed_arrow" || style === "curved_dashed";
  const isBidirectional = style === "bidirectional";
  const isCurved =
    style === "curved_arrow" || style === "curved_dashed";
  const isLine = style === "line";

  const dashArray = isDashed ? "3 2" : undefined;

  if (isCurved) {
    return (
      <g>
        <path
          d="M 2,7 Q 15,0 28,7"
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          strokeDasharray={dashArray}
        />
        {!isLine && (
          <polygon
            points="26,4 30,7 26,10"
            fill={color}
          />
        )}
      </g>
    );
  }

  return (
    <g>
      <line
        x1={2}
        y1={5}
        x2={28}
        y2={5}
        stroke={color}
        strokeWidth={1.5}
        strokeDasharray={dashArray}
      />
      {isBidirectional && (
        <polygon points="2,2 6,5 2,8" fill={color} />
      )}
      {!isLine && (
        <polygon points="26,2 30,5 26,8" fill={color} />
      )}
    </g>
  );
}

// ─── Composant principal ─────────────────────────────────────────────

export default function LegendBox({
  data,
  theme,
  canvasW,
  canvasH,
}: LegendBoxProps) {
  // Collecter les shapes utilisees (dedup)
  const usedShapes = useMemo(() => {
    const set = new Set<NodeShape>();
    for (const node of data.nodes) {
      set.add(node.shape ?? "rounded_rect");
    }
    return [...set];
  }, [data.nodes]);

  // Collecter les styles de connexion utilises (dedup)
  const usedStyles = useMemo(() => {
    const set = new Set<ConnectionStyle>();
    for (const conn of data.connections) {
      set.add(conn.style ?? "arrow");
    }
    return [...set];
  }, [data.connections]);

  // Collecter les zones utilisees
  const usedZones = useMemo(() => {
    return data.zones.filter((z) => z.nodes.length > 0);
  }, [data.zones]);

  // Calculer la taille de la legende
  const ROW_H = 18;
  const PADDING = 12;
  const TITLE_H = 20;
  const SECTION_GAP = 6;

  const shapeCount = usedShapes.length;
  const styleCount = usedStyles.length;
  const zoneCount = usedZones.length;

  const sectionCount =
    (shapeCount > 0 ? 1 : 0) +
    (styleCount > 0 ? 1 : 0) +
    (zoneCount > 0 ? 1 : 0);

  const totalRows = shapeCount + styleCount + zoneCount;
  const contentH =
    TITLE_H +
    totalRows * ROW_H +
    (sectionCount > 1 ? (sectionCount - 1) * SECTION_GAP : 0) +
    PADDING;

  const BOX_W = 170;
  const BOX_H = contentH;
  const MARGIN = 20;

  const boxX = canvasW - BOX_W - MARGIN;
  const boxY = canvasH - BOX_H - MARGIN;

  // Couleur de bordure
  const borderColor = theme.textMuted;

  // Rendre les rangees
  let currentY = boxY + TITLE_H + 4;

  const shapeRows: React.JSX.Element[] = [];
  usedShapes.forEach((shape, i) => {
    const sc = theme.sectionColors[i % theme.sectionColors.length];
    shapeRows.push(
      <g key={`shape-${shape}`}>
        <g transform={`translate(${boxX + PADDING}, ${currentY})`}>
          <ShapePreview shape={shape} color={sc.border} />
        </g>
        <text
          x={boxX + PADDING + 26}
          y={currentY + 10}
          fill={theme.text}
          fontSize={10}
          fontWeight={400}
        >
          {SHAPE_LABELS[shape] ?? shape}
        </text>
      </g>,
    );
    currentY += ROW_H;
  });

  if (shapeCount > 0 && (styleCount > 0 || zoneCount > 0)) {
    currentY += SECTION_GAP;
  }

  const styleRows: React.JSX.Element[] = [];
  usedStyles.forEach((style, i) => {
    const sc = theme.sectionColors[(i + 2) % theme.sectionColors.length];
    styleRows.push(
      <g key={`conn-${style}`}>
        <g transform={`translate(${boxX + PADDING}, ${currentY})`}>
          <ConnPreview style={style} color={sc.border} />
        </g>
        <text
          x={boxX + PADDING + 36}
          y={currentY + 8}
          fill={theme.text}
          fontSize={10}
          fontWeight={400}
        >
          {CONN_LABELS[style] ?? style}
        </text>
      </g>,
    );
    currentY += ROW_H;
  });

  if (styleCount > 0 && zoneCount > 0) {
    currentY += SECTION_GAP;
  }

  const zoneRows: React.JSX.Element[] = [];
  usedZones.forEach((zone, i) => {
    const sc = theme.sectionColors[i % theme.sectionColors.length];
    zoneRows.push(
      <g key={`zone-${zone.name}`}>
        <circle
          cx={boxX + PADDING + 6}
          cy={currentY + 5}
          r={5}
          fill={sc.fill}
          stroke={sc.border}
          strokeWidth={1.2}
        />
        <text
          x={boxX + PADDING + 16}
          y={currentY + 9}
          fill={theme.text}
          fontSize={10}
          fontWeight={400}
        >
          {zone.name}
        </text>
      </g>,
    );
    currentY += ROW_H;
  });

  // Titre
  const titleText = "Legende";
  const titleW = titleText.length * 7 + 16;
  const titleX = boxX + BOX_W / 2;
  const titleY = boxY;

  return (
    <g>
      {/* Box dashed */}
      <rect
        x={boxX}
        y={boxY}
        width={BOX_W}
        height={BOX_H}
        rx={6}
        fill={theme.bg}
        fillOpacity={0.92}
        stroke={borderColor}
        strokeWidth={1.5}
        strokeDasharray="6 3"
      />

      {/* Fond blanc derriere le titre (coupe la bordure) */}
      <rect
        x={titleX - titleW / 2}
        y={titleY - 8}
        width={titleW}
        height={16}
        rx={3}
        fill={theme.bg}
      />

      {/* Titre sur la bordure */}
      <text
        x={titleX}
        y={titleY + 3}
        textAnchor="middle"
        fill={borderColor}
        fontSize={11}
        fontWeight={600}
      >
        {titleText}
      </text>

      {/* Contenu */}
      {shapeRows}
      {styleRows}
      {zoneRows}
    </g>
  );
}
