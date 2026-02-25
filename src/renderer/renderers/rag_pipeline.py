"""RAG pipeline renderer - specialized for Retrieval-Augmented Generation flows.

Shows the full RAG pipeline: Documents → Chunking → Embedding → Vector Store → Retrieval → LLM → Response

Inspired by the AI Engineering Guidebook RAG architecture diagrams.

Supports three rendering modes:
- Guidebook theme: DailyDoseofDS style with header-band stages
- Whiteboard theme: SwirlAI style with dashed borders
- Dark themes: Dark background with accent bars
"""

from PIL import Image, ImageDraw

from ..themes import hex_to_rgb
from ..typography import get_font, text_size, draw_text_block
from ..shapes import (
    draw_rounded_rect, draw_node, draw_node_with_header,
    draw_dashed_rect, draw_section_box, draw_step_number,
    draw_outer_border, draw_numbered_badge,
)
from ..arrows import draw_straight_arrow, draw_numbered_arrow
from ..gradients import draw_gradient_bar
from ..icons import paste_icon


def render_rag_pipeline(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render a RAG pipeline diagram."""
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
    """Render RAG pipeline in guidebook style (DailyDoseofDS)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    outer_color = theme.get("outer_border_color", "#5B8DEF")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=1)

    margin = 50
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

    n = len(data.nodes)
    if n == 0:
        return img

    section_colors = theme.get("section_colors", [
        {"fill": "#EBF3FF", "border": "#5B8DEF", "text": "#2B5EA7", "header_bg": "#5B8DEF"},
    ])

    # Two-row layout for RAG: top row (ingestion) and bottom row (query)
    # Split nodes: first half = ingestion, second half = query/generation
    mid = (n + 1) // 2
    top_nodes = data.nodes[:mid]
    bottom_nodes = data.nodes[mid:]

    arrow_gap = 55
    bottom_margin = 35

    def draw_row(nodes_list, row_y, row_h, start_idx=0):
        nn = len(nodes_list)
        if nn == 0:
            return {}
        usable_w = width - margin * 2
        stage_w = (usable_w - (nn - 1) * arrow_gap) // nn
        cy = row_y + row_h // 2
        positions = {}

        for i, node in enumerate(nodes_list):
            sc = section_colors[(start_idx + i) % len(section_colors)]
            color = node.color or sc["border"]
            header_bg = sc.get("header_bg", sc["border"])
            sx = margin + i * (stage_w + arrow_gap)
            sy = cy - row_h // 2

            positions[node.id] = (sx, sy, stage_w, row_h)

            draw_node_with_header(
                img, draw, (sx, sy, sx + stage_w, sy + row_h),
                label=node.label[:22], description=node.description,
                icon_name=node.icon.value if node.icon else None,
                fill_color="#FFFFFF", border_color=sc["border"],
                text_color=theme["text"], text_muted_color=theme["text_muted"],
                accent_color=color, header_bg=header_bg, icon_color="#FFFFFF",
            )

            # Numbered arrow to next
            if i < nn - 1:
                ax_start = sx + stage_w + 5
                ax_end = ax_start + arrow_gap - 10
                ay = cy

                arrow_label = None
                for conn in data.connections:
                    if conn.from_node == node.id:
                        arrow_label = conn.label
                        break

                draw_numbered_arrow(
                    draw, (ax_start, ay), (ax_end, ay),
                    number=start_idx + i + 1, label=arrow_label,
                    color=sc["border"], width=2, head_size=10, dashed=True,
                )

        return positions

    # Calculate row heights
    available_h = height - header_h - bottom_margin
    if bottom_nodes:
        row_h = (available_h - 30) // 2
        top_positions = draw_row(top_nodes, header_h + 5, row_h, start_idx=0)
        bottom_positions = draw_row(bottom_nodes, header_h + row_h + 35, row_h, start_idx=mid)

        # Draw connecting arrow between rows
        if top_nodes and bottom_nodes:
            last_top = top_nodes[-1]
            first_bottom = bottom_nodes[0]
            if last_top.id in top_positions and first_bottom.id in bottom_positions:
                tx, ty, tw_n, th_n = top_positions[last_top.id]
                bx, by, bw_n, bh_n = bottom_positions[first_bottom.id]

                # Curved arrow from last top to first bottom
                start_pt = (tx + tw_n // 2, ty + th_n)
                end_pt = (bx + bw_n // 2, by)

                sc = section_colors[mid % len(section_colors)]
                draw_straight_arrow(
                    draw, start_pt, end_pt,
                    color=sc["border"], width=2, head_size=10, dashed=True,
                )

                # Label
                conn_label = None
                for conn in data.connections:
                    if conn.from_node == last_top.id and conn.to_node == first_bottom.id:
                        conn_label = conn.label
                        break
                if conn_label:
                    mid_x = (start_pt[0] + end_pt[0]) // 2
                    mid_y = (start_pt[1] + end_pt[1]) // 2
                    label_font = get_font(10, "regular")
                    lw, _ = text_size(draw, conn_label, label_font)
                    draw.text((mid_x - lw // 2, mid_y - 8), conn_label, fill=hex_to_rgb(sc["border"]), font=label_font)
    else:
        row_h = available_h
        draw_row(top_nodes, header_h + 5, row_h, start_idx=0)

    # Footer
    if data.footer:
        footer_font = get_font(11, "regular")
        draw.text((margin, height - 25), data.footer, fill=hex_to_rgb(theme["text_muted"]), font=footer_font)

    return img


def _render_whiteboard(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render RAG pipeline in whiteboard style (SwirlAI)."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    outer_color = theme.get("outer_border_color", "#2B7DE9")
    draw_outer_border(draw, width, height, outer_color, margin=15, border_width=2)

    margin = 50
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

    n = len(data.nodes)
    if n == 0:
        return img

    section_colors = theme.get("section_colors", [
        {"fill": "#E3F2FD", "border": "#2B7DE9", "text": "#1565C0"},
    ])

    # Pipeline layout (single row, left to right)
    arrow_gap = 50
    usable_w = width - margin * 2
    stage_w = (usable_w - (n - 1) * arrow_gap) // n
    stage_h = height - header_h - margin - 30
    cy = header_h + stage_h // 2 + 15

    for i, node in enumerate(data.nodes):
        sc = section_colors[i % len(section_colors)]
        color = node.color or sc["border"]
        sx = margin + i * (stage_w + arrow_gap)
        sy = cy - stage_h // 2

        draw_section_box(
            draw, (sx, sy, sx + stage_w, sy + stage_h),
            title=f"Stage {i + 1}",
            fill_color=sc["fill"], border_color=sc["border"],
            text_color=sc["text"], dashed=True, border_width=2,
        )

        icon_y = sy + 40
        if node.icon:
            paste_icon(img, node.icon.value, (sx + stage_w // 2, icon_y + 16), 32, sc["border"])
            icon_y += 50
        else:
            icon_y += 15

        label_font = get_font(16, "bold")
        lw, _ = text_size(draw, node.label, label_font)
        draw.text(
            (sx + (stage_w - lw) // 2, icon_y),
            node.label[:22], fill=hex_to_rgb(theme["text"]), font=label_font,
        )

        if node.description:
            desc_font = get_font(11, "regular")
            draw_text_block(
                draw, node.description,
                (sx + 12, icon_y + 28), desc_font,
                hex_to_rgb(theme["text_muted"]), stage_w - 24, max_lines=4, align="center",
            )

        if i < n - 1:
            ax_start = sx + stage_w + 5
            ax_end = ax_start + arrow_gap - 10
            ay = cy

            draw_straight_arrow(
                draw, (ax_start, ay), (ax_end, ay),
                color=sc["border"], width=3, head_size=12, dashed=True,
            )
            draw_step_number(
                draw, ((ax_start + ax_end) // 2, ay - 18),
                i + 1, bg_color="#FFFFFF", border_color=sc["border"],
                text_color=sc["border"], radius=12,
            )

    return img


def _render_dark(
    data,
    width: int,
    height: int,
    theme: dict,
) -> Image.Image:
    """Render RAG pipeline in dark mode."""
    img = Image.new("RGB", (width, height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    draw_gradient_bar(img, (0, 0, width, 5), theme["gradient_start"], theme["gradient_end"])

    title_font = get_font(28, "bold")
    tw, _ = text_size(draw, data.title, title_font)
    draw.text(((width - tw) // 2, 20), data.title, fill=hex_to_rgb(theme["text"]), font=title_font)

    header_h = 70
    if data.subtitle:
        sub_font = get_font(14, "regular")
        sw, _ = text_size(draw, data.subtitle, sub_font)
        draw.text(((width - sw) // 2, 55), data.subtitle, fill=hex_to_rgb(theme["text_muted"]), font=sub_font)
        header_h = 85

    margin = 50
    n = len(data.nodes)
    if n == 0:
        return img

    arrow_gap = 45
    usable_w = width - margin * 2
    stage_w = (usable_w - (n - 1) * arrow_gap) // n
    stage_h = height - header_h - margin - 40
    cy = header_h + stage_h // 2 + 20

    node_colors = theme.get("node_colors", [theme["accent"]])

    for i, node in enumerate(data.nodes):
        color = node.color or node_colors[i % len(node_colors)]
        sx = margin + i * (stage_w + arrow_gap)
        sy = cy - stage_h // 2

        draw_rounded_rect(draw, (sx, sy, sx + stage_w, sy + stage_h), 12, theme["card"], theme["border"], 2)
        draw_rounded_rect(draw, (sx + 1, sy + 1, sx + stage_w - 1, sy + 5), 12, color)

        stage_font = get_font(11, "semibold")
        stage_label = f"STAGE {i + 1}"
        slw, _ = text_size(draw, stage_label, stage_font)
        draw.text((sx + (stage_w - slw) // 2, sy + 15), stage_label, fill=hex_to_rgb(color), font=stage_font)

        icon_y = sy + 40
        if node.icon:
            paste_icon(img, node.icon.value, (sx + stage_w // 2, icon_y + 16), 32, color)
            icon_y += 45
        else:
            icon_y += 10

        label_font = get_font(15, "bold")
        lw, _ = text_size(draw, node.label, label_font)
        draw.text((sx + (stage_w - lw) // 2, icon_y), node.label[:20], fill=hex_to_rgb(theme["text"]), font=label_font)

        if node.description:
            desc_font = get_font(11, "regular")
            draw_text_block(
                draw, node.description,
                (sx + 10, icon_y + 25), desc_font,
                hex_to_rgb(theme["text_muted"]), stage_w - 20, max_lines=4, align="center",
            )

        if i < n - 1:
            ax = sx + stage_w + 5
            ay = cy
            draw_straight_arrow(
                draw, (ax, ay), (ax + arrow_gap - 10, ay),
                color=theme["accent"], width=3, head_size=10,
            )

    return img
