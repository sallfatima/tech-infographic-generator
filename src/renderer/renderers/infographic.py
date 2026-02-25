"""General infographic renderer - cards with icons and stats.

Supports three rendering modes:
- Guidebook theme: DailyDoseofDS style with header-band cards, clean layout
- Whiteboard theme: SwirlAI style with dashed borders, colored cards
- Dark themes: Dark background with gradient accents
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size, draw_text_block
from ..shapes import (
    draw_rounded_rect, draw_node_with_header, draw_dashed_rect,
    draw_outer_border, draw_step_number,
)
from ..gradients import draw_gradient_bar, draw_gradient_rect
from ..icons import paste_icon
from ..layout import layout_grid


def render_infographic(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a general infographic with icon cards."""
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
    """Render infographic in guidebook style (DailyDoseofDS)."""
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

    # Grid layout
    node_ids = [n.id for n in data.nodes]
    n = len(node_ids)
    cols = 3 if n >= 6 else 2 if n >= 3 else 1
    positions = layout_grid(node_ids, width, height, cols=cols, header_h=header_h)

    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[i % len(section_colors)]
        color = node.color or sc["border"]
        header_bg = sc.get("header_bg", sc["border"])

        # Card with colored header band
        draw_node_with_header(
            img, draw,
            (x, y, x + w, y + h),
            label=node.label[:30],
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
    """Render infographic in whiteboard style (SwirlAI)."""
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

    # Grid layout
    node_ids = [n.id for n in data.nodes]
    n = len(node_ids)
    cols = 3 if n >= 6 else 2 if n >= 3 else 1
    positions = layout_grid(node_ids, width, height, cols=cols, header_h=header_h)

    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        sc = section_colors[i % len(section_colors)]
        color = node.color or sc["border"]

        # Card with colored fill
        draw.rounded_rectangle(
            (x, y, x + w, y + h),
            radius=12,
            fill=hex_to_rgb(sc["fill"]),
        )

        # Dashed border
        draw_dashed_rect(
            draw, (x, y, x + w, y + h),
            sc["border"], width=2, dash=8, gap=5, radius=12,
        )

        # Content layout
        content_y = y + 15

        # Icon (left side) + Label (right of icon)
        if node.icon:
            icon_size = min(32, h // 4)
            paste_icon(img, node.icon.value, (x + 28, content_y + icon_size // 2 + 2), icon_size, sc["border"])
            label_x = x + 55
        else:
            label_x = x + 18

        # Label
        label_font = get_font(17, "bold")
        draw.text(
            (label_x, content_y),
            node.label[:30],
            fill=hex_to_rgb(theme["text"]),
            font=label_font,
        )
        content_y += 32

        # Description
        if node.description:
            desc_font = get_font(13, "regular")
            draw_text_block(
                draw, node.description,
                (x + 18, content_y),
                desc_font,
                hex_to_rgb(theme["text_muted"]),
                w - 36,
                max_lines=(h - 50) // 18,
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
    """Render infographic in dark mode (original style)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Full-width gradient bar
    draw_gradient_bar(img, (0, 0, width, 6), theme["gradient_start"], theme["gradient_end"])

    # Title area
    title_font = get_font(34, "bold")
    draw.text((60, 30), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

    header_h = 85
    if data.subtitle:
        sub_font = get_font(16, "regular")
        draw.text((60, 72), data.subtitle, fill=hex_to_rgb(theme["text_muted"]), font=sub_font)
        header_h = 105

    # Grid layout
    node_ids = [n.id for n in data.nodes]
    n = len(node_ids)
    cols = 3 if n >= 6 else 2 if n >= 3 else 1
    positions = layout_grid(node_ids, width, height, cols=cols, header_h=header_h)

    node_colors = theme.get("node_colors", [theme["accent"]])

    for i, node in enumerate(data.nodes):
        if node.id not in positions:
            continue
        x, y, w, h = positions[node.id]
        color = node.color or node_colors[i % len(node_colors)]

        # Card background
        draw_rounded_rect(draw, (x, y, x + w, y + h), 12, theme["card"], theme["border"])

        # Top gradient accent
        draw_gradient_rect(img, (x + 1, y + 1, x + w - 1, y + 5), color, theme.get("accent2", color), radius=12)

        # Icon (centered)
        content_y = y + 18
        if node.icon:
            icon_size = min(36, h // 4)
            paste_icon(img, node.icon.value, (x + 35, content_y + icon_size // 2), icon_size, color)
            label_x = x + 65
        else:
            label_x = x + 20

        # Label
        label_font = get_font(17, "bold")
        draw.text(
            (label_x, content_y),
            node.label[:35],
            fill=hex_to_rgb(theme["text"]),
            font=label_font,
        )
        content_y += 30

        # Description
        if node.description:
            desc_font = get_font(13, "regular")
            draw_text_block(
                draw, node.description,
                (x + 20, content_y),
                desc_font,
                hex_to_rgb(theme["text_muted"]),
                w - 40,
                max_lines=(h - 60) // 20,
            )

    # Footer
    if data.footer:
        footer_font = get_font(11, "regular")
        draw.text(
            (60, height - 30),
            data.footer,
            fill=hex_to_rgb(theme["text_muted"]),
            font=footer_font,
        )

    return img
