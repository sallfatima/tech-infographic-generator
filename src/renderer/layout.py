"""Layout algorithms for positioning nodes on the canvas.

Content-aware: node dimensions adapt to their description length,
so cards with more text are taller and cards with no text stay compact.
"""

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
    else:
        # Grid/card layout
        header_h = 32 if is_header_style else 10
        icon_h = 28 if has_icon else 0
        label_h = 22
        padding = 16

    base_h = header_h + icon_h + label_h + padding

    if not description:
        return max(min_h, base_h)

    # Measure wrapped description
    text_w = card_w - 28  # inner padding
    desc_fs = min(11, max(9, card_w // 30))
    desc_font = get_font(desc_fs, "regular")
    line_h = int(desc_fs * 1.4)

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
    layer_gap = 10
    node_h = min(layer_h - layer_gap * 2 - 20, 80)
    label_width = 100

    for li, layer in enumerate(layers):
        layer_y = header_h + li * layer_h
        node_ids = layer.get("nodes", [])
        n_nodes = len(node_ids)
        if n_nodes == 0:
            continue

        usable_w = canvas_w - margin * 2 - label_width
        node_w = min(usable_w // n_nodes - 20, 160)
        total_nodes_w = n_nodes * node_w + (n_nodes - 1) * 20
        start_x = margin + label_width + (usable_w - total_nodes_w) // 2

        for ni, nid in enumerate(node_ids):
            x = start_x + ni * (node_w + 20)
            y = layer_y + (layer_h - node_h) // 2
            positions[nid] = (x, y, node_w, node_h)

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
    gap = 50
    node_w = min((usable_w - (n - 1) * gap) // n, 200)

    # Content-aware height
    if nodes:
        content_heights = measure_content_heights(
            nodes, node_w, is_header_style=False, min_h=70, max_h=250,
        )
        # Use the tallest needed height (all stages same height for alignment)
        node_h = max(content_heights.values())
    else:
        node_h = min(100, (canvas_h - header_h - margin * 2))

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
    row_gap: int = 12,
    col_gap: int = 12,
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
        arrow_space = (rows - 1) * 50  # minimum gap for arrows between rows
        available_for_cards = usable_h - arrow_space
        if total_rows_h > available_for_cards and available_for_cards > 0:
            scale = available_for_cards / total_rows_h
            row_heights = [max(60, int(h * scale)) for h in row_heights]
            total_rows_h = sum(row_heights)

        # Compute row gaps from leftover
        leftover_h = usable_h - total_rows_h
        if rows > 1:
            actual_row_gap = max(row_gap, min(leftover_h // (rows), 80))
        else:
            actual_row_gap = row_gap

        # Push grid toward top
        total_grid_h = total_rows_h + (rows - 1) * actual_row_gap
        top_leftover = max(0, usable_h - total_grid_h)
        start_y = header_h + min(top_leftover // 5, 30)

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
        actual_row_gap = max(row_gap, leftover_h // rows)
        actual_row_gap = min(actual_row_gap, 80)
    else:
        actual_row_gap = row_gap

    total_grid_h = rows * node_h + (rows - 1) * actual_row_gap
    top_leftover = max(0, usable_h - total_grid_h)
    start_y = header_h + min(top_leftover // 5, 30)

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
    center_w, center_h = 160, 80
    positions[center_id] = (cx - center_w // 2, cy - center_h // 2, center_w, center_h)

    n = len(outer_ids)
    if n == 0:
        return positions

    radius = min(canvas_w, canvas_h - header_h) // 3
    node_w, node_h = 140, 70

    for i, nid in enumerate(outer_ids):
        angle = (2 * math.pi * i) / n - math.pi / 2
        nx = int(cx + radius * math.cos(angle)) - node_w // 2
        ny = int(cy + radius * math.sin(angle)) - node_h // 2
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
