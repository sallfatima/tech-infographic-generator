/**
 * Moteur de layout — positionne les nodes sur le canvas SVG.
 *
 * Phase 1 : layout grille simple (3 colonnes, espacement uniforme).
 * Phase 2 : layouts spécialisés (radial, layered, flow, zone-grid).
 *
 * Règle : DÉTERMINISTE — même input = même output. Pas de random().
 */

import type { InfographicData, LayoutResult, NodePosition } from "../types/infographic";

/** Marges et dimensions par défaut. */
const MARGIN_X = 40;
const MARGIN_TOP = 80; // espace pour le titre
const MARGIN_BOTTOM = 40;
const NODE_W = 180;
const NODE_H = 90;
const GAP_X = 40;
const GAP_Y = 40;

/**
 * Layout principal — dispatch vers le bon layout selon le type.
 * Pour Phase 1, tout passe par layoutGrid().
 */
export function layoutNodes(
  data: InfographicData,
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const n = data.nodes.length;
  if (n === 0) return new Map();

  // Phase 1 : grille adaptative pour tous les types
  return layoutGrid(data, canvasW, canvasH);
}

/**
 * Layout grille — place les nodes en lignes/colonnes.
 *
 * Calcul adaptatif :
 * - ≤3 nodes → 1 ligne horizontale centrée
 * - ≤6 nodes → 2 lignes
 * - ≤9 nodes → 3 lignes de 3
 * - >9 nodes → grille 4 colonnes
 */
function layoutGrid(
  data: InfographicData,
  canvasW: number,
  canvasH: number,
): LayoutResult {
  const positions: LayoutResult = new Map();
  const n = data.nodes.length;

  // Nombre de colonnes adaptatif
  let cols: number;
  if (n <= 3) cols = n;
  else if (n <= 6) cols = 3;
  else if (n <= 9) cols = 3;
  else cols = 4;

  const rows = Math.ceil(n / cols);

  // Calcul taille des nodes pour remplir l'espace disponible
  const availW = canvasW - 2 * MARGIN_X;
  const availH = canvasH - MARGIN_TOP - MARGIN_BOTTOM;

  const nodeW = Math.min(NODE_W, (availW - (cols - 1) * GAP_X) / cols);
  const nodeH = Math.min(NODE_H, (availH - (rows - 1) * GAP_Y) / rows);

  // Largeur totale de la grille
  const gridW = cols * nodeW + (cols - 1) * GAP_X;
  const gridH = rows * nodeH + (rows - 1) * GAP_Y;

  // Offset pour centrer la grille
  const offsetX = MARGIN_X + (availW - gridW) / 2;
  const offsetY = MARGIN_TOP + (availH - gridH) / 2;

  data.nodes.forEach((node, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);

    // Centrer la dernière ligne si elle n'est pas complète
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
 * Utilisé pour que les flèches partent/arrivent au bord du rectangle.
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

  // Intersection avec le rectangle
  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);
  const halfW = pos.w / 2;
  const halfH = pos.h / 2;

  let scale: number;
  if (absDx * halfH > absDy * halfW) {
    // Intersection avec bord gauche ou droit
    scale = halfW / absDx;
  } else {
    // Intersection avec bord haut ou bas
    scale = halfH / absDy;
  }

  return {
    x: cx + dx * scale,
    y: cy + dy * scale,
  };
}
