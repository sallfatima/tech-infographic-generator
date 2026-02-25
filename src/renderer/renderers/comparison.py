"""Comparison renderer - side-by-side columns.

Supports three rendering modes:
- Guidebook theme: DailyDoseofDS style with header-band columns, accent bars
- Whiteboard theme: SwirlAI style with dashed borders, colored columns
- Dark themes: Dark background with gradient headers
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size, draw_text_block
from ..shapes import (
    draw_rounded_rect, draw_node_with_header, draw_dashed_rect,
    draw_section_box, draw_outer_border,
)
from ..gradients import draw_gradient_bar, draw_gradient_rect
from ..icons import paste_icon
from ..typography import wrap_text


def render_comparison(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a side-by-side comparison chart."""
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
    """Render comparison in guidebook style (DailyDoseofDS)."""
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

    gap = 20
    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Group nodes by their 'group' field
    groups = {}
    for node in data.nodes:
        key = node.group or node.id
        groups.setdefault(key, []).append(node)

    group_list = list(groups.items())
    n_cols = len(group_list)
    if n_cols == 0:
        return img

    col_w = (width - margin * 2 - (n_cols - 1) * gap) // n_cols

    for ci, (group_name, nodes) in enumerate(group_list):
        col_x = margin + ci * (col_w + gap)
        sc = section_colors[ci % len(section_colors)]
        header_bg = sc.get("header_bg", sc["border"])

        col_top = header_h
        col_bottom = height - 30

        # Column card with white background and border
        draw.rounded_rectangle(
            (col_x, col_top, col_x + col_w, col_bottom),
            radius=10,
            fill=hex_to_rgb("#FFFFFF"),
            outline=hex_to_rgb(sc["border"]),
            width=1,
        )

        # Colored header band for column title
        band_h = 38
        draw.rounded_rectangle(
            (col_x, col_top, col_x + col_w, col_top + band_h + 10),
            radius=10,
            fill=hex_to_rgb(header_bg),
        )
        # Flat bottom to header band
        draw.rectangle(
            (col_x, col_top + band_h - 5, col_x + col_w, col_top + band_h + 10),
            fill=hex_to_rgb(header_bg),
        )

        # Header text (white on colored band)
        header_font = get_font(16, "bold")
        htw, hth = text_size(draw, group_name, header_font)
        draw.text(
            (col_x + (col_w - htw) // 2, col_top + (band_h - hth) // 2 + 2),
            group_name,
            fill=hex_to_rgb("#FFFFFF"),
            font=header_font,
        )

        # Render items in column body — content-adaptive heights
        item_y = col_top + band_h + 18
        label_font = get_font(14, "bold")
        item_font = get_font(12, "regular")
        item_line_h = int(12 * 1.4)
        n_items = len(nodes)
        available_col_h = col_bottom - item_y - 10
        item_gap = 8

        for ni, node in enumerate(nodes):
            # Measure needed height based on description
            base_item_h = 38  # label + padding
            if node.description:
                desc_lines = wrap_text(draw, node.description, item_font, col_w - 48)
                desc_h = len(desc_lines) * item_line_h + 6
                item_h = base_item_h + desc_h
            else:
                item_h = base_item_h + 12

            # Clamp to available space
            remaining_items = n_items - ni
            max_item_h = (available_col_h - (remaining_items - 1) * item_gap) // max(remaining_items, 1)
            item_h = min(item_h, max(max_item_h, 50))

            # Pastel card background
            draw.rounded_rectangle(
                (col_x + 10, item_y, col_x + col_w - 10, item_y + item_h),
                radius=8,
                fill=hex_to_rgb(sc["fill"]),
                outline=hex_to_rgb(sc["border"]),
                width=1,
            )

            # Colored left accent bar
            draw.rounded_rectangle(
                (col_x + 10, item_y + 4, col_x + 15, item_y + item_h - 4),
                radius=2,
                fill=hex_to_rgb(sc["border"]),
            )

            # Icon
            if node.icon:
                paste_icon(img, node.icon.value, (col_x + 30, item_y + 16), 16, sc["border"])

            # Label
            label_x = col_x + (48 if node.icon else 24)
            draw.text(
                (label_x, item_y + 8),
                node.label,
                fill=hex_to_rgb(theme["text"]),
                font=label_font,
            )

            if node.description:
                desc_top = item_y + 30
                remaining_h = (item_y + item_h - 6) - desc_top
                available_lines = max(1, remaining_h // item_line_h)
                draw_text_block(
                    draw, node.description,
                    (col_x + 24, desc_top),
                    item_font,
                    hex_to_rgb(theme["text_muted"]),
                    col_w - 48,
                    max_lines=available_lines,
                )

            item_y += item_h + item_gap
            available_col_h -= (item_h + item_gap)

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
    """Render comparison in whiteboard style (SwirlAI)."""
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

    gap = 25
    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Group nodes by their 'group' field
    groups = {}
    for node in data.nodes:
        key = node.group or node.id
        groups.setdefault(key, []).append(node)

    group_list = list(groups.items())
    n_cols = len(group_list)
    if n_cols == 0:
        return img

    col_w = (width - margin * 2 - (n_cols - 1) * gap) // n_cols

    for ci, (group_name, nodes) in enumerate(group_list):
        col_x = margin + ci * (col_w + gap)
        sc = section_colors[ci % len(section_colors)]

        # Column section box with dashed border
        col_top = header_h
        col_bottom = height - 35
        draw_section_box(
            draw,
            (col_x, col_top, col_x + col_w, col_bottom),
            title=group_name,
            fill_color=sc["fill"],
            border_color=sc["border"],
            text_color=sc["text"],
            dashed=True,
            border_width=2,
        )

        # Render items in column — content-adaptive heights
        item_y = col_top + 35
        label_font = get_font(15, "bold")
        item_font = get_font(13, "regular")
        item_line_h = int(13 * 1.4)
        n_items = len(nodes)
        available_col_h = col_bottom - item_y - 10
        item_gap = 10

        for ni, node in enumerate(nodes):
            # Measure needed height based on description
            base_item_h = 42  # label + padding
            if node.description:
                desc_lines = wrap_text(draw, node.description, item_font, col_w - 52)
                desc_h = len(desc_lines) * item_line_h + 6
                item_h = base_item_h + desc_h
            else:
                item_h = base_item_h + 16

            # Clamp to available space
            remaining_items = n_items - ni
            max_item_h = (available_col_h - (remaining_items - 1) * item_gap) // max(remaining_items, 1)
            item_h = min(item_h, max(max_item_h, 50))

            draw.rounded_rectangle(
                (col_x + 12, item_y, col_x + col_w - 12, item_y + item_h),
                radius=8,
                fill=hex_to_rgb("#FFFFFF"),
                outline=hex_to_rgb(sc["border"]),
                width=1,
            )

            # Left accent bar
            draw.rounded_rectangle(
                (col_x + 12, item_y, col_x + 16, item_y + item_h),
                radius=2,
                fill=hex_to_rgb(sc["border"]),
            )

            # Icon
            if node.icon:
                paste_icon(img, node.icon.value, (col_x + 32, item_y + 18), 18, sc["border"])

            # Label
            label_x = col_x + (50 if node.icon else 28)
            draw.text(
                (label_x, item_y + 10),
                node.label,
                fill=hex_to_rgb(theme["text"]),
                font=label_font,
            )

            if node.description:
                desc_top = item_y + 35
                remaining_h = (item_y + item_h - 6) - desc_top
                available_lines = max(1, remaining_h // item_line_h)
                draw_text_block(
                    draw, node.description,
                    (col_x + 28, desc_top),
                    item_font,
                    hex_to_rgb(theme["text_muted"]),
                    col_w - 52,
                    max_lines=available_lines,
                )

            item_y += item_h + item_gap
            available_col_h -= (item_h + item_gap)

    return img


def _render_dark(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render comparison in dark mode (original style)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(img, (0, 0, width, 5), theme["gradient_start"], theme["gradient_end"])

    # Title
    title_font = get_font(30, "bold")
    tw, _ = text_size(draw, data.title, title_font)
    draw.text(((width - tw) // 2, 25), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

    header_h = 80
    if data.subtitle:
        sub_font = get_font(14, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(
            ((width - sw) // 2, 62),
            data.subtitle,
            fill=hex_to_rgb(theme["text_muted"]),
            font=sub_font,
        )
        header_h = 95

    margin = 50
    gap = 25

    # Group nodes
    groups = {}
    for node in data.nodes:
        key = node.group or node.id
        groups.setdefault(key, []).append(node)

    group_list = list(groups.items())
    n_cols = len(group_list)
    if n_cols == 0:
        return img

    col_w = (width - margin * 2 - (n_cols - 1) * gap) // n_cols
    node_colors = theme.get("node_colors", [theme["accent"]])

    for ci, (group_name, nodes) in enumerate(group_list):
        col_x = margin + ci * (col_w + gap)
        color = node_colors[ci % len(node_colors)]

        # Column header with gradient
        header_h_col = 55
        draw_gradient_rect(
            img,
            (col_x, header_h, col_x + col_w, header_h + header_h_col),
            color,
            theme.get("accent2", color),
            radius=10,
        )

        # Header text
        header_font = get_font(18, "bold")
        htw, hth = text_size(draw, group_name, header_font)
        draw.text(
            (col_x + (col_w - htw) // 2, header_h + (header_h_col - hth) // 2),
            group_name,
            fill=hex_to_rgb("#FFFFFF"),
            font=header_font,
        )

        # Column body background
        body_top = header_h + header_h_col + 5
        draw_rounded_rect(
            draw,
            (col_x, body_top, col_x + col_w, height - 40),
            10,
            theme["card"],
            theme["border"],
        )

        # Render items in column — content-adaptive
        item_y = body_top + 15
        item_font = get_font(14, "regular")
        label_font = get_font(15, "bold")
        item_line_h = int(14 * 1.4)
        available_col_h = (height - 40) - item_y - 10

        for node in nodes:
            # Icon
            if node.icon:
                paste_icon(img, node.icon.value, (col_x + 25, item_y + 10), 20, color)

            # Label
            label_x = col_x + (45 if node.icon else 15)
            draw.text(
                (label_x, item_y),
                node.label,
                fill=hex_to_rgb(theme["text"]),
                font=label_font,
            )

            if node.description:
                desc_y = item_y + 22
                remaining_h = min(available_col_h - 30, 120)
                available_lines = max(1, remaining_h // item_line_h)
                used_h = draw_text_block(
                    draw, node.description,
                    (col_x + 15, desc_y),
                    item_font,
                    hex_to_rgb(theme["text_muted"]),
                    col_w - 30,
                    max_lines=available_lines,
                )
                item_y = desc_y + used_h + 15
            else:
                item_y += 35

            available_col_h = (height - 40) - item_y

            # Separator line
            draw.line(
                [(col_x + 15, item_y - 5), (col_x + col_w - 15, item_y - 5)],
                fill=hex_to_rgb(theme["border"]),
                width=1,
            )

    return img
