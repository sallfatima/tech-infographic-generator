/**
 * iconLoader.ts — Charge les SVG icons depuis /public/icons/ et les cache.
 * Utilisé par IconBadge.tsx pour afficher les vrais SVG au lieu des emojis.
 */

const cache = new Map<string, string>();
const pending = new Map<string, Promise<string | null>>();

/** Liste des 45 icônes SVG disponibles dans /public/icons/ */
export const AVAILABLE_ICONS: string[] = [
  "agent", "api", "arrow_right", "brain", "cache", "chart", "check",
  "cloud", "code", "container", "context", "cpu", "database", "document",
  "embedding", "evaluation", "filter", "finetune", "folder", "gear",
  "globe", "guardrails", "layers", "lightning", "llm", "lock", "mcp",
  "memory", "monitor", "multi_agent", "network", "play", "prompt",
  "queue", "rag", "reasoning", "search", "server", "shield", "star",
  "tool_use", "transformer", "user", "vector_db", "workflow",
];

/**
 * Charge un SVG icon par son nom. Retourne le contenu inner SVG (paths, circles, etc.)
 * sans le wrapper <svg>. Le résultat est caché pour les appels suivants.
 */
export async function loadIcon(name: string): Promise<string | null> {
  const cached = cache.get(name);
  if (cached !== undefined) return cached;

  const inflight = pending.get(name);
  if (inflight) return inflight;

  const promise = fetch(`/icons/${name}.svg`)
    .then((response) => {
      if (!response.ok) return null;
      return response.text();
    })
    .then((text) => {
      if (!text) {
        cache.set(name, "");
        return null;
      }
      // Extraire le contenu inner SVG (sans le wrapper <svg>...</svg>)
      const match = text.match(/<svg[^>]*>([\s\S]*)<\/svg>/i);
      const inner = match ? match[1].trim() : text;
      cache.set(name, inner);
      return inner;
    })
    .catch(() => {
      cache.set(name, "");
      return null;
    })
    .finally(() => {
      pending.delete(name);
    });

  pending.set(name, promise);
  return promise;
}

/**
 * Getter synchrone — retourne le contenu SVG si déjà en cache, sinon null.
 * Utile pour le rendu initial avant que le fetch async ne termine.
 */
export function getIconContent(name: string): string | null {
  const content = cache.get(name);
  return content || null;
}

/**
 * Précharge un batch d'icônes en parallèle.
 * Appeler au montage du DiagramCanvas pour éviter le flash d'emojis.
 */
export async function preloadIcons(names: string[]): Promise<void> {
  await Promise.all(names.map(loadIcon));
}
