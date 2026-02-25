/**
 * Wrapper Rough.js — fonctions de dessin hand-drawn.
 *
 * Rough.js (https://roughjs.com/) est la librairie utilisée par Excalidraw.
 * Elle génère des shapes SVG avec un style "dessiné à la main".
 */

import rough from "roughjs";
import type { RoughSVG } from "roughjs/bin/svg";
import type { Options } from "roughjs/bin/core";

// ─── Factory ────────────────────────────────────────────────────────

export function createRoughSvg(svgElement: SVGSVGElement): RoughSVG {
  return rough.svg(svgElement);
}

// ─── Shapes ─────────────────────────────────────────────────────────

export function drawRoughRect(
  rc: RoughSVG,
  x: number,
  y: number,
  w: number,
  h: number,
  opts: Options = {},
): SVGGElement {
  return rc.rectangle(x, y, w, h, opts) as unknown as SVGGElement;
}

export function drawRoughCircle(
  rc: RoughSVG,
  cx: number,
  cy: number,
  diameter: number,
  opts: Options = {},
): SVGGElement {
  return rc.circle(cx, cy, diameter, opts) as unknown as SVGGElement;
}

export function drawRoughEllipse(
  rc: RoughSVG,
  cx: number,
  cy: number,
  w: number,
  h: number,
  opts: Options = {},
): SVGGElement {
  return rc.ellipse(cx, cy, w, h, opts) as unknown as SVGGElement;
}

export function drawRoughPath(
  rc: RoughSVG,
  d: string,
  opts: Options = {},
): SVGGElement {
  return rc.path(d, opts) as unknown as SVGGElement;
}

export function drawRoughLine(
  rc: RoughSVG,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  opts: Options = {},
): SVGGElement {
  return rc.line(x1, y1, x2, y2, opts) as unknown as SVGGElement;
}

// ─── Shapes composites ─────────────────────────────────────────────

/**
 * Cylindre (pour databases) — ellipse top + rect body + ellipse bottom.
 */
export function drawRoughCylinder(
  rc: RoughSVG,
  x: number,
  y: number,
  w: number,
  h: number,
  opts: Options = {},
): SVGGElement {
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  const ellipseH = Math.min(h * 0.2, 20);
  const cx = x + w / 2;

  // Corps (rectangle sans top/bottom)
  const body = rc.path(
    `M ${x},${y + ellipseH / 2} L ${x},${y + h - ellipseH / 2} ` +
    `A ${w / 2},${ellipseH / 2} 0 0,0 ${x + w},${y + h - ellipseH / 2} ` +
    `L ${x + w},${y + ellipseH / 2}`,
    { ...opts, fill: undefined },
  );
  g.appendChild(body);

  // Ellipse du bas (avec fill)
  const bottom = rc.ellipse(cx, y + h - ellipseH / 2, w, ellipseH, opts);
  g.appendChild(bottom);

  // Ellipse du haut (avec fill)
  const top = rc.ellipse(cx, y + ellipseH / 2, w, ellipseH, opts);
  g.appendChild(top);

  return g;
}

/**
 * Hexagone — pour processing / compute nodes.
 */
export function drawRoughHexagon(
  rc: RoughSVG,
  cx: number,
  cy: number,
  size: number,
  opts: Options = {},
): SVGGElement {
  const points: [number, number][] = [];
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i - Math.PI / 6;
    points.push([
      cx + size * Math.cos(angle),
      cy + size * Math.sin(angle),
    ]);
  }

  const d = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p[0]},${p[1]}`)
    .join(" ") + " Z";

  return rc.path(d, opts) as unknown as SVGGElement;
}

/**
 * Nuage — path organique pour services cloud.
 */
export function drawRoughCloud(
  rc: RoughSVG,
  x: number,
  y: number,
  w: number,
  h: number,
  opts: Options = {},
): SVGGElement {
  const cx = x + w / 2;
  const cy = y + h / 2;
  const rx = w / 2;
  const ry = h / 2;

  // Path de nuage simplifiée avec bézier curves
  const d = `
    M ${cx - rx * 0.5},${cy + ry * 0.5}
    C ${cx - rx * 0.9},${cy + ry * 0.5} ${cx - rx},${cy} ${cx - rx * 0.7},${cy - ry * 0.3}
    C ${cx - rx * 0.5},${cy - ry * 0.8} ${cx - rx * 0.2},${cy - ry} ${cx + rx * 0.1},${cy - ry * 0.7}
    C ${cx + rx * 0.3},${cy - ry} ${cx + rx * 0.7},${cy - ry * 0.8} ${cx + rx * 0.8},${cy - ry * 0.3}
    C ${cx + rx},${cy} ${cx + rx * 0.9},${cy + ry * 0.4} ${cx + rx * 0.5},${cy + ry * 0.5}
    Z
  `.trim();

  return rc.path(d, opts) as unknown as SVGGElement;
}

/**
 * Diamant / losange — pour decision nodes.
 */
export function drawRoughDiamond(
  rc: RoughSVG,
  cx: number,
  cy: number,
  w: number,
  h: number,
  opts: Options = {},
): SVGGElement {
  const d = `M ${cx},${cy - h / 2} L ${cx + w / 2},${cy} L ${cx},${cy + h / 2} L ${cx - w / 2},${cy} Z`;
  return rc.path(d, opts) as unknown as SVGGElement;
}
