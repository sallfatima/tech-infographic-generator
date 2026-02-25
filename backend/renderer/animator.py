"""GIF animation generator - data flow animation with colored dots along arrows.

The complete diagram is shown on every frame. Colored dots/particles travel
along the arrow paths between nodes to visualize data flow through the system.
"""

from __future__ import annotations

import math
import time
from pathlib import Path
from collections import defaultdict

from PIL import Image, ImageDraw

from ..models.infographic import InfographicData, InfographicType
from .engine import ProRenderer
from .themes import hex_to_rgb, get_theme
from .layout import (
    layout_grid, layout_flow_horizontal, layout_layered,
    get_node_center, get_node_bottom, get_node_top,
    get_node_right, get_node_left,
)


class InfographicAnimator:
    """Generate animated GIFs with data flow visualization.

    The complete infographic is rendered once as a base image.
    On each frame, colored dots travel along the arrow paths to
    animate data flowing through the diagram connections.
    """

    def __init__(self, theme_name: str = "tech_blue"):
        self.renderer = ProRenderer(theme_name)
        self.theme_name = theme_name
        self.theme = get_theme(theme_name)

    def generate_gif(
        self,
        data: InfographicData,
        width: int = 1400,
        height: int = 900,
        frame_duration: int = 120,
        final_hold: int = 1500,
        output_path: str | None = None,
        n_frames: int = 30,
    ) -> Path:
        """Generate an animated GIF with data flow dots.

        Args:
            data: The structured infographic data.
            width: Frame width in pixels.
            height: Frame height in pixels.
            frame_duration: Milliseconds per frame (120ms = smooth animation).
            final_hold: Milliseconds to hold the last frame before looping.
            output_path: Where to save. Auto-generated if None.
            n_frames: Number of animation frames (more = smoother, larger file).

        Returns:
            Path to the saved GIF file.
        """
        frames = self._build_flow_frames(data, width, height, n_frames)

        if not frames:
            # Fallback: single static frame
            img = self.renderer.render_to_image(data, width, height)
            frames = [img]

        if output_path is None:
            Path("output").mkdir(exist_ok=True)
            output_path = f"output/animated_{int(time.time())}.gif"

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # All frames same duration, last frame held longer
        durations = [frame_duration] * len(frames)
        if durations:
            durations[-1] = final_hold

        # Save as animated GIF
        frames[0].save(
            str(path),
            format="GIF",
            save_all=True,
            append_images=frames[1:] if len(frames) > 1 else [],
            duration=durations,
            loop=0,
            optimize=True,
        )

        return path

    def _build_flow_frames(
        self,
        data: InfographicData,
        width: int,
        height: int,
        n_frames: int = 30,
    ) -> list[Image.Image]:
        """Build frames with animated dots flowing along arrow paths.

        1. Render complete diagram as base image
        2. Extract arrow paths (start/end points for each connection)
        3. For each frame, draw dots at interpolated positions along paths
        """
        # Step 1: Render the complete static diagram
        base_img = self.renderer.render_to_image(data, width, height)
        base_img = base_img.convert("RGB")

        # Step 2: Extract arrow paths between connected nodes
        arrow_paths = self._extract_arrow_paths(data, width, height)

        if not arrow_paths:
            # No connections — return just the static image
            return [base_img]

        # Step 3: Determine dot colors for each path
        path_colors = self._get_path_colors(data, arrow_paths)

        # Step 4: Build animated frames
        frames = []
        for frame_idx in range(n_frames):
            t = frame_idx / n_frames  # 0.0 to ~1.0
            frame = self._draw_flow_frame(
                base_img, arrow_paths, path_colors, t, n_frames,
            )
            frames.append(frame)

        return frames

    def _extract_arrow_paths(
        self,
        data: InfographicData,
        width: int,
        height: int,
    ) -> list[dict]:
        """Extract arrow path segments from the infographic layout.

        Returns a list of dicts, each with:
        - 'from_node': source node id
        - 'to_node': target node id
        - 'waypoints': list of (x,y) points forming the path
        - 'index': connection order (for staggering animation)
        """
        paths = []

        # We need to compute node positions using the same layout logic
        # as the renderers. This depends on the infographic type.
        positions = self._compute_positions(data, width, height)

        if not positions:
            return paths

        # For types with explicit connections (architecture, concept_map)
        if data.connections:
            node_layer_map = {}
            for li, layer in enumerate(data.layers):
                for nid in layer.nodes:
                    node_layer_map[nid] = li

            outgoing_down = defaultdict(list)
            outgoing_up = defaultdict(list)
            for conn in data.connections:
                fl = node_layer_map.get(conn.from_node, 0)
                tl = node_layer_map.get(conn.to_node, 0)
                if fl < tl:
                    outgoing_down[conn.from_node].append(conn.to_node)
                elif fl > tl:
                    outgoing_up[conn.from_node].append(conn.to_node)

            for ci, conn in enumerate(data.connections):
                if conn.from_node not in positions or conn.to_node not in positions:
                    continue

                from_pos = positions[conn.from_node]
                to_pos = positions[conn.to_node]
                from_layer = node_layer_map.get(conn.from_node, 0)
                to_layer = node_layer_map.get(conn.to_node, 0)

                # Compute start/end points (same logic as architecture renderer)
                if from_layer < to_layer:
                    siblings = outgoing_down[conn.from_node]
                    n_out = len(siblings)
                    if n_out > 1 and conn.to_node in siblings:
                        idx = siblings.index(conn.to_node)
                        fx, fy, fw, fh = from_pos
                        spread = min(fw - 20, n_out * 30)
                        offset = -spread // 2 + idx * (spread // max(n_out - 1, 1))
                        start = (fx + fw // 2 + offset, fy + fh)
                    else:
                        start = get_node_bottom(from_pos)
                    end = get_node_top(to_pos)
                elif from_layer > to_layer:
                    siblings = outgoing_up[conn.from_node]
                    n_out = len(siblings)
                    if n_out > 1 and conn.to_node in siblings:
                        idx = siblings.index(conn.to_node)
                        fx, fy, fw, fh = from_pos
                        spread = min(fw - 20, n_out * 30)
                        offset = -spread // 2 + idx * (spread // max(n_out - 1, 1))
                        start = (fx + fw // 2 + offset, fy)
                    else:
                        start = get_node_top(from_pos)
                    end = get_node_bottom(to_pos)
                else:
                    # Same layer — horizontal
                    from_cx = from_pos[0] + from_pos[2] // 2
                    to_cx = to_pos[0] + to_pos[2] // 2
                    if from_cx < to_cx:
                        start = get_node_right(from_pos)
                        end = get_node_left(to_pos)
                    else:
                        start = get_node_left(from_pos)
                        end = get_node_right(to_pos)

                waypoints = [start, end]
                paths.append({
                    "from_node": conn.from_node,
                    "to_node": conn.to_node,
                    "waypoints": waypoints,
                    "index": ci,
                })

        # For sequential types (process, pipeline, flowchart) without explicit connections
        # → create implicit sequential arrows between consecutive nodes
        if not paths and len(data.nodes) > 1:
            paths = self._extract_sequential_paths(data, positions)

        return paths

    def _extract_sequential_paths(
        self,
        data: InfographicData,
        positions: dict,
    ) -> list[dict]:
        """Extract sequential arrow paths for process/pipeline/flowchart types.

        These types connect nodes in order (node[0] → node[1] → node[2] → ...).
        """
        paths = []
        node_ids = [n.id for n in data.nodes]

        # Determine grid layout columns for process type
        is_grid = data.type in (
            InfographicType.PROCESS,
            InfographicType.INFOGRAPHIC,
            InfographicType.TIMELINE,
        )

        if is_grid:
            n = len(node_ids)
            cols = 3 if n > 4 else 2 if n > 2 else 1
        else:
            cols = len(node_ids)  # All in one row (horizontal flow)

        for i in range(len(node_ids) - 1):
            nid = node_ids[i]
            next_nid = node_ids[i + 1]
            if nid not in positions or next_nid not in positions:
                continue

            x1, y1, w1, h1 = positions[nid]
            x2, y2, w2, h2 = positions[next_nid]

            if is_grid:
                col1, col2 = i % cols, (i + 1) % cols
                row1, row2 = i // cols, (i + 1) // cols

                if row1 == row2:
                    # Same row → horizontal
                    start = (x1 + w1, y1 + h1 // 2)
                    end = (x2, y2 + h2 // 2)
                else:
                    # Different row → vertical
                    start = (x1 + w1 // 2, y1 + h1)
                    end = (x2 + w2 // 2, y2)
            else:
                # Horizontal flow (pipeline, flowchart)
                start = (x1 + w1, y1 + h1 // 2)
                end = (x2, y2 + h2 // 2)

            paths.append({
                "from_node": nid,
                "to_node": next_nid,
                "waypoints": [start, end],
                "index": i,
            })

        return paths

    def _compute_positions(
        self,
        data: InfographicData,
        width: int,
        height: int,
    ) -> dict:
        """Compute node positions using the same layout logic as renderers."""
        margin = 50
        header_h = 100 if data.subtitle else 80

        if data.type == InfographicType.ARCHITECTURE and data.layers:
            layers_data = [
                {"name": l.name, "nodes": l.nodes, "color": l.color}
                for l in data.layers
            ]
            return layout_layered(
                layers_data, data.nodes, width, height, margin, header_h,
            )

        node_ids = [n.id for n in data.nodes]

        if data.type in (
            InfographicType.PROCESS,
            InfographicType.INFOGRAPHIC,
            InfographicType.TIMELINE,
        ):
            cols = 3 if len(node_ids) > 4 else 2 if len(node_ids) > 2 else 1
            return layout_grid(
                node_ids, width, height, cols=cols, header_h=header_h,
            )

        if data.type in (
            InfographicType.FLOWCHART,
            InfographicType.PIPELINE,
            InfographicType.RAG_PIPELINE,
            InfographicType.MULTI_AGENT,
        ):
            return layout_flow_horizontal(
                node_ids, width, height, header_h=header_h,
            )

        # Fallback: grid layout
        cols = 3 if len(node_ids) > 4 else 2 if len(node_ids) > 2 else 1
        return layout_grid(
            node_ids, width, height, cols=cols, header_h=header_h,
        )

    def _get_path_colors(
        self,
        data: InfographicData,
        arrow_paths: list[dict],
    ) -> list[str]:
        """Determine the color for each arrow path's dot.

        Uses section colors from the theme, or node colors, cycling through
        a vivid palette for visual variety.
        """
        section_colors = self.theme.get("section_colors", [])
        node_colors = self.theme.get("node_colors", [self.theme.get("accent", "#5B8DEF")])

        # Vivid dot palette — pops against any background
        dot_palette = [
            "#FF6B6B",  # coral red
            "#4ECDC4",  # teal
            "#FFD93D",  # golden yellow
            "#6BCB77",  # green
            "#4D96FF",  # blue
            "#FF8C42",  # orange
            "#C77DFF",  # purple
            "#00D2FF",  # cyan
        ]

        colors = []
        for i, path in enumerate(arrow_paths):
            if section_colors:
                sc = section_colors[i % len(section_colors)]
                colors.append(sc.get("border", dot_palette[i % len(dot_palette)]))
            elif node_colors:
                colors.append(node_colors[i % len(node_colors)])
            else:
                colors.append(dot_palette[i % len(dot_palette)])

        return colors

    def _draw_flow_frame(
        self,
        base_img: Image.Image,
        arrow_paths: list[dict],
        path_colors: list[str],
        t: float,
        n_frames: int,
    ) -> Image.Image:
        """Draw a single animation frame with dots at position t along paths.

        Each connection gets multiple dots that travel from start to end.
        The dots are staggered so connections activate sequentially,
        creating a cascading data flow effect.

        Args:
            base_img: The complete static diagram.
            arrow_paths: List of arrow path dicts.
            path_colors: Color for each path's dots.
            t: Animation progress (0.0 to 1.0).
            n_frames: Total number of frames.
        """
        # Copy the base image — we draw dots on top
        frame = base_img.copy()
        draw = ImageDraw.Draw(frame)

        n_paths = len(arrow_paths)
        if n_paths == 0:
            return frame

        # Number of dots per path
        dots_per_path = 3

        # Each path has a stagger: path 0 starts at t=0, path 1 at t=stagger, etc.
        # This creates a cascading "wave" of dots flowing through the diagram.
        # All paths complete within one animation cycle so the loop is seamless.
        stagger = 0.15  # Delay between consecutive paths

        for pi, path in enumerate(arrow_paths):
            waypoints = path["waypoints"]
            color_hex = path_colors[pi] if pi < len(path_colors) else "#5B8DEF"
            color_rgb = hex_to_rgb(color_hex)

            # Brighter version for the glow/halo
            glow_rgb = tuple(min(255, c + 80) for c in color_rgb)

            # Path-specific time offset (cascading)
            path_offset = pi * stagger
            # Local time for this path, wrapping around
            local_t = (t - path_offset) % 1.0

            for dot_idx in range(dots_per_path):
                # Space dots evenly along the path with phase offset
                dot_phase = dot_idx / dots_per_path
                dot_t = (local_t + dot_phase) % 1.0

                # Dots travel from 0.0 (start) to 1.0 (end)
                # Only show dot if it's actively traveling (not at endpoint)
                if dot_t < 0.02 or dot_t > 0.98:
                    continue

                # Interpolate position along the polyline waypoints
                pos = self._interpolate_along_path(waypoints, dot_t)
                if pos is None:
                    continue

                px, py = pos

                # Size varies — lead dot is bigger, trailing dots are smaller
                # Also pulse slightly based on time
                pulse = 0.8 + 0.2 * math.sin(dot_t * math.pi)
                base_radius = 7 if dot_idx == 0 else 5
                radius = int(base_radius * pulse)

                # Draw glow (larger, semi-transparent effect via lighter color)
                glow_r = radius + 4
                draw.ellipse(
                    (px - glow_r, py - glow_r, px + glow_r, py + glow_r),
                    fill=glow_rgb,
                )

                # Draw the dot
                draw.ellipse(
                    (px - radius, py - radius, px + radius, py + radius),
                    fill=color_rgb,
                )

                # Bright center highlight
                highlight_r = max(2, radius - 3)
                highlight_rgb = tuple(min(255, c + 120) for c in color_rgb)
                draw.ellipse(
                    (px - highlight_r, py - highlight_r,
                     px + highlight_r, py + highlight_r),
                    fill=highlight_rgb,
                )

        return frame

    def _interpolate_along_path(
        self,
        waypoints: list[tuple[int, int]],
        t: float,
    ) -> tuple[int, int] | None:
        """Interpolate a position along a polyline path.

        Args:
            waypoints: List of (x, y) points forming the path.
            t: Parameter from 0.0 (start) to 1.0 (end).

        Returns:
            (x, y) position at parameter t, or None if path is empty.
        """
        if len(waypoints) < 2:
            return None

        # Calculate total path length
        segment_lengths = []
        total_length = 0.0
        for i in range(len(waypoints) - 1):
            dx = waypoints[i + 1][0] - waypoints[i][0]
            dy = waypoints[i + 1][1] - waypoints[i][1]
            seg_len = math.sqrt(dx * dx + dy * dy)
            segment_lengths.append(seg_len)
            total_length += seg_len

        if total_length < 1:
            return waypoints[0]

        # Find position at distance = t * total_length
        target_dist = t * total_length
        accumulated = 0.0

        for i, seg_len in enumerate(segment_lengths):
            if accumulated + seg_len >= target_dist:
                # Position is on this segment
                if seg_len < 1:
                    return waypoints[i]
                local_t = (target_dist - accumulated) / seg_len
                x = int(waypoints[i][0] + local_t * (waypoints[i + 1][0] - waypoints[i][0]))
                y = int(waypoints[i][1] + local_t * (waypoints[i + 1][1] - waypoints[i][1]))
                return (x, y)
            accumulated += seg_len

        # Fallback: return last point
        return waypoints[-1]
