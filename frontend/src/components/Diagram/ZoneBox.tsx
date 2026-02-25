/**
 * ZoneBox — Zone dashed avec titre SUR la bordure (style SwirlAI).
 *
 * Représente un groupement visuel (ex: "K8s Control Plane", "Ingestion Pipeline").
 * Le titre est positionné en haut-centre avec un fond blanc qui "coupe" la bordure.
 */

interface ZoneBoxProps {
  x: number;
  y: number;
  w: number;
  h: number;
  title: string;
  borderColor?: string;
  fillColor?: string;
  fillOpacity?: number;
  dashed?: boolean;
}

export default function ZoneBox({
  x,
  y,
  w,
  h,
  title,
  borderColor = "#2B7DE9",
  fillColor = "#E3F2FD",
  fillOpacity = 0.15,
  dashed = true,
}: ZoneBoxProps) {
  const titleLen = title.length * 7 + 16;
  const titleX = x + w / 2;
  const titleY = y;

  return (
    <g>
      {/* Zone rectangle */}
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={8}
        fill={fillColor}
        fillOpacity={fillOpacity}
        stroke={borderColor}
        strokeWidth={2}
        strokeDasharray={dashed ? "8 4" : undefined}
      />
      {/* Fond blanc derrière le titre (coupe la bordure) */}
      <rect
        x={titleX - titleLen / 2}
        y={titleY - 10}
        width={titleLen}
        height={20}
        rx={4}
        fill="white"
      />
      {/* Titre sur la bordure */}
      <text
        x={titleX}
        y={titleY + 4}
        textAnchor="middle"
        fill={borderColor}
        fontSize={12}
        fontWeight={600}
      >
        {title}
      </text>
    </g>
  );
}
