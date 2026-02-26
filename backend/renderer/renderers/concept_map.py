"""Concept map renderer - central node with radial branches.

Supports three rendering modes:
- Guidebook theme: DailyDoseofDS style with header-band nodes, numbered connections
- Whiteboard theme: SwirlAI style with dashed borders, colored sections, clean lines
- Dark themes: Dark background with colored cards
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size
from ..shapes import (
    draw_node, draw_node_with_header, draw_rounded_rect, draw_dashed_rect,
    draw_outer_border, draw_step_number, draw_numbered_badge,
)
from ..arrows import draw_straight_arrow, draw_connection, draw_numbered_arrow, draw_bezier_arrow
from ..icons import draw_icon_with_bg
from ..gradients import draw_gradient_bar
from ..layout import layout_radial, get_node_center, get_node_edge


def render_concept_map(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a concept map with a central node and radial branches."""
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
    """Render concept map in guidebook style (DailyDoseofDS)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Soft outer border
    outer_color = theme.get("outer_border_color", "#5B8DEF")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=1)

    header_h = 80

    # Clean colored title (editorial style)
    title_font = get_font(24, "bold")
    tw, th = text_size(draw, data.title, title_font)
    title_x = (width - tw) // 2
    title_y = 25
    draw.text(
        (title_x, title_y),
        data.title,
        fill=hex_to_rgb(theme["accent"]),
        font=title_font,
    )

    # Subtitle
    if data.subtitle:
        sub_font = get_font(12, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(
            ((width - sw) // 2, title_y + th + 8),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 100

    if not data.nodes:
        return img

    # First node is center, rest are outer
    center_node = data.nodes[0]
    outer_nodes = data.nodes[1:]
    outer_ids = [n.id for n in outer_nodes]

    positions = layout_radial(center_node.id, outer_ids, width, height, header_h)
    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Draw numbered connections (dashed arrows from center to outer)
    center_pos = positions.get(center_node.id)
    if center_pos:
        for i, node in enumerate(outer_nodes):
            if node.id in positions:
                sc = section_colors[(i + 1) % len(section_colors)]
                from_center = get_node_center(center_pos)
                to_center = get_node_center(positions[node.id])
                start = get_node_edge(center_pos, to_center)
                end = get_node_edge(positions[node.id], from_center)

                # Get label from connections
                conn_label = None
                for conn in data.connections:
                    if (conn.from_node == center_node.id and conn.to_node == node.id) or \
                       (conn.from_node == node.id and conn.to_node == center_node.id):
                        conn_label = conn.label
                        break

                draw_numbered_arrow(
                    draw, start, end,
                    number=i + 1,
                    label=conn_label,
                    color=sc["border"],
                    width=2,
                    head_size=10,
                    dashed=True,
                )

    # Draw outer nodes with header bands
    for i, node in enumerate(outer_nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[(i + 1) % len(section_colors)]
        color = node.color or sc["border"]
        header_bg = sc.get("header_bg", sc["border"])

        draw_node_with_header(
            img, draw,
            (x, y, x + w, y + h),
            label=node.label,
            description=node.description,
            icon_name=node.icon.value if node.icon else None,
            fill_color="#FFFFFF",
            border_color=sc["border"],
            text_color=theme["text"],
            text_muted_color=theme["text_muted"],
            accent_color=color,
            header_bg=header_bg,
            icon_color="#FFFFFF",
        )

    # Draw center node last (on top) - prominent with header band
    if center_pos:
        x, y, w, h = center_pos
        sc0 = section_colors[0]

        draw_node_with_header(
            img, draw,
            (x, y, x + w, y + h),
            label=center_node.label,
            description=center_node.description,
            icon_name=center_node.icon.value if center_node.icon else None,
            fill_color="#FFFFFF",
            border_color=sc0["border"],
            text_color=theme["text"],
            text_muted_color=theme["text_muted"],
            accent_color=sc0["border"],
            header_bg=sc0.get("header_bg", sc0["border"]),
            icon_color="#FFFFFF",
        )

    return img


def _render_whiteboard(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render concept map in whiteboard style (SwirlAI)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Outer dashed border
    outer_color = theme.get("outer_border_color", "#2B7DE9")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=2)

    header_h = 90

    # Title in colored box (SwirlAI style)
    title_font = get_font(26, "bold")
    tw, th = text_size(draw, data.title, title_font)
    title_x = (width - tw) // 2
    title_y = 28
    draw.rounded_rectangle(
        (title_x - 18, title_y - 6, title_x + tw + 18, title_y + th + 12),
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
            ((width - sw) // 2, title_y + th + 18),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 110

    if not data.nodes:
        return img

    # First node is center, rest are outer
    center_node = data.nodes[0]
    outer_nodes = data.nodes[1:]
    outer_ids = [n.id for n in outer_nodes]

    positions = layout_radial(center_node.id, outer_ids, width, height, header_h)
    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Draw connections (dashed lines from center to outer)
    center_pos = positions.get(center_node.id)
    if center_pos:
        for i, node in enumerate(outer_nodes):
            if node.id in positions:
                sc = section_colors[(i + 1) % len(section_colors)]
                from_center = get_node_center(center_pos)
                to_center = get_node_center(positions[node.id])
                start = get_node_edge(center_pos, to_center)
                end = get_node_edge(positions[node.id], from_center)

                # Check if explicit connection exists
                conn_style = "dashed_arrow"
                conn_label = None
                for conn in data.connections:
                    if (conn.from_node == center_node.id and conn.to_node == node.id) or \
                       (conn.from_node == node.id and conn.to_node == center_node.id):
                        conn_style = "dashed_arrow"  # Force dashed in whiteboard
                        conn_label = conn.label
                        break

                draw_bezier_arrow(
                    draw, start, end,
                    color=sc["border"], width=2, dashed=True,
                    curvature=0.15, label=conn_label,
                )

    # Draw outer nodes with colored dashed borders
    for i, node in enumerate(outer_nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[(i + 1) % len(section_colors)]
        color = node.color or sc["border"]

        # Light fill background
        draw.rounded_rectangle(
            (x, y, x + w, y + h),
            radius=10,
            fill=hex_to_rgb(sc["fill"]),
            outline=hex_to_rgb(sc["border"]),
            width=2,
        )

        # Draw dashed overlay border for SwirlAI feel
        draw_dashed_rect(draw, (x, y, x + w, y + h), sc["border"], width=2, dash=8, gap=5, radius=10)

        # Node content (icon + label + description)
        padding = 10
        content_y = y + padding + 4
        cx_node = x + w // 2

        max_content_y = y + h - 8  # bottom padding

        # Icon with background (SwirlAI style)
        if node.icon and (max_content_y - content_y) > 40:
            icon_bg_size = min(32, max(20, h // 5))
            icon_inner = int(icon_bg_size * 0.6)
            draw_icon_with_bg(img, draw, node.icon.value, (cx_node, content_y + icon_bg_size // 2),
                              icon_size=icon_inner, bg_size=icon_bg_size,
                              icon_color="#FFFFFF", bg_color=sc["border"])
            content_y += icon_bg_size + 4

        # Label — adaptive font with truncation
        if content_y < max_content_y - 10:
            max_lbl_w = w - padding * 2
            label_fs = min(14, max(11, h // 6))
            label_font = get_font(label_fs, "bold")
            lw, lh = text_size(draw, node.label, label_font)
            display_label = node.label
            if lw > max_lbl_w:
                for fs in range(label_fs - 1, 9, -1):
                    label_font = get_font(fs, "bold")
                    lw, lh = text_size(draw, display_label, label_font)
                    if lw <= max_lbl_w:
                        break
                if lw > max_lbl_w:
                    while lw > max_lbl_w and len(display_label) > 3:
                        display_label = display_label[:-1]
                        lw, lh = text_size(draw, display_label + "..", label_font)
                    display_label += ".."
                    lw, lh = text_size(draw, display_label, label_font)
            draw.text(
                (cx_node - lw // 2, content_y),
                display_label,
                fill=hex_to_rgb(theme["text"]),
                font=label_font,
            )
            content_y += lh + 2

        # Description — use readable font size based on available space
        if node.description:
            remaining_h = max_content_y - content_y
            if remaining_h > 12:
                desc_fs = min(10, max(9, h // 10))
                if remaining_h < 25:
                    desc_fs = 9
                desc_font = get_font(desc_fs, "regular")
                from ..typography import draw_text_block
                line_h = int(desc_fs * 1.35)
                available_lines = max(1, remaining_h // line_h)
                draw_text_block(
                    draw, node.description,
                    (x + padding, content_y),
                    desc_font,
                    hex_to_rgb(theme["text_muted"]),
                    w - padding * 2,
                    max_lines=available_lines,
                    align="center",
                )

    # Draw center node last (on top) - bigger, prominent
    if center_pos:
        x, y, w, h = center_pos
        sc0 = section_colors[0]

        # Center node with solid colored background
        draw.rounded_rectangle(
            (x - 2, y - 2, x + w + 2, y + h + 2),
            radius=14,
            fill=hex_to_rgb(sc0["border"]),
        )

        # Content
        cx_center = x + w // 2
        content_y = y + 12
        max_center_y = y + h - 8

        if center_node.icon and (max_center_y - content_y) > 50:
            icon_bg_size = min(36, max(22, h // 4))
            icon_inner = int(icon_bg_size * 0.6)
            draw_icon_with_bg(img, draw, center_node.icon.value,
                              (cx_center, content_y + icon_bg_size // 2),
                              icon_size=icon_inner, bg_size=icon_bg_size,
                              icon_color="#FFFFFF", bg_color=sc0["border"])
            content_y += icon_bg_size + 4

        # Label — adaptive font for center node
        max_lbl_w = w - 20
        label_fs = min(18, max(13, w // 12))
        label_font = get_font(label_fs, "bold")
        lw, lh = text_size(draw, center_node.label, label_font)
        if lw > max_lbl_w:
            for fs in range(label_fs - 1, 11, -1):
                label_font = get_font(fs, "bold")
                lw, lh = text_size(draw, center_node.label, label_font)
                if lw <= max_lbl_w:
                    break
        draw.text(
            (cx_center - lw // 2, content_y),
            center_node.label,
            fill=hex_to_rgb("#FFFFFF"),
            font=label_font,
        )
        content_y += lh + 4

        if center_node.description:
            remaining_h = max_center_y - content_y
            if remaining_h > 12:
                desc_fs = min(10, max(9, h // 10))
                desc_font = get_font(desc_fs, "regular")
                line_h = int(desc_fs * 1.35)
                max_desc_lines = max(1, remaining_h // line_h)
                from ..typography import draw_text_block
                draw_text_block(
                    draw, center_node.description, (x + 10, content_y),
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
    """Render concept map in dark mode (original style)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(img, (0, 0, width, 5), theme["gradient_start"], theme["gradient_end"])

    # Title
    title_font = get_font(28, "bold")
    tw, _ = text_size(draw, data.title, title_font)
    draw.text(((width - tw) // 2, 15), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

    header_h = 55
    if data.subtitle:
        sub_font = get_font(13, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(
            ((width - sw) // 2, 48),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 70

    if not data.nodes:
        return img

    # First node is center, rest are outer
    center_node = data.nodes[0]
    outer_nodes = data.nodes[1:]
    outer_ids = [n.id for n in outer_nodes]

    positions = layout_radial(center_node.id, outer_ids, width, height, header_h)
    node_colors = theme.get("node_colors", [theme["accent"]])

    # Draw connections (lines from center to outer)
    center_pos = positions.get(center_node.id)
    if center_pos:
        for i, node in enumerate(outer_nodes):
            if node.id in positions:
                color = node.color or node_colors[(i + 1) % len(node_colors)]
                from_center = get_node_center(center_pos)
                to_center = get_node_center(positions[node.id])
                start = get_node_edge(center_pos, to_center)
                end = get_node_edge(positions[node.id], from_center)

                # Check if explicit connection exists
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

    # Draw center node last (on top)
    if center_pos:
        x, y, w, h = center_pos
        draw_node(
            img, draw,
            (x, y, x + w, y + h),
            label=center_node.label,
            description=center_node.description,
            icon_name=center_node.icon.value if center_node.icon else None,
            shape=center_node.shape.value,
            fill_color=theme["accent"],
            border_color=theme["accent2"],
            text_color="#FFFFFF",
            text_muted_color="#E2E8F0",
            accent_color=theme["accent"],
            icon_color="#FFFFFF",
        )

    return img
