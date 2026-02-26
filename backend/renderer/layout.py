"""Layout algorithms for positioning nodes on the canvas.

Content-aware: node dimensions adapt to their description length,
so cards with more text are taller and cards with no text stay compact.
"""

from __future__ import annotations

import math
from PIL import Image, ImageDraw

from .typography import get_font, text_size, wrap_text


# ---------------------------------------------------------------------------
# Content measurement helpers
# ---------------------------------------------------------------------------

def measure_node_content_height(
    description: str | None,
    card_w: int,
    has_icon: bool = False,
    min_h: int = 60,
    max_h: int = 300,
    is_header_style: bool = False,
    is_pipeline: bool = False,
) -> int:
    """Measure the ideal card height for a node based on its content.

    This looks at the description text, wraps it at the given card width,
    and computes the minimum height needed to show all content without
    wasted space.

    Args:
        is_pipeline: If True, accounts for extra vertical elements
            (stage label, bigger icon area) used in pipeline renderers.

    Returns a height in pixels, clamped between min_h and max_h.
    """
    # We need a temporary draw context to measure text
    tmp = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(tmp)

    if is_pipeline:
        # Pipeline layout: stage label (20) + icon area (50) + label (22) + padding
        header_h = 20  # "STAGE N" label
        icon_h = 50 if has_icon else 15
        label_h = 24
        padding = 24
    elif is_header_style:
        # Guidebook style with header band
        header_h = 34
        icon_h = 28 if has_icon else 0
        label_h = 22
        padding = 16
    else:
        # Whiteboard/dark draw_node style — match actual rendering:
        # accent bar (9px) + top padding (18px) + icon (28+6) + label (lh+4) + bottom (6)
        header_h = 18  # accent bar + top padding
        icon_h = 34 if has_icon else 0  # icon_size(28) + gap(6)
        label_h = 26  # label text + gap(4)
        padding = 12  # bottom margin

    base_h = header_h + icon_h + label_h + padding

    if not description:
        return max(min_h, base_h)

    # Measure wrapped description — use a conservative font size estimate.
    # The actual draw_node() uses desc_fs = min(12, max(9, h // 8)),
    # and draw_node_with_header() uses desc_fs = min(11, max(9, h // 10)).
    # Since we don't know h yet, we estimate with a larger font to be safe
    # (overestimate height → cards are slightly taller → no text overflow).
    text_w = card_w - 24  # inner padding (padding * 2 = 24)
    if is_header_style:
        desc_fs = 11  # match draw_node_with_header max
        line_h = int(desc_fs * 1.35)  # match draw_node_with_header
    else:
        desc_fs = 12  # match draw_node max
        line_h = int(desc_fs * 1.4)  # match draw_node
    desc_font = get_font(desc_fs, "regular")

    lines = wrap_text(draw, description, desc_font, text_w)
    desc_h = len(lines) * line_h + 6  # +6 margin

    needed = base_h + desc_h
    return max(min_h, min(needed, max_h))


def measure_content_heights(
    nodes,
    card_w: int,
    is_header_style: bool = False,
    is_pipeline: bool = False,
    min_h: int = 60,
    max_h: int = 300,
) -> dict[str, int]:
    """Measure ideal height for each node in a list.

    Returns {node_id: ideal_height_px}.
    """
    heights = {}
    for node in nodes:
        h = measure_node_content_height(
            description=node.description,
            card_w=card_w,
            has_icon=node.icon is not None,
            min_h=min_h,
            max_h=max_h,
            is_header_style=is_header_style,
            is_pipeline=is_pipeline,
        )
        heights[node.id] = h
    return heights


# ---------------------------------------------------------------------------
# Layout functions
# ---------------------------------------------------------------------------

def layout_layered(
    layers: list[dict],
    nodes: list[dict],
    canvas_w: int,
    canvas_h: int,
    margin: int = 60,
    header_h: int = 100,
) -> dict[str, tuple[int, int, int, int]]:
    """Layered architecture layout: horizontal layers stacked vertically.

    Returns dict of {node_id: (x, y, w, h)} bounding boxes.
    """
    positions = {}
    if not layers:
        return positions

    n_layers = len(layers)
    available_h = canvas_h - header_h - margin
    layer_h = available_h // n_layers
    # Reserve space for step number badges (radius ~16px) + arrow labels (~20px)
    # + extra padding so arrows don't collide with node content
    label_reserve = 45
    layer_gap = max(30, label_reserve)
    # Map node ids to node objects so we can measure content per-layer.
    nodes_by_id = {getattr(n, "id", None): n for n in nodes}

    for li, layer in enumerate(layers):
        layer_y = header_h + li * layer_h
        node_ids = layer.get("nodes", [])
        n_nodes = len(node_ids)
        if n_nodes == 0:
            continue

        # Adaptive gap and width based on number of nodes
        usable_w = canvas_w - margin * 2
        if n_nodes <= 3:
            gap = 45
            max_node_w = 220
        elif n_nodes <= 5:
            gap = 30  # smaller gap for more nodes
            max_node_w = 200
        else:
            gap = 20
            max_node_w = 180

        node_w = min((usable_w - (n_nodes - 1) * gap) // max(n_nodes, 1), max_node_w)
        node_w = max(node_w, 100)  # minimum readable width
        total_nodes_w = n_nodes * node_w + (n_nodes - 1) * gap
        start_x = margin + (usable_w - total_nodes_w) // 2

        # Content-aware node height for this layer (helps avoid text overlap in dense
        # architecture cards with long descriptions).
        layer_nodes = [nodes_by_id[nid] for nid in node_ids if nid in nodes_by_id]
        max_node_h = max(70, min(220, layer_h - label_reserve - 16))
        if layer_nodes:
            measured = measure_content_heights(
                layer_nodes,
                node_w,
                is_header_style=True,
                min_h=70,
                max_h=max_node_h,
            )
            node_h = max(measured.values()) if measured else max_node_h
        else:
            node_h = min(max_node_h, 160)
        node_h = max(70, min(node_h, max_node_h))

        # Reserve a little more space near the top for layer labels / arrows.
        top_reserve = min(max(label_reserve, 34), max(34, layer_h // 2))
        bottom_reserve = 12
        usable_layer_h = max(node_h, layer_h - top_reserve - bottom_reserve)
        node_y = layer_y + top_reserve + max(0, (usable_layer_h - node_h) // 2)

        for ni, nid in enumerate(node_ids):
            x = start_x + ni * (node_w + gap)
            positions[nid] = (x, node_y, node_w, node_h)

    return positions


def layout_flow_horizontal(
    node_ids: list[str],
    canvas_w: int,
    canvas_h: int,
    margin: int = 60,
    header_h: int = 80,
    nodes=None,
) -> dict[str, tuple[int, int, int, int]]:
    """Horizontal flow layout: left to right.

    If `nodes` are provided, stage height adapts to content.
    """
    positions = {}
    n = len(node_ids)
    if n == 0:
        return positions

    usable_w = canvas_w - margin * 2
    # Adaptive gap: enough room for numbered arrow badges (badge ~20px + label ~40px)
    # Minimum 65px gap ensures step numbers + labels don't overlap nodes
    gap = max(65, min(85, (usable_w - n * 120) // max(n - 1, 1)))
    node_w = min((usable_w - (n - 1) * gap) // n, 200)

    # Content-aware height
    if nodes:
        content_heights = measure_content_heights(
            nodes, node_w, is_header_style=False, min_h=90, max_h=280,
        )
        # Use the tallest needed height (all stages same height for alignment)
        node_h = max(content_heights.values())
    else:
        node_h = min(120, (canvas_h - header_h - margin * 2))

    # Clamp to available space
    max_available = canvas_h - header_h - margin * 2
    node_h = min(node_h, max_available)

    total_w = n * node_w + (n - 1) * gap
    start_x = margin + (usable_w - total_w) // 2
    cy = header_h + (canvas_h - header_h - margin) // 2

    for i, nid in enumerate(node_ids):
        x = start_x + i * (node_w + gap)
        y = cy - node_h // 2
        positions[nid] = (x, y, node_w, node_h)

    return positions


def layout_flow_vertical(
    node_ids: list[str],
    canvas_w: int,
    canvas_h: int,
    margin: int = 60,
    header_h: int = 80,
) -> dict[str, tuple[int, int, int, int]]:
    """Vertical flow layout: top to bottom."""
    positions = {}
    n = len(node_ids)
    if n == 0:
        return positions

    usable_h = canvas_h - header_h - margin
    gap = 30
    node_h = min((usable_h - (n - 1) * gap) // n, 80)
    node_w = min(220, canvas_w - margin * 2)
    cx = canvas_w // 2

    for i, nid in enumerate(node_ids):
        x = cx - node_w // 2
        y = header_h + i * (node_h + gap)
        positions[nid] = (x, y, node_w, node_h)

    return positions


def layout_grid(
    node_ids: list[str],
    canvas_w: int,
    canvas_h: int,
    cols: int = 3,
    margin: int = 50,
    header_h: int = 100,
    row_gap: int = 40,
    col_gap: int = 20,
    footer_h: int = 28,
    nodes=None,
) -> dict[str, tuple[int, int, int, int]]:
    """Grid layout for cards — content-aware sizing with arrow gaps.

    If `nodes` are passed, card heights adapt per-row based on the longest
    description in that row. Rows with no descriptions stay compact.
    """
    positions = {}
    n = len(node_ids)
    if n == 0:
        return positions

    cols = min(cols, n)
    rows = math.ceil(n / cols)
    usable_w = canvas_w - margin * 2
    usable_h = canvas_h - header_h - footer_h
    node_w = (usable_w - (cols - 1) * col_gap) // cols

    # --- Content-aware row heights ---
    if nodes:
        content_heights = measure_content_heights(
            nodes, node_w, is_header_style=True, min_h=70, max_h=250,
        )
        # Group by row — each row's height = max of its nodes
        row_heights = []
        for r in range(rows):
            row_node_ids = node_ids[r * cols: (r + 1) * cols]
            row_max_h = max(
                content_heights.get(nid, 100) for nid in row_node_ids
            )
            row_heights.append(row_max_h)

        # Check if total fits; if not, scale down proportionally
        total_rows_h = sum(row_heights)
        arrow_space = (rows - 1) * 70  # gap for numbered arrows + labels between rows
        available_for_cards = usable_h - arrow_space
        if total_rows_h > available_for_cards and available_for_cards > 0:
            scale = available_for_cards / total_rows_h
            row_heights = [max(60, int(h * scale)) for h in row_heights]
            total_rows_h = sum(row_heights)

        # Compute row gaps from leftover — keep compact, avoid huge whitespace
        leftover_h = usable_h - total_rows_h
        if rows > 1:
            # Cap gaps at 40px (was 80) to avoid massive whitespace
            actual_row_gap = max(row_gap, min(leftover_h // (rows + 1), 40))
        else:
            actual_row_gap = row_gap

        # Push grid toward top — minimal top margin
        total_grid_h = total_rows_h + (rows - 1) * actual_row_gap
        top_leftover = max(0, usable_h - total_grid_h)
        start_y = header_h + min(top_leftover // 8, 15)

        # Place nodes
        cum_y = start_y
        for r in range(rows):
            rh = row_heights[r]
            for c in range(cols):
                idx = r * cols + c
                if idx >= n:
                    break
                nid = node_ids[idx]
                x = margin + c * (node_w + col_gap)
                positions[nid] = (x, cum_y, node_w, rh)
            cum_y += rh + actual_row_gap

        return positions

    # --- Fallback: fixed heights (when nodes not provided) ---
    raw_h = (usable_h - (rows - 1) * row_gap) // rows
    max_h = {1: 300, 2: 200, 3: 140}.get(rows, 120)
    node_h = min(raw_h, max_h)

    total_cards_h = rows * node_h
    leftover_h = usable_h - total_cards_h
    if rows > 1:
        actual_row_gap = max(row_gap, leftover_h // (rows + 1))
        actual_row_gap = min(actual_row_gap, 40)
    else:
        actual_row_gap = row_gap

    total_grid_h = rows * node_h + (rows - 1) * actual_row_gap
    top_leftover = max(0, usable_h - total_grid_h)
    start_y = header_h + min(top_leftover // 8, 15)

    for i, nid in enumerate(node_ids):
        col = i % cols
        row = i // cols
        x = margin + col * (node_w + col_gap)
        y = start_y + row * (node_h + actual_row_gap)
        positions[nid] = (x, y, node_w, node_h)

    return positions


def layout_columns(
    groups: list[list[str]],
    canvas_w: int,
    canvas_h: int,
    margin: int = 60,
    header_h: int = 80,
) -> dict[str, tuple[int, int, int, int]]:
    """Column layout for comparisons. Each group is a column."""
    positions = {}
    n_cols = len(groups)
    if n_cols == 0:
        return positions

    gap = 30
    usable_w = canvas_w - margin * 2
    col_w = (usable_w - (n_cols - 1) * gap) // n_cols

    for ci, group in enumerate(groups):
        col_x = margin + ci * (col_w + gap)
        n_items = len(group)
        item_gap = 15
        usable_h = canvas_h - header_h - margin - 60  # 60 for column header
        item_h = min((usable_h - (n_items - 1) * item_gap) // max(n_items, 1), 100)

        for ri, nid in enumerate(group):
            x = col_x
            y = header_h + 60 + ri * (item_h + item_gap)
            positions[nid] = (x, y, col_w, item_h)

    return positions


def layout_radial(
    center_id: str,
    outer_ids: list[str],
    canvas_w: int,
    canvas_h: int,
    header_h: int = 80,
) -> dict[str, tuple[int, int, int, int]]:
    """Radial/concept-map layout: center node with surrounding nodes."""
    positions = {}
    cx = canvas_w // 2
    cy = header_h + (canvas_h - header_h) // 2
    center_w, center_h = 200, 120
    positions[center_id] = (cx - center_w // 2, cy - center_h // 2, center_w, center_h)

    n = len(outer_ids)
    if n == 0:
        return positions

    # Adapt radius and node size to number of outer nodes
    # Bigger nodes = more room for descriptions
    available = min(canvas_w, canvas_h - header_h)
    if n <= 4:
        radius = available // 3
        node_w, node_h = 220, 130
    elif n <= 6:
        radius = int(available * 0.38)
        node_w, node_h = 200, 120
    else:
        radius = int(available * 0.42)
        node_w, node_h = 185, 110

    # Clamp so nodes don't go offscreen
    max_radius = min(
        (canvas_w - node_w - 40) // 2,
        (canvas_h - header_h - node_h - 40) // 2,
    )
    radius = min(radius, max_radius)

    for i, nid in enumerate(outer_ids):
        angle = (2 * math.pi * i) / n - math.pi / 2
        nx = int(cx + radius * math.cos(angle)) - node_w // 2
        ny = int(cy + radius * math.sin(angle)) - node_h // 2
        # Clamp to canvas bounds
        nx = max(20, min(nx, canvas_w - node_w - 20))
        ny = max(header_h + 10, min(ny, canvas_h - node_h - 20))
        positions[nid] = (nx, ny, node_w, node_h)

    return positions


def get_node_center(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    """Get the center point of a node's bounding box."""
    x, y, w, h = pos
    return (x + w // 2, y + h // 2)


def get_node_edge(
    pos: tuple[int, int, int, int],
    target: tuple[int, int],
) -> tuple[int, int]:
    """Get the edge point of a node closest to a target point."""
    x, y, w, h = pos
    cx, cy = x + w // 2, y + h // 2
    tx, ty = target

    dx = tx - cx
    dy = ty - cy

    if dx == 0 and dy == 0:
        return (cx, cy)

    if abs(dy) >= abs(dx):
        if dy > 0:
            return (cx, y + h)
        else:
            return (cx, y)
    else:
        if dx > 0:
            return (x + w, cy)
        else:
            return (x, cy)


def get_node_bottom(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    x, y, w, h = pos
    return (x + w // 2, y + h)


def get_node_top(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    x, y, w, h = pos
    return (x + w // 2, y)


def get_node_left(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    x, y, w, h = pos
    return (x, y + h // 2)


def get_node_right(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    x, y, w, h = pos
    return (x + w, y + h // 2)


# ---------------------------------------------------------------------------
# Force-directed layout (organic positioning)
# ---------------------------------------------------------------------------

def layout_force_directed(
    nodes: list,
    connections: list,
    canvas_w: int,
    canvas_h: int,
    margin: int = 80,
    header_h: int = 120,
    iterations: int = 150,
    node_w: int = 160,
    node_h: int = 90,
) -> dict[str, tuple[int, int, int, int]]:
    """Force-directed layout for organic, non-grid placement (SwirlAI style).

    Connected nodes attract, all nodes repel, same-group nodes cluster.
    Returns {node_id: (x, y, w, h)}.
    """
    import random
    random.seed(42)  # deterministic for same input

    n = len(nodes)
    if n == 0:
        return {}

    # Build adjacency from connections
    adj = set()
    for conn in connections:
        adj.add((conn.from_node, conn.to_node))
        adj.add((conn.to_node, conn.from_node))

    # Initialize positions: group-based clustering
    usable_w = canvas_w - 2 * margin
    usable_h = canvas_h - header_h - margin
    cx, cy = margin + usable_w // 2, header_h + usable_h // 2

    # Group nodes by zone/group
    groups: dict[str | None, list[int]] = {}
    for i, node in enumerate(nodes):
        g = getattr(node, 'zone', None) or getattr(node, 'group', None)
        groups.setdefault(g, []).append(i)

    # Seed positions by group
    pos_x = [0.0] * n
    pos_y = [0.0] * n
    g_keys = list(groups.keys())
    for gi, gk in enumerate(g_keys):
        # Spread groups around the center
        angle = 2 * math.pi * gi / max(len(g_keys), 1) - math.pi / 2
        gr = min(usable_w, usable_h) * 0.25
        gx = cx + gr * math.cos(angle) if gk is not None else cx
        gy = cy + gr * math.sin(angle) if gk is not None else cy
        for idx in groups[gk]:
            pos_x[idx] = gx + random.uniform(-40, 40)
            pos_y[idx] = gy + random.uniform(-40, 40)

    # Force simulation — scale repulsion with canvas size and node count
    # For few nodes on large canvas, we need stronger repulsion
    area_factor = (usable_w * usable_h) / max(n * n, 1)
    repulsion_k = max(8000.0, area_factor * 0.5)
    attraction_k = 0.012
    group_k = 0.03
    damping = 0.5

    node_ids = [node.id for node in nodes]
    id_to_idx = {nid: i for i, nid in enumerate(node_ids)}

    for iteration in range(iterations):
        # Cooling schedule
        temp = damping * (1 - iteration / iterations)
        if temp < 0.01:
            break

        fx = [0.0] * n
        fy = [0.0] * n

        # Repulsive forces (all pairs)
        for i in range(n):
            for j in range(i + 1, n):
                dx = pos_x[i] - pos_x[j]
                dy = pos_y[i] - pos_y[j]
                dist_sq = dx * dx + dy * dy + 1.0
                dist = math.sqrt(dist_sq)
                force = repulsion_k / dist_sq
                fdx = force * dx / dist
                fdy = force * dy / dist
                fx[i] += fdx
                fy[i] += fdy
                fx[j] -= fdx
                fy[j] -= fdy

        # Attractive forces (connected pairs)
        for conn in connections:
            i = id_to_idx.get(conn.from_node)
            j = id_to_idx.get(conn.to_node)
            if i is None or j is None:
                continue
            dx = pos_x[j] - pos_x[i]
            dy = pos_y[j] - pos_y[i]
            dist = math.sqrt(dx * dx + dy * dy + 1.0)
            force = attraction_k * dist
            fx[i] += force * dx / dist
            fy[i] += force * dy / dist
            fx[j] -= force * dx / dist
            fy[j] -= force * dy / dist

        # Group cohesion forces
        for gk, indices in groups.items():
            if gk is None or len(indices) < 2:
                continue
            gcx = sum(pos_x[i] for i in indices) / len(indices)
            gcy = sum(pos_y[i] for i in indices) / len(indices)
            for i in indices:
                fx[i] += group_k * (gcx - pos_x[i])
                fy[i] += group_k * (gcy - pos_y[i])

        # Apply forces with temperature
        for i in range(n):
            pos_x[i] += fx[i] * temp
            pos_y[i] += fy[i] * temp
            # Boundary clamping
            pos_x[i] = max(margin + node_w // 2, min(canvas_w - margin - node_w // 2, pos_x[i]))
            pos_y[i] = max(header_h + node_h // 2, min(canvas_h - margin - node_h // 2, pos_y[i]))

    # Post-process: expand to fill canvas if nodes are too clustered
    if n > 1:
        min_x = min(pos_x)
        max_x = max(pos_x)
        min_y = min(pos_y)
        max_y = max(pos_y)
        span_x = max_x - min_x
        span_y = max_y - min_y
        target_w = usable_w * 0.75
        target_h = usable_h * 0.70
        # Scale up if nodes use less than 60% of the canvas
        if span_x > 0 and span_x < target_w * 0.6:
            scale_x = target_w / max(span_x, 1)
            for i in range(n):
                pos_x[i] = cx + (pos_x[i] - cx) * scale_x
        if span_y > 0 and span_y < target_h * 0.6:
            scale_y = target_h / max(span_y, 1)
            for i in range(n):
                pos_y[i] = cy + (pos_y[i] - cy) * scale_y
        # Re-clamp to canvas bounds
        for i in range(n):
            pos_x[i] = max(margin + node_w // 2, min(canvas_w - margin - node_w // 2, pos_x[i]))
            pos_y[i] = max(header_h + node_h // 2, min(canvas_h - margin - node_h // 2, pos_y[i]))

    # Convert to bounding boxes
    positions = {}
    for i, nid in enumerate(node_ids):
        x = int(pos_x[i]) - node_w // 2
        y = int(pos_y[i]) - node_h // 2
        positions[nid] = (x, y, node_w, node_h)

    # Resolve overlaps as final pass
    positions = resolve_overlaps(positions, padding=15)
    return positions


def layout_zone_based(
    zones: list[dict],
    nodes: list,
    connections: list,
    canvas_w: int,
    canvas_h: int,
    margin: int = 60,
    header_h: int = 100,
    zone_padding: int = 35,
) -> tuple[dict[str, tuple], list[dict]]:
    """Zone-based layout: allocate regions per zone, place nodes within.

    Returns (node_positions, zone_rects) where zone_rects is
    [{"bbox": (x,y,w,h), "name": str, "color": str}].
    """
    if not zones:
        return {}, []

    n_zones = len(zones)
    usable_w = canvas_w - 2 * margin
    usable_h = canvas_h - header_h - margin

    # Decide arrangement: horizontal if <=3 zones, vertical if more
    if n_zones <= 3:
        # Horizontal arrangement
        zone_gap = 20
        zone_w = (usable_w - (n_zones - 1) * zone_gap) // n_zones
        zone_rects = []
        for zi, zone in enumerate(zones):
            zx = margin + zi * (zone_w + zone_gap)
            zy = header_h + 10
            zh = usable_h - 20
            zone_rects.append({
                "bbox": (zx, zy, zone_w, zh),
                "name": zone.get("name", f"Zone {zi + 1}"),
                "color": zone.get("color", "#2B7DE9"),
            })
    else:
        # 2-row arrangement
        cols = (n_zones + 1) // 2
        zone_gap = 20
        row_gap = 20
        zone_w = (usable_w - (cols - 1) * zone_gap) // cols
        row_h = (usable_h - row_gap) // 2
        zone_rects = []
        for zi, zone in enumerate(zones):
            r = zi // cols
            c = zi % cols
            zx = margin + c * (zone_w + zone_gap)
            zy = header_h + 10 + r * (row_h + row_gap)
            zone_rects.append({
                "bbox": (zx, zy, zone_w, row_h),
                "name": zone.get("name", f"Zone {zi + 1}"),
                "color": zone.get("color", "#2B7DE9"),
            })

    # Place nodes within their zone
    positions = {}
    zone_node_map = {z.get("name", f"Zone {i + 1}"): z.get("nodes", []) for i, z in enumerate(zones)}

    for zr in zone_rects:
        zname = zr["name"]
        node_ids_in_zone = zone_node_map.get(zname, [])
        if not node_ids_in_zone:
            continue

        bx, by, bw, bh = zr["bbox"]
        inner_x = bx + zone_padding
        inner_y = by + zone_padding + 25  # +25 for zone title
        inner_w = bw - 2 * zone_padding
        inner_h = bh - 2 * zone_padding - 25

        n_local = len(node_ids_in_zone)
        # Simple grid within zone
        if n_local <= 3:
            cols_local = n_local
        elif n_local <= 6:
            cols_local = 3
        else:
            cols_local = min(4, n_local)

        rows_local = math.ceil(n_local / cols_local)
        nw = min((inner_w - (cols_local - 1) * 12) // cols_local, 150)
        nh = min((inner_h - (rows_local - 1) * 12) // rows_local, 90)

        for ni, nid in enumerate(node_ids_in_zone):
            r = ni // cols_local
            c = ni % cols_local
            total_row_w = cols_local * nw + (cols_local - 1) * 12
            offset_x = (inner_w - total_row_w) // 2
            nx = inner_x + offset_x + c * (nw + 12)
            ny = inner_y + r * (nh + 12)
            positions[nid] = (nx, ny, nw, nh)

    return positions, zone_rects


def resolve_overlaps(
    positions: dict[str, tuple[int, int, int, int]],
    padding: int = 20,
    max_iterations: int = 50,
    canvas_w: int = 1400,
    canvas_h: int = 900,
) -> dict[str, tuple[int, int, int, int]]:
    """Post-process positions to eliminate bounding-box overlaps.

    Iteratively pushes overlapping nodes apart along the axis of least
    overlap. Clamps to canvas bounds.
    """
    ids = list(positions.keys())
    n = len(ids)
    if n < 2:
        return positions

    # Work with mutable copies
    pos = {nid: list(bbox) for nid, bbox in positions.items()}

    for _ in range(max_iterations):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                a = pos[ids[i]]
                b = pos[ids[j]]
                # Check overlap with padding
                ax1, ay1 = a[0] - padding, a[1] - padding
                ax2, ay2 = a[0] + a[2] + padding, a[1] + a[3] + padding
                bx1, by1 = b[0] - padding, b[1] - padding
                bx2, by2 = b[0] + b[2] + padding, b[1] + b[3] + padding

                if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
                    # Overlap detected — push apart
                    overlap_x = min(ax2 - bx1, bx2 - ax1)
                    overlap_y = min(ay2 - by1, by2 - ay1)

                    if overlap_x < overlap_y:
                        # Push horizontally
                        shift = overlap_x // 2 + 1
                        if a[0] < b[0]:
                            a[0] -= shift
                            b[0] += shift
                        else:
                            a[0] += shift
                            b[0] -= shift
                    else:
                        # Push vertically
                        shift = overlap_y // 2 + 1
                        if a[1] < b[1]:
                            a[1] -= shift
                            b[1] += shift
                        else:
                            a[1] += shift
                            b[1] -= shift

                    # Clamp
                    a[0] = max(10, min(a[0], canvas_w - a[2] - 10))
                    a[1] = max(10, min(a[1], canvas_h - a[3] - 10))
                    b[0] = max(10, min(b[0], canvas_w - b[2] - 10))
                    b[1] = max(10, min(b[1], canvas_h - b[3] - 10))
                    moved = True

        if not moved:
            break

    return {nid: tuple(bbox) for nid, bbox in pos.items()}
