"""Flowchart renderer - horizontal/vertical step flows.

Supports two rendering modes:
- Whiteboard theme: SwirlAI style with dashed borders, step numbers, colored sections
- Dark themes: Dark background with accent bars
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size, draw_text_block
from ..shapes import (
    draw_node, draw_node_with_header, draw_rounded_rect, draw_dashed_rect,
    draw_section_box, draw_step_number, draw_outer_border, draw_numbered_badge,
)
from ..arrows import draw_straight_arrow, draw_connection, draw_numbered_arrow
from ..gradients import draw_gradient_bar
from ..layout import layout_flow_horizontal, get_node_center, get_node_right, get_node_left
from ..icons import paste_icon


def render_flowchart(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a horizontal flowchart."""
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
    """Render flowchart in DailyDoseofDS guidebook style.

    Features:
    - Nodes with colored header bands
    - Numbered dashed arrows with step labels
    - Clean pastel aesthetic
    """
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Subtle outer border
    outer_color = theme.get("outer_border_color", "#5B8DEF")
    draw_outer_border(draw, width, height, outer_color, margin=12, border_width=1)

    margin = 50
    header_h = 80

    # Title (clean colored text, guidebook style)
    title_font = get_font(26, "bold")
    tw, th = text_size(draw, data.title, title_font)
    title_x = (width - tw) // 2
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
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(
            ((width - sw) // 2, title_y + th + 10),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 100

    # Layout nodes
    node_ids = [n.id for n in data.nodes]
    positions = layout_flow_horizontal(node_ids, width, height, header_h=header_h)
    nodes_dict = {n.id: n for n in data.nodes}
    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Draw a subtle flow track behind nodes
    if len(node_ids) >= 2 and node_ids[0] in positions and node_ids[-1] in positions:
        first_pos = positions[node_ids[0]]
        last_pos = positions[node_ids[-1]]
        track_y = first_pos[1] + first_pos[3] // 2
        track_x0 = first_pos[0] - 15
        track_x1 = last_pos[0] + last_pos[2] + 15
        draw.rounded_rectangle(
            (track_x0, track_y - 55, track_x1, track_y + 55),
            radius=20,
            fill=hex_to_rgb("#FAFBFF"),
        )

    # Draw numbered arrows between consecutive nodes
    for i in range(len(node_ids) - 1):
        nid = node_ids[i]
        next_nid = node_ids[i + 1]
        if nid in positions and next_nid in positions:
            start = get_node_right(positions[nid])
            end = get_node_left(positions[next_nid])

            sc = section_colors[i % len(section_colors)]
            conn_color = sc["border"]

            # Find connection label
            label = None
            for conn in data.connections:
                if conn.from_node == nid and conn.to_node == next_nid:
                    label = conn.label
                    break

            draw_numbered_arrow(
                draw, start, end,
                number=i + 1,
                label=label,
                color=conn_color,
                width=2,
                dashed=True,
                badge_size=18,
            )

    # Draw nodes with header bands
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[i % len(section_colors)]
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
    """Render flowchart in whiteboard style (SwirlAI)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Outer dashed border
    outer_color = theme.get("outer_border_color", "#2B7DE9")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=2)

    margin = 50
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

    # Layout nodes
    node_ids = [n.id for n in data.nodes]
    positions = layout_flow_horizontal(node_ids, width, height, header_h=header_h)
    nodes_dict = {n.id: n for n in data.nodes}
    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Draw a subtle flow track behind nodes
    if len(node_ids) >= 2 and node_ids[0] in positions and node_ids[-1] in positions:
        first_pos = positions[node_ids[0]]
        last_pos = positions[node_ids[-1]]
        track_y = first_pos[1] + first_pos[3] // 2
        track_x0 = first_pos[0] - 10
        track_x1 = last_pos[0] + last_pos[2] + 10
        # Light track background
        draw.rounded_rectangle(
            (track_x0, track_y - 50, track_x1, track_y + 50),
            radius=25,
            fill=hex_to_rgb("#F8FBFF"),
            outline=hex_to_rgb("#E3EBF5"),
            width=1,
        )

    # Draw arrows between consecutive nodes
    for i in range(len(node_ids) - 1):
        nid = node_ids[i]
        next_nid = node_ids[i + 1]
        if nid in positions and next_nid in positions:
            start = get_node_right(positions[nid])
            end = get_node_left(positions[next_nid])

            # Color based on source node index
            sc = section_colors[i % len(section_colors)]
            conn_color = sc["border"]

            # Find matching connection for label
            label = None
            for conn in data.connections:
                if conn.from_node == nid and conn.to_node == next_nid:
                    label = conn.label
                    break

            draw_straight_arrow(
                draw, start, end,
                color=conn_color,
                width=3,
                head_size=12,
                dashed=True,
            )

    # Draw nodes with section-colored borders and step numbers
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[i % len(section_colors)]
        color = node.color or sc["border"]

        # Step number above node
        draw_step_number(
            draw, (x + w // 2, y - 20),
            i + 1,
            bg_color="#FFFFFF",
            border_color=sc["border"],
            text_color=sc["border"],
            radius=15,
        )

        # Node with white fill and colored border
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
    """Render flowchart in dark mode (original style)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Accent bar
    draw_gradient_bar(img, (0, 0, width, 4), theme["gradient_start"], theme["gradient_end"])

    # Title
    title_font = get_font(28, "bold")
    tw, th = text_size(draw, data.title, title_font)
    draw.text(
        ((width - tw) // 2, 20),
        data.title,
        fill=hex_to_rgb(theme["text"]),
        font=title_font,
    )

    # Subtitle
    header_h = 70
    if data.subtitle:
        sub_font = get_font(14, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(
            ((width - sw) // 2, 55),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 85

    # Layout nodes
    node_ids = [n.id for n in data.nodes]
    positions = layout_flow_horizontal(node_ids, width, height, header_h=header_h)
    nodes_dict = {n.id: n for n in data.nodes}
    node_colors = theme.get("node_colors", [theme["accent"]])

    # Draw arrows between consecutive nodes (horizontal flow: right → left)
    for i in range(len(node_ids) - 1):
        nid = node_ids[i]
        next_nid = node_ids[i + 1]
        if nid in positions and next_nid in positions:
            start = get_node_right(positions[nid])
            end = get_node_left(positions[next_nid])

            draw_straight_arrow(
                draw, start, end,
                color=theme["accent"],
                width=3,
                head_size=10,
            )

    # Draw step numbers and nodes
    num_font = get_font(12, "bold")
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        color = node.color or node_colors[i % len(node_colors)]

        # Step number badge
        badge_x = x + w // 2
        badge_y = y - 18
        badge_r = 14
        draw.ellipse(
            (badge_x - badge_r, badge_y - badge_r, badge_x + badge_r, badge_y + badge_r),
            fill=hex_to_rgb(color),
        )
        num_text = str(i + 1)
        nw, nh = text_size(draw, num_text, num_font)
        draw.text(
            (badge_x - nw // 2, badge_y - nh // 2),
            num_text,
            fill=hex_to_rgb("#FFFFFF"),
            font=num_font,
        )

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

    return img
