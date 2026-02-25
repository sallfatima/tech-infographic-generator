/**
 * DiagramCanvas — SVG container principal avec rendu Rough.js.
 *
 * Phase 4 : Framer Motion animations (progressive node/edge appearance).
 * Les positions viennent du Zustand store (pas du layout local).
 */

import { useMemo, useRef, useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { RoughSVG } from "roughjs/bin/svg";
import { createRoughSvg } from "../../lib/roughRenderer";
import { getTheme } from "../../lib/themes";
import { useDiagramState } from "../../hooks/useDiagramState";
import RoughNode from "./RoughNode";
import RoughEdge from "./RoughEdge";
import ZoneBox from "./ZoneBox";

/** Dimensions du canvas SVG. */
const CANVAS_W = 1400;
const CANVAS_H = 900;

/** Variants Framer Motion pour les nodes (apparition progressive). */
const nodeVariants = {
  hidden: { opacity: 0, scale: 0.7 },
  visible: (i: number) => ({
    opacity: 1,
    scale: 1,
    transition: {
      delay: i * 0.08,
      duration: 0.4,
      ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number],
    },
  }),
  exit: { opacity: 0, scale: 0.8, transition: { duration: 0.2 } },
};

/** Variants pour les edges (apparition après les nodes). */
const edgeVariants = {
  hidden: { opacity: 0 },
  visible: (i: number) => ({
    opacity: 1,
    transition: {
      delay: 0.3 + i * 0.06,
      duration: 0.3,
    },
  }),
};

export default function DiagramCanvas() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [rc, setRc] = useState<RoughSVG | null>(null);

  // Store
  const data = useDiagramState((s) => s.data);
  const positions = useDiagramState((s) => s.positions);
  const selectedNodeId = useDiagramState((s) => s.selectedNodeId);
  const themeName = useDiagramState((s) => s.themeName);
  const zoom = useDiagramState((s) => s.zoom);
  const selectNode = useDiagramState((s) => s.selectNode);
  const updateNodePosition = useDiagramState((s) => s.updateNodePosition);
  const updateNodeLabel = useDiagramState((s) => s.updateNodeLabel);

  const theme = useMemo(() => getTheme(themeName), [themeName]);

  // ─── Drag state (local, pas dans le store) ───────────────────────
  const dragRef = useRef<{
    nodeId: string;
    offsetX: number;
    offsetY: number;
  } | null>(null);

  // ─── Inline edit state ────────────────────────────────────────────
  const [editingNodeId, setEditingNodeId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialiser Rough.js
  useEffect(() => {
    if (svgRef.current) {
      setRc(createRoughSvg(svgRef.current));
    }
  }, []);

  // Focus l'input quand on commence à éditer
  useEffect(() => {
    if (editingNodeId && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editingNodeId]);

  // ─── SVG coordinate conversion ───────────────────────────────────
  const svgPoint = useCallback(
    (clientX: number, clientY: number) => {
      const svg = svgRef.current;
      if (!svg) return { x: 0, y: 0 };
      const pt = svg.createSVGPoint();
      pt.x = clientX;
      pt.y = clientY;
      const ctm = svg.getScreenCTM();
      if (!ctm) return { x: 0, y: 0 };
      const svgP = pt.matrixTransform(ctm.inverse());
      return { x: svgP.x, y: svgP.y };
    },
    [],
  );

  // ─── Drag handlers ────────────────────────────────────────────────
  const handleDragStart = useCallback(
    (nodeId: string, e: React.MouseEvent) => {
      const pos = positions[nodeId];
      if (!pos) return;
      const svgP = svgPoint(e.clientX, e.clientY);
      dragRef.current = {
        nodeId,
        offsetX: svgP.x - pos.x,
        offsetY: svgP.y - pos.y,
      };
    },
    [positions, svgPoint],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!dragRef.current) return;
      const svgP = svgPoint(e.clientX, e.clientY);
      const newX = svgP.x - dragRef.current.offsetX;
      const newY = svgP.y - dragRef.current.offsetY;
      updateNodePosition(dragRef.current.nodeId, newX, newY);
    },
    [svgPoint, updateNodePosition],
  );

  const handleMouseUp = useCallback(() => {
    dragRef.current = null;
  }, []);

  // ─── Background click → deselect ─────────────────────────────────
  const handleBgClick = useCallback(
    (e: React.MouseEvent) => {
      if (
        e.target === svgRef.current ||
        (e.target as SVGElement).tagName === "rect"
      ) {
        selectNode(null);
      }
    },
    [selectNode],
  );

  // ─── Double-click → inline edit ───────────────────────────────────
  const handleDoubleClick = useCallback(
    (nodeId: string) => {
      const node = data?.nodes.find((n) => n.id === nodeId);
      if (!node) return;
      setEditingNodeId(nodeId);
      setEditText(node.label);
    },
    [data],
  );

  const commitEdit = useCallback(() => {
    if (editingNodeId && editText.trim()) {
      updateNodeLabel(editingNodeId, editText.trim());
    }
    setEditingNodeId(null);
  }, [editingNodeId, editText, updateNodeLabel]);

  const cancelEdit = useCallback(() => {
    setEditingNodeId(null);
  }, []);

  if (!data) return null;

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${CANVAS_W} ${CANVAS_H}`}
        className="w-full h-full rounded-xl shadow-lg"
        style={{
          maxHeight: "80vh",
          backgroundColor: theme.bg,
          transform: `scale(${zoom})`,
          transformOrigin: "center center",
        }}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={handleBgClick}
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

        {/* Zones de groupement */}
        {data.zones.map((zone, i) => {
          const zoneNodeIds = zone.nodes ?? [];
          const zonePositions = zoneNodeIds
            .map((id: string) => positions[id])
            .filter(Boolean);

          if (zonePositions.length === 0) return null;

          const minX = Math.min(...zonePositions.map((p) => p.x)) - 20;
          const minY = Math.min(...zonePositions.map((p) => p.y)) - 30;
          const maxX =
            Math.max(...zonePositions.map((p) => p.x + p.w)) + 20;
          const maxY =
            Math.max(...zonePositions.map((p) => p.y + p.h)) + 20;

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

        {/* Connections avec animation Framer Motion */}
        <AnimatePresence>
          {rc &&
            data.connections.map((conn, i) => {
              const fromPos = positions[conn.from_node];
              const toPos = positions[conn.to_node];
              if (!fromPos || !toPos) return null;

              const sc = theme.sectionColors[i % theme.sectionColors.length];

              return (
                <motion.g
                  key={`edge-${i}`}
                  custom={i}
                  variants={edgeVariants}
                  initial="hidden"
                  animate="visible"
                >
                  <RoughEdge
                    rc={rc}
                    fromPos={fromPos}
                    toPos={toPos}
                    label={conn.label}
                    style={conn.style}
                    index={i}
                    theme={theme}
                    borderColor={sc.border}
                  />
                </motion.g>
              );
            })}
        </AnimatePresence>

        {/* Nodes avec animation Framer Motion */}
        <AnimatePresence>
          {rc &&
            data.nodes.map((node, i) => {
              const pos = positions[node.id];
              if (!pos) return null;

              const sc = theme.sectionColors[i % theme.sectionColors.length];

              return (
                <motion.g
                  key={node.id}
                  custom={i}
                  variants={nodeVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                >
                  <RoughNode
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
                    isSelected={selectedNodeId === node.id}
                    onSelect={selectNode}
                    onDragStart={handleDragStart}
                    onDoubleClick={handleDoubleClick}
                  />
                </motion.g>
              );
            })}
        </AnimatePresence>
      </svg>

      {/* Overlay input pour édition inline */}
      {editingNodeId && (
        <div
          className="absolute pointer-events-auto"
          style={{
            left: "50%",
            top: "50%",
            transform: `translate(-50%, -50%)`,
          }}
        >
          <div className="bg-white rounded-lg shadow-xl border border-blue-400 p-2 flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") commitEdit();
                if (e.key === "Escape") cancelEdit();
              }}
              onBlur={commitEdit}
              className="px-3 py-1.5 text-sm rounded border border-slate-200
                         focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400
                         min-w-[200px]"
              placeholder="Nom du node..."
            />
            <button
              onMouseDown={(e) => {
                e.preventDefault();
                commitEdit();
              }}
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700
                         transition-colors cursor-pointer"
            >
              OK
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
