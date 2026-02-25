/**
 * StepNumber — Numéros cerclés ①②③ (style ByteByteGo/SwirlAI).
 * Positionné le long des edges pour indiquer l'ordre du flux.
 */

interface StepNumberProps {
  cx: number;
  cy: number;
  number: number;
  bgColor?: string;
  borderColor?: string;
  textColor?: string;
  radius?: number;
}

export default function StepNumber({
  cx,
  cy,
  number,
  bgColor = "#FFFFFF",
  borderColor = "#2B7DE9",
  textColor = "#2B7DE9",
  radius = 12,
}: StepNumberProps) {
  return (
    <g>
      <circle
        cx={cx}
        cy={cy}
        r={radius}
        fill={bgColor}
        stroke={borderColor}
        strokeWidth={2}
      />
      <text
        x={cx}
        y={cy + 1}
        textAnchor="middle"
        dominantBaseline="central"
        fill={textColor}
        fontSize={radius * 1.1}
        fontWeight={700}
      >
        {number}
      </text>
    </g>
  );
}
