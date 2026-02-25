"""Layout algorithms for positioning nodes on the canvas."""

import math


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
) -> dict[str, tuple[int, int, int, int]]:
    """Horizontal flow layout: left to right."""
    positions = {}
    n = len(node_ids)
    if n == 0:
        return positions

    usable_w = canvas_w - margin * 2
    gap = 50
    node_w = min((usable_w - (n - 1) * gap) // n, 200)
    node_h = min(100, (canvas_h - header_h - margin * 2))
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
) -> dict[str, tuple[int, int, int, int]]:
    """Grid layout for cards — balanced sizing with arrow gaps between rows."""
    positions = {}
    n = len(node_ids)
    if n == 0:
        return positions

    cols = min(cols, n)
    rows = math.ceil(n / cols)
    usable_w = canvas_w - margin * 2
    usable_h = canvas_h - header_h - footer_h
    node_w = (usable_w - (cols - 1) * col_gap) // cols

    # Calculate card height: fill available space but cap for readability
    raw_h = (usable_h - (rows - 1) * row_gap) // rows
    max_h = {1: 300, 2: 200, 3: 140}.get(rows, 120)
    node_h = min(raw_h, max_h)

    # Distribute leftover space as row gaps (arrows need ~40-60px between rows)
    total_cards_h = rows * node_h
    leftover_h = usable_h - total_cards_h
    if rows > 1:
        # All leftover goes between rows (for arrows), not above/below
        actual_row_gap = max(row_gap, leftover_h // rows)
        # Cap the gap so it's not absurdly large
        actual_row_gap = min(actual_row_gap, 80)
    else:
        actual_row_gap = row_gap

    # Position: push grid toward top with small offset
    total_grid_h = rows * node_h + (rows - 1) * actual_row_gap
    # Small top offset (10-15% of leftover), rest goes to bottom
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
    """Get the edge point of a node closest to a target point.

    Uses a directional approach:
    - If the target is mostly below, return bottom-center
    - If the target is mostly above, return top-center
    - If the target is mostly to the right, return right-center
    - If the target is mostly to the left, return left-center

    This produces clean orthogonal connections.
    """
    x, y, w, h = pos
    cx, cy = x + w // 2, y + h // 2
    tx, ty = target

    dx = tx - cx
    dy = ty - cy

    if dx == 0 and dy == 0:
        return (cx, cy)

    # Determine primary direction based on angle
    # Use the dominant axis to pick the edge
    if abs(dy) >= abs(dx):
        # Primarily vertical
        if dy > 0:
            # Target is below -> bottom-center
            return (cx, y + h)
        else:
            # Target is above -> top-center
            return (cx, y)
    else:
        # Primarily horizontal
        if dx > 0:
            # Target is to the right -> right-center
            return (x + w, cy)
        else:
            # Target is to the left -> left-center
            return (x, cy)


def get_node_bottom(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    """Get the bottom-center point of a node."""
    x, y, w, h = pos
    return (x + w // 2, y + h)


def get_node_top(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    """Get the top-center point of a node."""
    x, y, w, h = pos
    return (x + w // 2, y)


def get_node_left(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    """Get the left-center point of a node."""
    x, y, w, h = pos
    return (x, y + h // 2)


def get_node_right(pos: tuple[int, int, int, int]) -> tuple[int, int]:
    """Get the right-center point of a node."""
    x, y, w, h = pos
    return (x + w, y + h // 2)
