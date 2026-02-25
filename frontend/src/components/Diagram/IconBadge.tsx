/**
 * IconBadge — Icône SVG blanche sur cercle coloré.
 * Style DailyDoseofDS : icône proéminente avec fond circulaire.
 */

interface IconBadgeProps {
  cx: number;
  cy: number;
  icon: string;
  bgColor: string;
  size?: number;
}

/** Map des icônes → emoji/symboles simples (Phase 2 basique, Phase 3 → vrais SVG). */
const ICON_SYMBOLS: Record<string, string> = {
  database: "🗄",
  server: "🖥",
  cloud: "☁",
  user: "👤",
  lock: "🔒",
  api: "⚡",
  network: "🌐",
  code: "💻",
  brain: "🧠",
  chart: "📊",
  gear: "⚙",
  lightning: "⚡",
  container: "📦",
  queue: "📋",
  cache: "💾",
  monitor: "📺",
  shield: "🛡",
  globe: "🌍",
  arrow_right: "→",
  check: "✓",
  star: "★",
  folder: "📁",
  cpu: "🔲",
  memory: "🧩",
  search: "🔍",
  filter: "⏏",
  layers: "📚",
  workflow: "🔄",
  document: "📄",
  play: "▶",
  agent: "🤖",
  rag: "📎",
  prompt: "💬",
  finetune: "🎯",
  embedding: "📐",
  vector_db: "🔢",
  llm: "🧠",
  transformer: "🔀",
  evaluation: "📏",
  guardrails: "🚧",
  context: "📖",
  tool_use: "🔧",
  mcp: "🔌",
  multi_agent: "👥",
  reasoning: "💡",
  person_laptop: "💻",
  chat: "💬",
  pipeline_icon: "⏩",
};

export default function IconBadge({
  cx,
  cy,
  icon,
  bgColor,
  size = 28,
}: IconBadgeProps) {
  const circleR = size * 0.85;
  const symbol = ICON_SYMBOLS[icon] ?? "●";

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
      {/* Symbole/icône centré */}
      <text
        x={cx}
        y={cy + 1}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={size * 0.7}
      >
        {symbol}
      </text>
    </g>
  );
}
