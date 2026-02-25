"""Layered architecture diagram renderer (SwirlAI / ByteByteGo style).

Supports two rendering modes:
- Whiteboard theme: Clean white background, dashed colored borders, section boxes
- Dark themes: Dark background with layer bands and accent bars
"""

from collections import defaultdict

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb, get_theme
from ..typography import get_font, text_size
from ..shapes import (
    draw_rounded_rect, draw_node, draw_node_with_header, draw_dashed_rect,
    draw_section_box, draw_step_number, draw_outer_border, draw_numbered_badge,
)
from ..arrows import draw_connection, draw_straight_arrow, draw_numbered_arrow, draw_bezier_arrow
from ..icons import draw_icon_with_bg
from ..gradients import draw_gradient_bar
from ..layout import (
    layout_layered, get_node_center, get_node_edge,
    get_node_bottom, get_node_top, get_node_right, get_node_left,
)


def render_architecture(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a layered architecture diagram."""
    is_whiteboard = theme.get("dashed_border", False)
    is_guidebook = theme.get("node_header_band", False)

    if is_guidebook:
        return _render_guidebook(data, width, height, theme)
    elif is_whiteboard:
        return _render_whiteboard(data, width, height, theme)
    else:
        return _render_dark(data, width, height, theme)


def _render_guidebook(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render in DailyDoseofDS guidebook style.

    Features:
    - Soft pastel section backgrounds with colored header bands
    - Nodes with colored top header bands (label on colored bg, description on white)
    - Numbered dashed arrows with step labels
    - Clean, editorial look with generous whitespace
    """
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Subtle outer border (thinner than whiteboard)
    outer_color = theme.get("outer_border_color", "#5B8DEF")
    draw_outer_border(draw, width, height, outer_color, margin=12, border_width=1)

    margin = 50
    header_h = 80

    # Title - clean, colored text (no box background)
    title_font = get_font(28, "bold")
    tw, th = text_size(draw, data.title, title_font)
    title_x = margin
    title_y = 22
    draw.text(
        (title_x, title_y),
        data.title,
        fill=hex_to_rgb(theme["accent"]),
        font=title_font,
    )

    # Subtitle
    if data.subtitle:
        sub_font = get_font(13, "regular")
        draw.text(
            (title_x, title_y + th + 8),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 95

    # Build layers data — support both data.layers and data.zones
    if data.layers:
        layers_data = [{"name": l.name, "nodes": l.nodes, "color": l.color} for l in data.layers]
    elif data.zones:
        layers_data = [
            {"name": z.get("name", f"Zone {i+1}"), "nodes": z.get("nodes", []), "color": z.get("color")}
            for i, z in enumerate(data.zones)
        ]
    else:
        layers_data = [{"name": data.title, "nodes": [n.id for n in data.nodes], "color": None}]
    nodes_dict = {n.id: n for n in data.nodes}

    # Create synthetic Layer objects for rendering if we only have zones
    effective_layers = data.layers if data.layers else [
        type("Layer", (), {"name": ld["name"], "nodes": ld["nodes"], "color": ld.get("color")})()
        for ld in layers_data
    ]

    # Calculate positions
    positions = layout_layered(layers_data, data.nodes, width, height, margin, header_h)

    # Section colors from theme
    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Draw layer section boxes with colored left accent bar (guidebook style)
    n_layers = len(effective_layers)
    layer_boxes = {}
    if n_layers > 0:
        available_h = height - header_h - 30
        layer_h = available_h // n_layers
        layer_gap = 10

        for li, layer in enumerate(effective_layers):
            ly = header_h + li * layer_h
            sc = section_colors[li % len(section_colors)]

            box = (margin - 8, ly + layer_gap // 2, width - margin + 8, ly + layer_h - layer_gap // 2)
            layer_boxes[li] = box
            bx0, by0, bx1, by1 = box

            # Soft fill background
            draw.rounded_rectangle(box, radius=8, fill=hex_to_rgb(sc["fill"]))

            # Colored left accent bar (4px wide)
            draw.rounded_rectangle(
                (bx0, by0, bx0 + 5, by1),
                radius=3,
                fill=hex_to_rgb(sc["border"]),
            )

            # Layer name label (colored, top-left inside the section)
            label_font = get_font(14, "bold")
            draw.text(
                (bx0 + 16, by0 + 8),
                layer.name,
                fill=hex_to_rgb(sc["text"]),
                font=label_font,
            )

    # Node styling
    node_layer_map = {}
    for li, layer in enumerate(effective_layers):
        for nid in layer.nodes:
            node_layer_map[nid] = li

    # Draw nodes with header bands
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        li = node_layer_map.get(node.id, 0)
        sc = section_colors[li % len(section_colors)]
        color = node.color or sc["border"]
        header_bg = sc.get("header_bg", sc["border"])

        draw_node_with_header(
            img, draw,
            (x, y, x + w, y + h),
            label=node.label,
            description=node.description,
            icon_name=node.icon.value if node.icon else None,
            shape=node.shape.value,
            fill_color="#FFFFFF",
            border_color=sc["border"],
            text_color=theme["text"],
            text_muted_color=theme["text_muted"],
            accent_color=color,
            header_bg=header_bg,
            icon_color=color,
        )

    # Count outgoing connections for fan-out distribution
    outgoing_down = defaultdict(list)
    outgoing_up = defaultdict(list)
    for conn in data.connections:
        fl = node_layer_map.get(conn.from_node, 0)
        tl = node_layer_map.get(conn.to_node, 0)
        if fl < tl:
            outgoing_down[conn.from_node].append(conn.to_node)
        elif fl > tl:
            outgoing_up[conn.from_node].append(conn.to_node)

    # Draw connections with numbered arrows
    for ci, conn in enumerate(data.connections):
        if conn.from_node in positions and conn.to_node in positions:
            from_pos = positions[conn.from_node]
            to_pos = positions[conn.to_node]
            from_layer = node_layer_map.get(conn.from_node, 0)
            to_layer = node_layer_map.get(conn.to_node, 0)

            sc = section_colors[from_layer % len(section_colors)]
            conn_color = sc["border"]

            if from_layer < to_layer:
                siblings = outgoing_down[conn.from_node]
                n_out = len(siblings)
                if n_out > 1:
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
                if n_out > 1:
                    idx = siblings.index(conn.to_node)
                    fx, fy, fw, fh = from_pos
                    spread = min(fw - 20, n_out * 30)
                    offset = -spread // 2 + idx * (spread // max(n_out - 1, 1))
                    start = (fx + fw // 2 + offset, fy)
                else:
                    start = get_node_top(from_pos)
                end = get_node_bottom(to_pos)
            else:
                from_cx = from_pos[0] + from_pos[2] // 2
                to_cx = to_pos[0] + to_pos[2] // 2
                if from_cx < to_cx:
                    start = get_node_right(from_pos)
                    end = get_node_left(to_pos)
                else:
                    start = get_node_left(from_pos)
                    end = get_node_right(to_pos)

            # Use numbered dashed arrows (guidebook style)
            draw_numbered_arrow(
                draw, start, end,
                number=ci + 1,
                label=conn.label,
                color=conn_color,
                width=2,
                dashed=True,
                badge_size=18,
            )

    # Footer
    if data.footer:
        footer_font = get_font(11, "regular")
        draw.text(
            (margin, height - 28),
            data.footer,
            fill=hex_to_rgb(theme["text_muted"]),
            font=footer_font,
        )

    return img


def _render_whiteboard(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render in whiteboard style (SwirlAI / ByteByteGo)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Outer dashed border
    outer_color = theme.get("outer_border_color", "#2B7DE9")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=2)

    margin = 50
    header_h = 90

    # Title in a rounded box (SwirlAI style)
    title_font = get_font(26, "bold")
    tw, th = text_size(draw, data.title, title_font)
    title_x = width - margin - tw - 30
    title_y = 25
    # Title background box
    draw.rounded_rectangle(
        (title_x - 15, title_y - 5, title_x + tw + 15, title_y + th + 10),
        radius=8,
        fill=hex_to_rgb("#E3F2FD"),
        outline=hex_to_rgb("#2B7DE9"),
        width=2,
    )
    draw.text(
        (title_x, title_y),
        data.title,
        fill=hex_to_rgb("#1565C0"),
        font=title_font,
    )

    # Subtitle
    if data.subtitle:
        sub_font = get_font(13, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(
            (title_x, title_y + th + 15),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 105

    # Build layers data — support both data.layers and data.zones
    if data.layers:
        layers_data = [{"name": l.name, "nodes": l.nodes, "color": l.color} for l in data.layers]
    elif data.zones:
        layers_data = [
            {"name": z.get("name", f"Zone {i+1}"), "nodes": z.get("nodes", []), "color": z.get("color")}
            for i, z in enumerate(data.zones)
        ]
    else:
        layers_data = [{"name": data.title, "nodes": [n.id for n in data.nodes], "color": None}]
    nodes_dict = {n.id: n for n in data.nodes}

    # Create synthetic Layer objects for rendering if we only have zones
    effective_layers = data.layers if data.layers else [
        type("Layer", (), {"name": ld["name"], "nodes": ld["nodes"], "color": ld.get("color")})()
        for ld in layers_data
    ]

    # Calculate positions
    positions = layout_layered(layers_data, data.nodes, width, height, margin, header_h)

    # Section colors from theme
    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Draw layer section boxes (dashed colored borders)
    n_layers = len(effective_layers)
    layer_boxes = {}
    if n_layers > 0:
        available_h = height - header_h - 35
        layer_h = available_h // n_layers
        layer_gap = 12

        for li, layer in enumerate(effective_layers):
            ly = header_h + li * layer_h
            sc = section_colors[li % len(section_colors)]

            box = (margin - 10, ly + layer_gap // 2, width - margin + 10, ly + layer_h - layer_gap // 2)
            layer_boxes[li] = box

            # Section box with dashed border
            draw_section_box(
                draw, box,
                title=layer.name,
                fill_color=sc["fill"],
                border_color=sc["border"],
                text_color=sc["text"],
                dashed=True,
                border_width=2,
            )

    # Node styling for whiteboard
    node_layer_map = {}
    for li, layer in enumerate(effective_layers):
        for nid in layer.nodes:
            node_layer_map[nid] = li

    # Draw nodes
    node_colors = theme.get("node_colors", [theme["accent"]])
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        li = node_layer_map.get(node.id, 0)
        sc = section_colors[li % len(section_colors)]
        color = node.color or sc["border"]

        draw_node(
            img, draw,
            (x, y, x + w, y + h),
            label=node.label,
            description=node.description,
            icon_name=node.icon.value if node.icon else None,
            shape=node.shape.value,
            fill_color="#FFFFFF",
            border_color=sc["border"],
            text_color=theme["text"],
            text_muted_color=theme["text_muted"],
            accent_color=color,
            icon_color=color,
        )

    # Count outgoing connections for fan-out distribution
    outgoing_down = defaultdict(list)
    outgoing_up = defaultdict(list)
    for conn in data.connections:
        fl = node_layer_map.get(conn.from_node, 0)
        tl = node_layer_map.get(conn.to_node, 0)
        if fl < tl:
            outgoing_down[conn.from_node].append(conn.to_node)
        elif fl > tl:
            outgoing_up[conn.from_node].append(conn.to_node)

    # Draw connections with step numbers
    for ci, conn in enumerate(data.connections):
        if conn.from_node in positions and conn.to_node in positions:
            from_pos = positions[conn.from_node]
            to_pos = positions[conn.to_node]
            from_layer = node_layer_map.get(conn.from_node, 0)
            to_layer = node_layer_map.get(conn.to_node, 0)

            # Determine connection color based on source section
            sc = section_colors[from_layer % len(section_colors)]
            conn_color = sc["border"]

            if from_layer < to_layer:
                siblings = outgoing_down[conn.from_node]
                n_out = len(siblings)
                if n_out > 1:
                    idx = siblings.index(conn.to_node)
                    fx, fy, fw, fh = from_pos
                    spread = min(fw - 20, n_out * 30)
                    offset = -spread // 2 + idx * (spread // max(n_out - 1, 1))
                    start = (fx + fw // 2 + offset, fy + fh)
                else:
                    start = get_node_bottom(from_pos)
                end = get_node_top(to_pos)
                routing = "manhattan"
            elif from_layer > to_layer:
                siblings = outgoing_up[conn.from_node]
                n_out = len(siblings)
                if n_out > 1:
                    idx = siblings.index(conn.to_node)
                    fx, fy, fw, fh = from_pos
                    spread = min(fw - 20, n_out * 30)
                    offset = -spread // 2 + idx * (spread // max(n_out - 1, 1))
                    start = (fx + fw // 2 + offset, fy)
                else:
                    start = get_node_top(from_pos)
                end = get_node_bottom(to_pos)
                routing = "manhattan"
            else:
                from_cx = from_pos[0] + from_pos[2] // 2
                to_cx = to_pos[0] + to_pos[2] // 2
                if from_cx < to_cx:
                    start = get_node_right(from_pos)
                    end = get_node_left(to_pos)
                else:
                    start = get_node_left(from_pos)
                    end = get_node_right(to_pos)
                routing = "straight"

            # Use bezier dashed arrows for whiteboard style (SwirlAI)
            draw_bezier_arrow(
                draw, start, end,
                color=conn_color, width=2, dashed=True,
                curvature=0.15, label=conn.label,
            )

            # Draw step number near the start of the connection (not mid to avoid label overlap)
            t = 0.25  # 25% along the path
            num_x = int(start[0] + t * (end[0] - start[0]))
            num_y = int(start[1] + t * (end[1] - start[1]))
            draw_step_number(
                draw, (num_x - 13, num_y - 13),
                ci + 1,
                bg_color="#FFFFFF",
                border_color=conn_color,
                text_color=conn_color,
                radius=13,
            )

    # Footer
    if data.footer:
        footer_font = get_font(11, "regular")
        draw.text(
            (margin, height - 30),
            data.footer,
            fill=hex_to_rgb(theme["text_muted"]),
            font=footer_font,
        )

    return img


def _render_dark(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render in dark mode (original style)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(img, (0, 0, width, 5), theme["gradient_start"], theme["gradient_end"])

    # Title
    title_font = get_font(32, "bold")
    draw.text((60, 25), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

    if data.subtitle:
        sub_font = get_font(16, "regular")
        draw.text((60, 65), data.subtitle, fill=hex_to_rgb(theme["text_muted"]), font=sub_font)

    header_h = 100
    margin = 60

    layers_data = [{"name": l.name, "nodes": l.nodes, "color": l.color} for l in data.layers]
    nodes_dict = {n.id: n for n in data.nodes}
    positions = layout_layered(layers_data, data.nodes, width, height, margin, header_h)

    # Draw layer backgrounds
    n_layers = len(data.layers)
    if n_layers > 0:
        available_h = height - header_h - margin // 2
        layer_h = available_h // n_layers
        layer_colors = theme.get("layer_colors", ["#1E293B"] * 4)

        for li, layer in enumerate(data.layers):
            ly = header_h + li * layer_h
            lcolor = layer.color or layer_colors[li % len(layer_colors)]

            draw_rounded_rect(
                draw,
                (margin // 2, ly + 2, width - margin // 2, ly + layer_h - 2),
                8, lcolor, theme["border"],
            )

            label_font = get_font(13, "semibold")
            lw, lh = text_size(draw, layer.name, label_font)
            draw.text(
                (margin // 2 + 10, ly + layer_h // 2 - lh // 2),
                layer.name,
                fill=hex_to_rgb(theme["text_muted"]),
                font=label_font,
            )

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

    # Draw connections
    for conn in data.connections:
        if conn.from_node in positions and conn.to_node in positions:
            from_pos = positions[conn.from_node]
            to_pos = positions[conn.to_node]
            from_layer = node_layer_map.get(conn.from_node, 0)
            to_layer = node_layer_map.get(conn.to_node, 0)

            if from_layer < to_layer:
                siblings = outgoing_down[conn.from_node]
                n_out = len(siblings)
                if n_out > 1:
                    idx = siblings.index(conn.to_node)
                    fx, fy, fw, fh = from_pos
                    spread = min(fw - 20, n_out * 30)
                    offset = -spread // 2 + idx * (spread // max(n_out - 1, 1))
                    start = (fx + fw // 2 + offset, fy + fh)
                else:
                    start = get_node_bottom(from_pos)
                end = get_node_top(to_pos)
                routing = "manhattan"
            elif from_layer > to_layer:
                siblings = outgoing_up[conn.from_node]
                n_out = len(siblings)
                if n_out > 1:
                    idx = siblings.index(conn.to_node)
                    fx, fy, fw, fh = from_pos
                    spread = min(fw - 20, n_out * 30)
                    offset = -spread // 2 + idx * (spread // max(n_out - 1, 1))
                    start = (fx + fw // 2 + offset, fy)
                else:
                    start = get_node_top(from_pos)
                end = get_node_bottom(to_pos)
                routing = "manhattan"
            else:
                from_cx = from_pos[0] + from_pos[2] // 2
                to_cx = to_pos[0] + to_pos[2] // 2
                if from_cx < to_cx:
                    start = get_node_right(from_pos)
                    end = get_node_left(to_pos)
                else:
                    start = get_node_left(from_pos)
                    end = get_node_right(to_pos)
                routing = "straight"

            draw_connection(
                draw, start, end,
                style=conn.style.value,
                label=conn.label,
                color=theme["text_muted"],
                routing=routing,
            )

    # Draw nodes
    node_colors = theme.get("node_colors", [theme["accent"]])
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        color = node.color or node_colors[i % len(node_colors)]

        draw_node(
            img, draw,
            (x, y, x + w, y + h),
            label=node.label,
            description=node.description,
            icon_name=node.icon.value if node.icon else None,
            shape=node.shape.value,
            fill_color=theme["card"],
            border_color=theme["border"],
            text_color=theme["text"],
            text_muted_color=theme["text_muted"],
            accent_color=color,
            icon_color=color,
        )

    if data.footer:
        footer_font = get_font(11, "regular")
        draw.text(
            (margin, height - 30),
            data.footer,
            fill=hex_to_rgb(theme["text_muted"]),
            font=footer_font,
        )

    return img
