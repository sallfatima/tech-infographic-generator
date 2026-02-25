"""Multi-agent system renderer - shows agent hierarchy, communication, and tools.

Inspired by the AI Engineering Guidebook patterns:
- Hierarchical: manager agent delegates to worker agents
- Network: agents communicate freely
- Router: controller routes to specialists

Supports three rendering modes:
- Guidebook theme: DailyDoseofDS style with header-band agent cards
- Whiteboard theme: SwirlAI style with dashed borders
- Dark themes: Dark background with accent bars
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size, draw_text_block
from ..shapes import (
    draw_node, draw_node_with_header, draw_rounded_rect,
    draw_dashed_rect, draw_outer_border, draw_step_number,
    draw_zone_group,
)
from ..arrows import draw_connection, draw_straight_arrow, draw_bezier_arrow
from ..gradients import draw_gradient_bar
from ..layout import layout_radial, layout_force_directed, get_node_center, get_node_edge
from ..icons import paste_icon, draw_icon_with_bg


def render_multi_agent(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a multi-agent system diagram."""
    is_guidebook = theme.get("node_header_band", False)
    is_whiteboard = theme.get("dashed_border", False)

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
    """Render multi-agent in guidebook style (DailyDoseofDS)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    outer_color = theme.get("outer_border_color", "#5B8DEF")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=1)

    header_h = 80

    # Title
    title_font = get_font(24, "bold")
    tw, th = text_size(draw, data.title, title_font)
    title_x = (width - tw) // 2
    title_y = 25
    draw.text((title_x, title_y), data.title, fill=hex_to_rgb(theme["accent"]), font=title_font)

    if data.subtitle:
        sub_font = get_font(12, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(((width - sw) // 2, title_y + th + 8), data.subtitle, fill=hex_to_rgb(theme["text_muted"]), font=sub_font)
        header_h = 100

    if not data.nodes:
        return img

    center_node = data.nodes[0]
    outer_nodes = data.nodes[1:]
    outer_ids = [n.id for n in outer_nodes]

    positions = layout_radial(center_node.id, outer_ids, width, height, header_h)
    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Draw connections with numbered arrows
    center_pos = positions.get(center_node.id)
    if center_pos:
        for i, node in enumerate(outer_nodes):
            if node.id in positions:
                sc = section_colors[(i + 1) % len(section_colors)]
                from_center = get_node_center(center_pos)
                to_center = get_node_center(positions[node.id])
                start = get_node_edge(center_pos, to_center)
                end = get_node_edge(positions[node.id], from_center)

                conn_label = None
                conn_style = "arrow"
                for conn in data.connections:
                    if (conn.from_node == center_node.id and conn.to_node == node.id) or \
                       (conn.from_node == node.id and conn.to_node == center_node.id):
                        conn_label = conn.label
                        conn_style = conn.style.value if conn.style else "arrow"
                        break

                draw_connection(
                    draw, start, end,
                    style=conn_style, label=conn_label,
                    color=sc["border"], routing="straight", width=2,
                )

    # Draw outer agent nodes
    for i, node in enumerate(outer_nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[(i + 1) % len(section_colors)]
        color = node.color or sc["border"]
        header_bg = sc.get("header_bg", sc["border"])

        draw_node_with_header(
            img, draw, (x, y, x + w, y + h),
            label=node.label, description=node.description,
            icon_name=node.icon.value if node.icon else None,
            fill_color="#FFFFFF", border_color=sc["border"],
            text_color=theme["text"], text_muted_color=theme["text_muted"],
            accent_color=color, header_bg=header_bg, icon_color="#FFFFFF",
        )

    # Draw center (manager) agent last
    if center_pos:
        x, y, w, h = center_pos
        sc0 = section_colors[0]
        draw_node_with_header(
            img, draw, (x, y, x + w, y + h),
            label=center_node.label, description=center_node.description,
            icon_name=center_node.icon.value if center_node.icon else None,
            fill_color="#FFFFFF", border_color=sc0["border"],
            text_color=theme["text"], text_muted_color=theme["text_muted"],
            accent_color=sc0["border"],
            header_bg=sc0.get("header_bg", sc0["border"]),
            icon_color="#FFFFFF",
        )

    # Draw inter-agent connections (non-center connections)
    for conn in data.connections:
        if conn.from_node != center_node.id and conn.to_node != center_node.id:
            if conn.from_node in positions and conn.to_node in positions:
                from_center = get_node_center(positions[conn.from_node])
                to_center = get_node_center(positions[conn.to_node])
                start = get_node_edge(positions[conn.from_node], to_center)
                end = get_node_edge(positions[conn.to_node], from_center)
                draw_connection(
                    draw, start, end,
                    style=conn.style.value if conn.style else "dashed_arrow",
                    label=conn.label,
                    color=theme["text_muted"], routing="straight", width=1,
                )

    return img


def _render_whiteboard(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render multi-agent in whiteboard style (SwirlAI)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    outer_color = theme.get("outer_border_color", "#2B7DE9")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=2)

    header_h = 90

    title_font = get_font(26, "bold")
    tw, th = text_size(draw, data.title, title_font)
    title_x = (width - tw) // 2
    title_y = 28
    draw.rounded_rectangle(
        (title_x - 18, title_y - 6, title_x + tw + 18, title_y + th + 12),
        radius=8, fill=hex_to_rgb("#E3F2FD"), outline=hex_to_rgb("#2B7DE9"), width=2,
    )
    draw.text((title_x, title_y), data.title, fill=hex_to_rgb("#1565C0"), font=title_font)

    if data.subtitle:
        sub_font = get_font(13, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(((width - sw) // 2, title_y + th + 18), data.subtitle, fill=hex_to_rgb(theme["text_muted"]), font=sub_font)
        header_h = 110

    if not data.nodes:
        return img

    center_node = data.nodes[0]
    outer_nodes = data.nodes[1:]
    outer_ids = [n.id for n in outer_nodes]

    positions = layout_force_directed(
        data.nodes, data.connections, width, height,
        margin=70, header_h=header_h, node_w=170, node_h=100,
    )
    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Draw zones if available
    if hasattr(data, 'zones') and data.zones:
        from ..layout import layout_zone_based
        positions, zone_rects = layout_zone_based(
            data.zones, data.nodes, data.connections, width, height,
            margin=70, header_h=header_h,
        )
        for zr in zone_rects:
            zi = zone_rects.index(zr)
            zsc = section_colors[zi % len(section_colors)]
            draw_zone_group(img, draw, zr["bbox"], zr["name"], zsc)
            draw = ImageDraw.Draw(img)  # refresh after zone overlay

    # Draw connections
    center_pos = positions.get(center_node.id)
    if center_pos:
        for i, node in enumerate(outer_nodes):
            if node.id in positions:
                sc = section_colors[(i + 1) % len(section_colors)]
                from_center = get_node_center(center_pos)
                to_center = get_node_center(positions[node.id])
                start = get_node_edge(center_pos, to_center)
                end = get_node_edge(positions[node.id], from_center)

                conn_label = None
                for conn in data.connections:
                    if (conn.from_node == center_node.id and conn.to_node == node.id) or \
                       (conn.from_node == node.id and conn.to_node == center_node.id):
                        conn_label = conn.label
                        break

                flip = (i % 2 == 0)
                draw_bezier_arrow(
                    draw, start, end, color=sc["border"],
                    width=2, dashed=True, curvature=0.2,
                    label=conn_label, flip_curve=flip,
                )

    # Draw outer nodes
    for i, node in enumerate(outer_nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[(i + 1) % len(section_colors)]

        draw.rounded_rectangle(
            (x, y, x + w, y + h), radius=10,
            fill=hex_to_rgb(sc["fill"]), outline=hex_to_rgb(sc["border"]), width=2,
        )
        draw_dashed_rect(draw, (x, y, x + w, y + h), sc["border"], width=2, dash=8, gap=5, radius=10)

        padding = 10
        content_y = y + padding + 4
        cx_node = x + w // 2

        if node.icon:
            icon_bg_size = min(40, h // 3)
            icon_inner = int(icon_bg_size * 0.6)
            draw_icon_with_bg(img, draw, node.icon.value, (cx_node, content_y + icon_bg_size // 2),
                             icon_size=icon_inner, bg_size=icon_bg_size,
                             icon_color="#FFFFFF", bg_color=sc["border"])
            content_y += icon_bg_size + 4

        label_font = get_font(min(14, max(11, h // 6)), "bold")
        lw, lh = text_size(draw, node.label, label_font)
        draw.text((cx_node - lw // 2, content_y), node.label, fill=hex_to_rgb(theme["text"]), font=label_font)
        content_y += lh + 2

        if node.description and h > 60:
            desc_fs = min(10, max(8, h // 8))
            desc_font = get_font(desc_fs, "regular")
            line_h = int(desc_fs * 1.4)
            remaining_h = (y + h - 6) - content_y
            available_lines = max(1, remaining_h // line_h)
            draw_text_block(draw, node.description, (x + padding, content_y), desc_font, hex_to_rgb(theme["text_muted"]), w - padding * 2, max_lines=available_lines, align="center")

    # Draw center node
    if center_pos:
        x, y, w, h = center_pos
        sc0 = section_colors[0]
        draw.rounded_rectangle((x - 2, y - 2, x + w + 2, y + h + 2), radius=14, fill=hex_to_rgb(sc0["border"]))

        cx_center = x + w // 2
        content_y = y + 12

        if center_node.icon:
            draw_icon_with_bg(img, draw, center_node.icon.value, (cx_center, content_y + 18),
                             icon_size=22, bg_size=36,
                             icon_color="#FFFFFF", bg_color="#FFFFFF",
                             border_color=sc0["border"])
            content_y += 40

        label_font = get_font(18, "bold")
        lw, lh = text_size(draw, center_node.label, label_font)
        draw.text((cx_center - lw // 2, content_y), center_node.label, fill=hex_to_rgb("#FFFFFF"), font=label_font)

        if center_node.description:
            desc_font = get_font(10, "regular")
            desc_text = center_node.description
            remaining_h = (y + h - 6) - (content_y + lh + 4)
            line_h = int(10 * 1.4)
            max_desc_lines = max(1, remaining_h // line_h)
            draw_text_block(
                draw, desc_text, (x + 10, content_y + lh + 4),
                desc_font, hex_to_rgb("#E2E8F0"), w - 20,
                line_height=line_h, max_lines=max_desc_lines, align="center",
            )

    return img


def _render_dark(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render multi-agent in dark mode."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(img, (0, 0, width, 5), theme["gradient_start"], theme["gradient_end"])

    title_font = get_font(28, "bold")
    tw, _ = text_size(draw, data.title, title_font)
    draw.text(((width - tw) // 2, 15), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

    header_h = 55
    if data.subtitle:
        sub_font = get_font(13, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(((width - sw) // 2, 48), data.subtitle, fill=hex_to_rgb(theme["text_muted"]), font=sub_font)
        header_h = 70

    if not data.nodes:
        return img

    center_node = data.nodes[0]
    outer_nodes = data.nodes[1:]
    outer_ids = [n.id for n in outer_nodes]

    positions = layout_radial(center_node.id, outer_ids, width, height, header_h)
    node_colors = theme.get("node_colors", [theme["accent"]])

    # Draw connections
    center_pos = positions.get(center_node.id)
    if center_pos:
        for i, node in enumerate(outer_nodes):
            if node.id in positions:
                color = node.color or node_colors[(i + 1) % len(node_colors)]
                from_center = get_node_center(center_pos)
                to_center = get_node_center(positions[node.id])
                start = get_node_edge(center_pos, to_center)
                end = get_node_edge(positions[node.id], from_center)

                conn_style = "arrow"
                conn_label = None
                for conn in data.connections:
                    if (conn.from_node == center_node.id and conn.to_node == node.id) or \
                       (conn.from_node == node.id and conn.to_node == center_node.id):
                        conn_style = conn.style.value
                        conn_label = conn.label
                        break

                draw_connection(
                    draw, start, end,
                    style=conn_style, label=conn_label,
                    color=color, routing="straight",
                )

    # Draw outer nodes
    for i, node in enumerate(outer_nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        color = node.color or node_colors[(i + 1) % len(node_colors)]

        draw_node(
            img, draw, (x, y, x + w, y + h),
            label=node.label, description=node.description,
            icon_name=node.icon.value if node.icon else None,
            shape=node.shape.value,
            fill_color=theme["card"], border_color=theme["border"],
            text_color=theme["text"], text_muted_color=theme["text_muted"],
            accent_color=color, icon_color=color,
        )

    # Draw center node
    if center_pos:
        x, y, w, h = center_pos
        draw_node(
            img, draw, (x, y, x + w, y + h),
            label=center_node.label, description=center_node.description,
            icon_name=center_node.icon.value if center_node.icon else None,
            shape=center_node.shape.value,
            fill_color=theme["accent"], border_color=theme["accent2"],
            text_color="#FFFFFF", text_muted_color="#E2E8F0",
            accent_color=theme["accent"], icon_color="#FFFFFF",
        )

    # Draw non-center connections
    for conn in data.connections:
        if conn.from_node != center_node.id and conn.to_node != center_node.id:
            if conn.from_node in positions and conn.to_node in positions:
                from_center = get_node_center(positions[conn.from_node])
                to_center = get_node_center(positions[conn.to_node])
                start = get_node_edge(positions[conn.from_node], to_center)
                end = get_node_edge(positions[conn.to_node], from_center)
                draw_connection(
                    draw, start, end,
                    style=conn.style.value if conn.style else "dashed_arrow",
                    label=conn.label,
                    color=theme["text_muted"], routing="straight",
                )

    return img
