"""Process/steps renderer - numbered steps with descriptions.

Supports three rendering modes:
- Guidebook theme: DailyDoseofDS style with header-band step cards, numbered badges
- Whiteboard theme: SwirlAI style with dashed borders, colored step cards
- Dark themes: Dark background with accent bars
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size, draw_text_block
from ..shapes import (
    draw_rounded_rect, draw_node_with_header, draw_dashed_rect,
    draw_step_number, draw_outer_border, draw_numbered_badge,
)
from ..gradients import draw_gradient_bar
from ..icons import paste_icon, draw_icon_with_bg
from ..layout import layout_grid
from ..arrows import draw_numbered_arrow, draw_straight_arrow, draw_bezier_arrow


def render_process(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render numbered process steps as a card grid."""
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
    """Render process in guidebook style (DailyDoseofDS)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Soft outer border
    outer_color = theme.get("outer_border_color", "#5B8DEF")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=1)

    margin = 50
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

    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Layout as grid — content-aware: pass nodes so heights adapt to descriptions
    node_ids = [n.id for n in data.nodes]
    cols = 3 if len(node_ids) > 4 else 2 if len(node_ids) > 2 else 1
    positions = layout_grid(
        node_ids, width, height, cols=cols, header_h=header_h,
        nodes=data.nodes,
    )

    # Draw flow arrows between consecutive nodes FIRST (behind cards)
    for i in range(len(data.nodes) - 1):
        n1 = data.nodes[i]
        n2 = data.nodes[i + 1]
        if n1.id not in positions or n2.id not in positions:
            continue
        x1, y1, w1, h1 = positions[n1.id]
        x2, y2, w2, h2 = positions[n2.id]
        sc = section_colors[i % len(section_colors)]

        # Determine arrow direction based on actual positions (not just col/row indices)
        # This correctly handles grid wrapping (e.g. end of row 1 → start of row 2)
        cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
        cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
        is_same_row = abs(cy1 - cy2) < h1 // 2

        if is_same_row:
            # Horizontal: right edge → left edge
            start = (x1 + w1, cy1)
            end = (x2, cy2)
        else:
            # Vertical: bottom edge → top edge (row wrap)
            start = (cx1, y1 + h1)
            end = (cx2, y2)

        conn_label = None
        if data.connections and i < len(data.connections):
            conn_label = data.connections[i].label

        draw_numbered_arrow(
            draw, start, end,
            number=i + 1,
            label=conn_label,
            color=sc["border"],
            dashed=True,
            width=2,
        )

    # Draw node cards ON TOP of arrows
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
            fill_color="#FFFFFF",
            border_color=sc["border"],
            text_color=theme["text"],
            text_muted_color=theme["text_muted"],
            accent_color=color,
            header_bg=header_bg,
            icon_color="#FFFFFF",
        )

        # Numbered badge in the top-left corner (offset outside the card)
        draw_numbered_badge(
            draw,
            (x + 18, y - 5),
            i + 1,
            bg_color="#FFFFFF",
            text_color=sc["border"],
            size=18,
        )

    # Footer
    if data.footer:
        footer_font = get_font(11, "regular")
        draw.text(
            (margin, height - 25),
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
    """Render process in whiteboard style (SwirlAI)."""
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

    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Layout as grid — content-aware
    node_ids = [n.id for n in data.nodes]
    cols = 3 if len(node_ids) > 4 else 2 if len(node_ids) > 2 else 1
    positions = layout_grid(
        node_ids, width, height, cols=cols, header_h=header_h,
        nodes=data.nodes,
    )

    # Draw flow arrows between consecutive nodes FIRST (behind cards)
    for i in range(len(data.nodes) - 1):
        n1 = data.nodes[i]
        n2 = data.nodes[i + 1]
        if n1.id not in positions or n2.id not in positions:
            continue
        x1, y1, w1, h1 = positions[n1.id]
        x2, y2, w2, h2 = positions[n2.id]
        sc = section_colors[i % len(section_colors)]

        # Use actual positions to determine direction (handles grid wrapping)
        cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
        cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
        is_same_row = abs(cy1 - cy2) < h1 // 2

        if is_same_row:
            start = (x1 + w1, cy1)
            end = (x2, cy2)
        else:
            start = (cx1, y1 + h1)
            end = (cx2, y2)

        conn_label = None
        if data.connections and i < len(data.connections):
            conn_label = data.connections[i].label

        draw_bezier_arrow(
            draw, start, end,
            color=sc["border"], width=2, dashed=True,
            curvature=0.15, label=conn_label,
        )

    # Draw node cards ON TOP of arrows
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[i % len(section_colors)]
        color = node.color or sc["border"]

        # Card with colored fill and dashed border
        draw.rounded_rectangle(
            (x, y, x + w, y + h),
            radius=12,
            fill=hex_to_rgb(sc["fill"]),
        )
        draw_dashed_rect(
            draw, (x, y, x + w, y + h),
            sc["border"], width=2, dash=8, gap=5, radius=12,
        )

        # Step number badge on border (straddles top-left, not inside content)
        draw_step_number(
            draw, (x + 24, y),
            i + 1,
            bg_color="#FFFFFF",
            border_color=sc["border"],
            text_color=sc["border"],
            radius=16,
        )

        # Icon in top-right with background (SwirlAI style)
        icon_bottom = y + 28
        if node.icon:
            icon_bg_size = min(32, max(20, h // 5))
            icon_inner = int(icon_bg_size * 0.6)
            draw_icon_with_bg(img, draw, node.icon.value, (x + w - 28, y + 24),
                              icon_size=icon_inner, bg_size=icon_bg_size,
                              icon_color="#FFFFFF", bg_color=sc["border"])
            icon_bottom = y + 24 + icon_bg_size // 2

        # Label — adaptive font, positioned below step number area
        label_top = y + 12
        max_label_w = w - 65  # account for step number + icon
        label_font = get_font(14, "bold")
        for fs in range(17, 11, -1):
            label_font = get_font(fs, "bold")
            lw, lh = text_size(draw, node.label, label_font)
            if lw <= max_label_w:
                break
        display_label = node.label
        lw, lh = text_size(draw, display_label, label_font)
        if lw > max_label_w:
            while lw > max_label_w and len(display_label) > 3:
                display_label = display_label[:-1]
                lw, lh = text_size(draw, display_label + "..", label_font)
            display_label += ".."
            lw, lh = text_size(draw, display_label, label_font)

        draw.text(
            (x + 50, label_top),
            display_label,
            fill=hex_to_rgb(theme["text"]),
            font=label_font,
        )

        # Description — dynamic max_lines based on actual remaining space
        desc_top = max(label_top + lh + 6, icon_bottom + 4)
        if node.description:
            remaining_h = (y + h - 8) - desc_top
            if remaining_h > 12:
                desc_fs = min(12, max(9, h // 10))
                if remaining_h < 30:
                    desc_fs = 9
                desc_font = get_font(desc_fs, "regular")
                line_h = int(desc_fs * 1.4)
                available_lines = max(1, remaining_h // line_h)
                draw_text_block(
                    draw, node.description,
                    (x + 14, desc_top),
                    desc_font,
                    hex_to_rgb(theme["text_muted"]),
                    w - 28,
                    max_lines=available_lines,
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


def _render_dark(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render process in dark mode (original style)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(img, (0, 0, width, 5), theme["gradient_start"], theme["gradient_end"])

    # Title
    title_font = get_font(30, "bold")
    draw.text((60, 25), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

    header_h = 80
    if data.subtitle:
        sub_font = get_font(15, "regular")
        draw.text((60, 62), data.subtitle, fill=hex_to_rgb(theme["text_muted"]), font=sub_font)
        header_h = 95

    # Layout as grid — content-aware
    node_ids = [n.id for n in data.nodes]
    cols = 3 if len(node_ids) > 4 else 2 if len(node_ids) > 2 else 1
    positions = layout_grid(
        node_ids, width, height, cols=cols, header_h=header_h,
        nodes=data.nodes,
    )
    node_colors = theme.get("node_colors", [theme["accent"]])

    # Draw flow arrows between consecutive nodes FIRST (behind cards)
    for i in range(len(data.nodes) - 1):
        n1 = data.nodes[i]
        n2 = data.nodes[i + 1]
        if n1.id not in positions or n2.id not in positions:
            continue
        x1, y1, w1, h1 = positions[n1.id]
        x2, y2, w2, h2 = positions[n2.id]
        color = node_colors[i % len(node_colors)]

        # Use actual positions to determine direction
        cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
        cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
        is_same_row = abs(cy1 - cy2) < h1 // 2

        if is_same_row:
            start = (x1 + w1, cy1)
            end = (x2, cy2)
        else:
            start = (cx1, y1 + h1)
            end = (cx2, y2)

        draw_straight_arrow(
            draw, start, end,
            color=color,
            width=2,
            head_size=10,
        )

    # Draw node cards ON TOP of arrows
    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        color = node.color or node_colors[i % len(node_colors)]

        # Card background
        draw_rounded_rect(draw, (x, y, x + w, y + h), 12, theme["card"], theme["border"])

        # Left accent bar
        draw_rounded_rect(draw, (x, y, x + 4, y + h), 2, color)

        # Step number badge — proportional to card size
        badge_r = min(18, h // 6)
        badge_cx = x + 10 + badge_r
        badge_cy = y + 10 + badge_r
        draw.ellipse(
            (badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r),
            fill=hex_to_rgb(color),
        )
        num_font = get_font(max(11, badge_r), "bold")
        num_text = str(i + 1)
        nw, nh = text_size(draw, num_text, num_font)
        draw.text(
            (badge_cx - nw // 2, badge_cy - nh // 2),
            num_text,
            fill=hex_to_rgb("#FFFFFF"),
            font=num_font,
        )

        # Icon
        if node.icon:
            icon_size = min(24, h // 5)
            paste_icon(img, node.icon.value, (x + w - 30, y + 10 + badge_r), icon_size, color)

        # Label — adaptive font, positioned next to badge
        label_x = badge_cx + badge_r + 8
        max_label_w = (x + w - 10) - label_x
        label_font = get_font(14, "bold")
        for fs in range(17, 11, -1):
            label_font = get_font(fs, "bold")
            lw, lh = text_size(draw, node.label, label_font)
            if lw <= max_label_w:
                break
        display_label = node.label
        lw, lh = text_size(draw, display_label, label_font)
        if lw > max_label_w:
            while lw > max_label_w and len(display_label) > 3:
                display_label = display_label[:-1]
                lw, lh = text_size(draw, display_label + "..", label_font)
            display_label += ".."
            lw, lh = text_size(draw, display_label, label_font)

        draw.text(
            (label_x, badge_cy - lh // 2),
            display_label,
            fill=hex_to_rgb(theme["text"]),
            font=label_font,
        )

        # Description — dynamic max_lines based on actual remaining space
        desc_top = max(badge_cy + badge_r + 6, y + 10 + badge_r * 2 + 8)
        if node.description:
            remaining_h = (y + h - 8) - desc_top
            if remaining_h > 12:
                desc_fs = min(13, max(9, h // 10))
                if remaining_h < 30:
                    desc_fs = 9
                desc_font = get_font(desc_fs, "regular")
                line_h = int(desc_fs * 1.4)
                available_lines = max(1, remaining_h // line_h)
                draw_text_block(
                    draw, node.description,
                    (x + 14, desc_top),
                    desc_font,
                    hex_to_rgb(theme["text_muted"]),
                    w - 28,
                    max_lines=available_lines,
                )

    return img
