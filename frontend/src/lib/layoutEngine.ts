/**
 * Moteur de layout — positionne les nodes sur le canvas SVG.
 *
 * 4 layouts disponibles :
 * - grid (auto) : grille adaptative N colonnes
 * - vertical : layers horizontaux top-to-bottom
 * - horizontal : colonnes left-to-right (pipeline)
 * - radial : hub central + nodes en cercle
 *
 * Regle : DETERMINISTE — meme input = meme output. Pas de random().
 */

import type { InfographicData, LayoutResult, NodePosition } from "../types/infographic";

/** Marges et dimensions par defaut. */
const MARGIN_X = 40;
const MARGIN_TOP = 80; // espace pour le titre
const MARGIN_BOTTOM = 40;
const NODE_W = 180;
const NODE_H = 90;
const GAP_X = 40;
const GAP_Y = 40;

// ─────────────────────────────────────────────────────────
// Dispatcher principal
// ─────────────────────────────────────────────────────────

/**
 * Layout principal — dispatch vers le bon layout selon le mode.
 */
export function layoutNodes(
  data: InfographicData,
  canvasW: number,
  canvasH: number,
  mode: "auto" | "vertical" | "horizontal" | "radial" = "auto",
): LayoutResult {
  const n = data.nodes.length;
  if (n === 0) return new Map();

  switch (mode) {
    case "vertical":
      return layoutVertical(data, canvasW, canvasH);
    case "horizontal":
      return layoutHorizontal(data, canvasW, canvasH);
    case "radial":
      return layoutRadial(data, canvasW, canvasH);
    default:
      return layoutGrid(data, canvasW, canvasH);
  }
}

// ─────────────────────────────────────────────────────────
// Helpers : topological layer assignment
// ─────────────────────────────────────────────────────────

/**
 * Assigne un layer (profondeur) a chaque node via BFS depuis les sources.
 * Sources = nodes sans connexions entrantes.
 * Si pas de connexions, distribue uniformement.
 */
function assignLayers(data: InfographicData): Map<string, number> {
  const layerMap = new Map<string, number>();
  const nodeIds = new Set(data.nodes.map((n) => n.id));

  // Si pas de connexions, distribuer par index
  if (data.connections.length === 0) {
    data.nodes.forEach((node, i) => {
      layerMap.set(node.id, i);
    });
    return layerMap;
  }

  // Construire le graphe : adjacency list
  const incoming = new Map<string, Set<string>>();
  const outgoing = new Map<string, Set<string>>();
  for (const id of nodeIds) {
    incoming.set(id, new Set());
    outgoing.set(id, new Set());
  }
  for (const conn of data.connections) {
    if (nodeIds.has(conn.from_node) && nodeIds.has(conn.to_node)) {
      outgoing.get(conn.from_node)?.add(conn.to_node);
      incoming.get(conn.to_node)?.add(conn.from_node);
    }
  }

  // Sources = nodes sans incoming
  const sources = data.nodes.filter(
    (n) => (incoming.get(n.id)?.size ?? 0) === 0
  );

  // BFS depuis les sources
  const queue: { id: string; depth: number }[] = sources.map((n) => ({
    id: n.id,
    depth: 0,
  }));
  const visited = new Set<string>();

  while (queue.length > 0) {
    const item = queue.shift();
    if (!item) break;
    const { id, depth } = item;

    if (visited.has(id)) {
      // Garder la profondeur max (longest path)
      const existing = layerMap.get(id) ?? 0;
      if (depth > existing) {
        layerMap.set(id, depth);
      }
      continue;
    }

    visited.add(id);
    layerMap.set(id, depth);

    for (const nextId of outgoing.get(id) ?? []) {
      queue.push({ id: nextId, depth: depth + 1 });
    }
  }

  // Nodes non visites (cycles ou isoles) : assigner au dernier layer + 1
  const maxLayer = Math.max(0, ...layerMap.values());
  let extraIdx = 0;
  for (const node of data.nodes) {
    if (!layerMap.has(node.id)) {
      layerMap.set(node.id, maxLayer + 1 + extraIdx);
      extraIdx++;
    }
  }

  return layerMap;
}

/**
 * Groupe les nodes par layer, tries par index original pour determinisme.
 */
function groupByLayer(
  data: InfographicData,
  layerMap: Map<string, number>,
): { id: string; idx: number }[][] {
  const groups = new Map<number, { id: string; idx: number }[]>();

  data.nodes.forEach((node, idx) => {
    const layer = layerMap.get(node.id) ?? 0;
    if (!groups.has(layer)) groups.set(layer, []);
    groups.get(layer)?.push({ id: node.id, idx });
  });

  // Trier les layers par numero, nodes par index original
  const sorted = [...groups.entries()].sort((a, b) => a[0] - b[0]);
  return sorted.map(([, nodes]) =>
    nodes.sort((a, b) => a.idx - b.idx)
  );
}

// ─────────────────────────────────────────────────────────
// Layout : Grid (auto)
// ─────────────────────────────────────────────────────────

/**
 * Layout grille — place les nodes en lignes/colonnes.
 * Adaptatif : 1-4 colonnes selon le nombre de nodes.
 */
function layoutGrid(
  data: InfographicData,
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const positions: LayoutResult = new Map();
  const n = data.nodes.length;

  let cols: number;
  if (n <= 3) cols = n;
  else if (n <= 6) cols = 3;
  else if (n <= 9) cols = 3;
  else cols = 4;

  const rows = Math.ceil(n / cols);

  const availW = canvasW - 2 * MARGIN_X;
  const availH = canvasH - MARGIN_TOP - MARGIN_BOTTOM;

  const nodeW = Math.min(NODE_W, (availW - (cols - 1) * GAP_X) / cols);
  const nodeH = Math.min(NODE_H, (availH - (rows - 1) * GAP_Y) / rows);

  const gridW = cols * nodeW + (cols - 1) * GAP_X;
  const gridH = rows * nodeH + (rows - 1) * GAP_Y;

  const offsetX = MARGIN_X + (availW - gridW) / 2;
  const offsetY = MARGIN_TOP + (availH - gridH) / 2;

  data.nodes.forEach((node, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);

    const nodesInRow = row === rows - 1 ? n - row * cols : cols;
    const rowOffsetX =
      nodesInRow < cols ? ((cols - nodesInRow) * (nodeW + GAP_X)) / 2 : 0;

    const pos: NodePosition = {
      x: offsetX + rowOffsetX + col * (nodeW + GAP_X),
      y: offsetY + row * (nodeH + GAP_Y),
      w: nodeW,
      h: nodeH,
    };

    positions.set(node.id, pos);
  });

  return positions;
}

// ─────────────────────────────────────────────────────────
// Layout : Vertical (top-to-bottom layers)
// ─────────────────────────────────────────────────────────

/**
 * Layout vertical — nodes en layers horizontaux, top-to-bottom.
 * Si connexions existent, les sources sont en haut.
 */
function layoutVertical(
  data: InfographicData,
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const positions: LayoutResult = new Map();
  const layerMap = assignLayers(data);
  const layers = groupByLayer(data, layerMap);
  const numLayers = layers.length;

  const availW = canvasW - 2 * MARGIN_X;
  const availH = canvasH - MARGIN_TOP - MARGIN_BOTTOM;

  const layerH = Math.min(
    NODE_H,
    (availH - (numLayers - 1) * GAP_Y) / numLayers
  );

  layers.forEach((layerNodes, layerIdx) => {
    const cols = layerNodes.length;
    const nodeW = Math.min(NODE_W, (availW - (cols - 1) * GAP_X) / cols);
    const rowW = cols * nodeW + (cols - 1) * GAP_X;
    const offsetX = MARGIN_X + (availW - rowW) / 2;
    const y = MARGIN_TOP + layerIdx * (layerH + GAP_Y);

    layerNodes.forEach((item, colIdx) => {
      positions.set(item.id, {
        x: offsetX + colIdx * (nodeW + GAP_X),
        y,
        w: nodeW,
        h: layerH,
      });
    });
  });

  return positions;
}

// ─────────────────────────────────────────────────────────
// Layout : Horizontal (left-to-right columns)
// ─────────────────────────────────────────────────────────

/**
 * Layout horizontal — nodes en colonnes left-to-right.
 * Sources a gauche, sinks a droite. Ideal pour pipelines.
 */
function layoutHorizontal(
  data: InfographicData,
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const positions: LayoutResult = new Map();
  const layerMap = assignLayers(data);
  const layers = groupByLayer(data, layerMap);
  const numCols = layers.length;

  const availW = canvasW - 2 * MARGIN_X;
  const availH = canvasH - MARGIN_TOP - MARGIN_BOTTOM;

  const colW = Math.min(
    NODE_W,
    (availW - (numCols - 1) * GAP_X) / numCols
  );

  layers.forEach((layerNodes, colIdx) => {
    const rows = layerNodes.length;
    const nodeH = Math.min(NODE_H, (availH - (rows - 1) * GAP_Y) / rows);
    const colH = rows * nodeH + (rows - 1) * GAP_Y;
    const offsetY = MARGIN_TOP + (availH - colH) / 2;
    const x = MARGIN_X + colIdx * (colW + GAP_X);

    layerNodes.forEach((item, rowIdx) => {
      positions.set(item.id, {
        x,
        y: offsetY + rowIdx * (nodeH + GAP_Y),
        w: colW,
        h: nodeH,
      });
    });
  });

  return positions;
}

// ─────────────────────────────────────────────────────────
// Layout : Radial (hub central + cercle)
// ─────────────────────────────────────────────────────────

/**
 * Layout radial — hub central (node le plus connecte) + nodes en cercle.
 * Ideal pour concept maps et hub-spoke architectures.
 */
function layoutRadial(
  data: InfographicData,
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const positions: LayoutResult = new Map();
  const n = data.nodes.length;

  if (n === 1) {
    positions.set(data.nodes[0].id, {
      x: canvasW / 2 - NODE_W / 2,
      y: canvasH / 2 - NODE_H / 2,
      w: NODE_W,
      h: NODE_H,
    });
    return positions;
  }

  // Trouver le hub : node avec le plus de connexions
  const connCount = new Map<string, number>();
  data.nodes.forEach((nd) => connCount.set(nd.id, 0));
  data.connections.forEach((c) => {
    connCount.set(c.from_node, (connCount.get(c.from_node) ?? 0) + 1);
    connCount.set(c.to_node, (connCount.get(c.to_node) ?? 0) + 1);
  });

  // Tri deterministe : plus de connexions d'abord, puis par index original
  const sortedNodes = [...data.nodes].sort((a, b) => {
    const diff = (connCount.get(b.id) ?? 0) - (connCount.get(a.id) ?? 0);
    if (diff !== 0) return diff;
    return data.nodes.indexOf(a) - data.nodes.indexOf(b);
  });
  const hubId = sortedNodes[0].id;

  const cx = canvasW / 2;
  const cy = (canvasH + MARGIN_TOP - MARGIN_BOTTOM) / 2;

  // Hub plus grand (1.2x)
  const hubW = NODE_W * 1.2;
  const hubH = NODE_H * 1.2;
  positions.set(hubId, {
    x: cx - hubW / 2,
    y: cy - hubH / 2,
    w: hubW,
    h: hubH,
  });

  // Nodes restants en cercle
  const others = data.nodes.filter((nd) => nd.id !== hubId);
  const availR = Math.min(
    canvasW - 2 * MARGIN_X,
    canvasH - MARGIN_TOP - MARGIN_BOTTOM,
  );
  const radius = availR / 2 - NODE_W * 0.7;

  others.forEach((node, i) => {
    // Commencer en haut (-PI/2) et tourner dans le sens horaire
    const angle = (2 * Math.PI * i) / others.length - Math.PI / 2;
    positions.set(node.id, {
      x: cx + radius * Math.cos(angle) - NODE_W / 2,
      y: cy + radius * Math.sin(angle) - NODE_H / 2,
      w: NODE_W,
      h: NODE_H,
    });
  });

  return positions;
}

// ─────────────────────────────────────────────────────────
// Helpers geometriques
// ─────────────────────────────────────────────────────────

/**
 * Retourne le point central d'un node (pour dessiner les connections).
 */
export function getNodeCenter(pos: NodePosition): { cx: number; cy: number } {
  return {
    cx: pos.x + pos.w / 2,
    cy: pos.y + pos.h / 2,
  };
}

/**
 * Calcule le point d'ancrage sur le bord d'un node vers un point cible.
 * Utilise pour que les fleches partent/arrivent au bord du rectangle.
 */
export function getEdgePoint(
  pos: NodePosition,
  targetX: number,
  targetY: number,
): { x: number; y: number } {
  const cx = pos.x + pos.w / 2;
  const cy = pos.y + pos.h / 2;
  const dx = targetX - cx;
  const dy = targetY - cy;

  if (dx === 0 && dy === 0) return { x: cx, y: cy };

  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);
  const halfW = pos.w / 2;
  const halfH = pos.h / 2;

  let scale: number;
  if (absDx * halfH > absDy * halfW) {
    scale = halfW / absDx;
  } else {
    scale = halfH / absDy;
  }

  return {
    x: cx + dx * scale,
    y: cy + dy * scale,
  };
}
