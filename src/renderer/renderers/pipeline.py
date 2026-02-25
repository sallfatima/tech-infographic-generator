"""Pipeline renderer - ML/Data pipeline with stages left-to-right.

Supports three rendering modes:
- Guidebook theme: DailyDoseofDS style with header-band nodes, numbered arrows
- Whiteboard theme: SwirlAI style with dashed borders, colored stages, step numbers
- Dark themes: Dark background with accent bars
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size, draw_text_block
from ..shapes import (
    draw_rounded_rect, draw_node, draw_node_with_header, draw_dashed_rect,
    draw_section_box, draw_step_number, draw_outer_border, draw_numbered_badge,
)
from ..arrows import draw_straight_arrow, draw_numbered_arrow, draw_bezier_arrow
from ..gradients import draw_gradient_bar
from ..icons import paste_icon, draw_icon_with_bg
from ..layout import measure_content_heights


def render_pipeline(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a pipeline diagram with stages flowing left to right."""
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
    """Render pipeline in guidebook style (DailyDoseofDS)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    # Soft outer border
    outer_color = theme.get("outer_border_color", "#5B8DEF")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=1)

    margin = 50
    header_h = 80

    # Clean colored title (no box - editorial style)
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

    n = len(data.nodes)
    if n == 0:
        return img

    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Pipeline stages layout - left to right with numbered arrows
    arrow_gap = 55
    usable_w = width - margin * 2
    stage_w = (usable_w - (n - 1) * arrow_gap) // n

    # Content-aware stage height
    content_heights = measure_content_heights(
        data.nodes, stage_w, is_header_style=True, is_pipeline=True, min_h=80, max_h=350,
    )
    stage_h = max(content_heights.values())
    max_available = height - header_h - margin - 25
    stage_h = min(stage_h, max_available)
    cy = header_h + stage_h // 2 + 10

    for i, node in enumerate(data.nodes):
        sc = section_colors[i % len(section_colors)]
        color = node.color or sc["border"]
        header_bg = sc.get("header_bg", sc["border"])
        sx = margin + i * (stage_w + arrow_gap)
        sy = cy - stage_h // 2

        # Node with colored header band (adaptive font, no forced truncation)
        draw_node_with_header(
            img, draw,
            (sx, sy, sx + stage_w, sy + stage_h),
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

        # Numbered arrow to next stage
        if i < n - 1:
            ax_start = sx + stage_w + 5
            ax_end = ax_start + arrow_gap - 10
            ay = cy

            # Get label from connections if available
            arrow_label = None
            for conn in data.connections:
                if conn.from_node == node.id:
                    arrow_label = conn.label
                    break

            draw_numbered_arrow(
                draw,
                (ax_start, ay),
                (ax_end, ay),
                number=i + 1,
                label=arrow_label,
                color=sc["border"],
                width=2,
                head_size=10,
                dashed=True,
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
    """Render pipeline in whiteboard style (SwirlAI)."""
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

    n = len(data.nodes)
    if n == 0:
        return img

    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Pipeline stages layout — content-aware height
    arrow_gap = 50
    usable_w = width - margin * 2
    stage_w = (usable_w - (n - 1) * arrow_gap) // n

    content_heights = measure_content_heights(
        data.nodes, stage_w, is_header_style=False, is_pipeline=True, min_h=80, max_h=350,
    )
    stage_h = max(content_heights.values())
    max_available = height - header_h - margin - 30
    stage_h = min(stage_h, max_available)
    # Center stages vertically in the available space
    cy = header_h + (height - header_h - margin) // 2

    # Zone support: render zone groups as background regions behind stages
    if hasattr(data, 'zones') and data.zones:
        from ..shapes import draw_zone_group
        from ..layout import layout_zone_based
        _node_positions, zone_rects = layout_zone_based(
            data.zones, data.nodes, data.connections,
            width, height, margin=margin, header_h=header_h,
        )
        for zr in zone_rects:
            zsc = zr.get("color_scheme", section_colors[0])
            draw_zone_group(
                img, draw,
                bbox=zr["bbox"],
                title=zr.get("name", ""),
                color_scheme=zsc,
                dashed=True,
            )

    for i, node in enumerate(data.nodes):
        sc = section_colors[i % len(section_colors)]
        color = node.color or sc["border"]
        sx = margin + i * (stage_w + arrow_gap)
        sy = cy - stage_h // 2

        # Stage section box with dashed border
        draw_section_box(
            draw,
            (sx, sy, sx + stage_w, sy + stage_h),
            title=f"Stage {i + 1}",
            fill_color=sc["fill"],
            border_color=sc["border"],
            text_color=sc["text"],
            dashed=True,
            border_width=2,
        )

        # Icon centered in the top area — prominent with colored background
        content_y = sy + 40
        if node.icon:
            icon_bg_size = min(38, stage_h // 4)
            icon_inner = int(icon_bg_size * 0.6)
            draw_icon_with_bg(img, draw, node.icon.value, (sx + stage_w // 2, content_y + icon_bg_size // 2),
                             icon_size=icon_inner, bg_size=icon_bg_size,
                             icon_color="#FFFFFF", bg_color=sc["border"])
            content_y += icon_bg_size + 4
        else:
            content_y += 15
        icon_y = content_y

        # Label centered — adaptive font, no forced truncation
        max_label_w = stage_w - 24
        label_font = get_font(14, "bold")
        for fs in range(16, 10, -1):
            label_font = get_font(fs, "bold")
            lw, _ = text_size(draw, node.label, label_font)
            if lw <= max_label_w:
                break
        display_label = node.label
        lw, _ = text_size(draw, display_label, label_font)
        if lw > max_label_w:
            while lw > max_label_w and len(display_label) > 3:
                display_label = display_label[:-1]
                lw, _ = text_size(draw, display_label + "..", label_font)
            display_label += ".."
            lw, _ = text_size(draw, display_label, label_font)
        draw.text(
            (sx + (stage_w - lw) // 2, icon_y),
            display_label,
            fill=hex_to_rgb(theme["text"]),
            font=label_font,
        )

        # Description — dynamic max_lines based on remaining stage space
        if node.description:
            desc_top = icon_y + 28
            remaining_h = (sy + stage_h - 8) - desc_top
            desc_fs = min(11, max(9, stage_w // 25))
            desc_font = get_font(desc_fs, "regular")
            line_h = int(desc_fs * 1.4)
            available_lines = max(1, remaining_h // line_h)
            draw_text_block(
                draw, node.description,
                (sx + 12, desc_top),
                desc_font,
                hex_to_rgb(theme["text_muted"]),
                stage_w - 24,
                line_height=line_h,
                max_lines=available_lines,
                align="center",
            )

        # Bezier arrow to next stage with connection label
        if i < n - 1:
            prev_x = sx
            prev_w = stage_w
            curr_x = margin + (i + 1) * (stage_w + arrow_gap)
            curr_y = cy - stage_h // 2

            # Find connection label from data.connections
            conn_label = None
            if data.connections:
                next_node = data.nodes[i + 1]
                for conn in data.connections:
                    if conn.from_node == node.id and conn.to_node == next_node.id:
                        conn_label = conn.label
                        break
                # Fallback: try matching by position if IDs don't match
                if conn_label is None:
                    for conn in data.connections:
                        if conn.from_node == node.id:
                            conn_label = conn.label
                            break

            draw_bezier_arrow(
                draw,
                (prev_x + prev_w, sy + stage_h // 2),
                (curr_x, curr_y + stage_h // 2),
                color=sc["border"], width=2, dashed=True,
                curvature=0.15, label=conn_label,
            )

            # Step number on arrow (retained for visual continuity)
            ax_start = sx + stage_w + 5
            ax_end = ax_start + arrow_gap - 10
            draw_step_number(
                draw,
                ((ax_start + ax_end) // 2, cy - 18),
                i + 1,
                bg_color="#FFFFFF",
                border_color=sc["border"],
                text_color=sc["border"],
                radius=12,
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
    """Render pipeline in dark mode (original style)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(img, (0, 0, width, 5), theme["gradient_start"], theme["gradient_end"])

    # Title
    title_font = get_font(28, "bold")
    tw, _ = text_size(draw, data.title, title_font)
    draw.text(((width - tw) // 2, 20), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

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

    margin = 50
    n = len(data.nodes)
    if n == 0:
        return img

    # Pipeline stages layout — content-aware height
    arrow_gap = 45
    usable_w = width - margin * 2
    stage_w = (usable_w - (n - 1) * arrow_gap) // n

    content_heights = measure_content_heights(
        data.nodes, stage_w, is_header_style=False, is_pipeline=True, min_h=80, max_h=350,
    )
    stage_h = max(content_heights.values())
    max_available = height - header_h - margin - 40
    stage_h = min(stage_h, max_available)
    cy = header_h + stage_h // 2 + 20

    node_colors = theme.get("node_colors", [theme["accent"]])

    for i, node in enumerate(data.nodes):
        color = node.color or node_colors[i % len(node_colors)]
        sx = margin + i * (stage_w + arrow_gap)
        sy = cy - stage_h // 2

        # Stage background
        draw_rounded_rect(draw, (sx, sy, sx + stage_w, sy + stage_h), 12, theme["card"], theme["border"], 2)

        # Top accent
        draw_rounded_rect(draw, (sx + 1, sy + 1, sx + stage_w - 1, sy + 5), 12, color)

        # Stage number
        stage_font = get_font(11, "semibold")
        stage_label = f"STAGE {i + 1}"
        slw, _ = text_size(draw, stage_label, stage_font)
        draw.text(
            (sx + (stage_w - slw) // 2, sy + 15),
            stage_label,
            fill=hex_to_rgb(color),
            font=stage_font,
        )

        # Icon
        icon_y = sy + 40
        if node.icon:
            paste_icon(img, node.icon.value, (sx + stage_w // 2, icon_y + 16), 32, color)
            icon_y += 45
        else:
            icon_y += 10

        # Label — adaptive font, no forced truncation
        max_label_w = stage_w - 20
        label_font = get_font(13, "bold")
        for fs in range(15, 10, -1):
            label_font = get_font(fs, "bold")
            lw, _ = text_size(draw, node.label, label_font)
            if lw <= max_label_w:
                break
        display_label = node.label
        lw, _ = text_size(draw, display_label, label_font)
        if lw > max_label_w:
            while lw > max_label_w and len(display_label) > 3:
                display_label = display_label[:-1]
                lw, _ = text_size(draw, display_label + "..", label_font)
            display_label += ".."
            lw, _ = text_size(draw, display_label, label_font)
        draw.text(
            (sx + (stage_w - lw) // 2, icon_y),
            display_label,
            fill=hex_to_rgb(theme["text"]),
            font=label_font,
        )

        # Description — dynamic max_lines based on remaining stage space
        if node.description:
            desc_top = icon_y + 25
            remaining_h = (sy + stage_h - 8) - desc_top
            desc_fs = min(11, max(9, stage_w // 25))
            desc_font = get_font(desc_fs, "regular")
            line_h = int(desc_fs * 1.4)
            available_lines = max(1, remaining_h // line_h)
            draw_text_block(
                draw, node.description,
                (sx + 10, desc_top),
                desc_font,
                hex_to_rgb(theme["text_muted"]),
                stage_w - 20,
                line_height=line_h,
                max_lines=available_lines,
                align="center",
            )

        # Arrow to next stage
        if i < n - 1:
            ax = sx + stage_w + 5
            ay = cy
            draw_straight_arrow(
                draw,
                (ax, ay),
                (ax + arrow_gap - 10, ay),
                color=theme["accent"],
                width=3,
                head_size=10,
            )

    return img
