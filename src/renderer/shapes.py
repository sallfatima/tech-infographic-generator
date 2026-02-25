"""Shape rendering for infographic nodes."""

import math

from PIL import Image, ImageDraw

from .themes import hex_to_rgb, hex_to_rgba
from .icons import paste_icon
from .typography import get_font, text_size, draw_text_block


def draw_rounded_rect(
    draw: ImageDraw.Draw,
    bbox: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
    outline_width: int = 1,
) -> None:
    fill_rgb = hex_to_rgb(fill)
    outline_rgb = hex_to_rgb(outline) if outline else None
    x0, y0, x1, y1 = bbox
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    draw.rounded_rectangle(bbox, radius=r, fill=fill_rgb, outline=outline_rgb, width=outline_width)


def draw_circle(
    draw: ImageDraw.Draw,
    center: tuple[int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
) -> None:
    cx, cy = center
    fill_rgb = hex_to_rgb(fill)
    outline_rgb = hex_to_rgb(outline) if outline else None
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=fill_rgb,
        outline=outline_rgb,
    )


def draw_diamond(
    draw: ImageDraw.Draw,
    center: tuple[int, int],
    width: int,
    height: int,
    fill: str,
    outline: str | None = None,
) -> None:
    cx, cy = center
    hw, hh = width // 2, height // 2
    points = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
    draw.polygon(points, fill=hex_to_rgb(fill), outline=hex_to_rgb(outline) if outline else None)


def draw_cylinder(
    draw: ImageDraw.Draw,
    bbox: tuple[int, int, int, int],
    fill: str,
    outline: str | None = None,
) -> None:
    """Draw a database cylinder shape."""
    x0, y0, x1, y1 = bbox
    ellipse_h = (y1 - y0) // 5
    fill_rgb = hex_to_rgb(fill)
    outline_rgb = hex_to_rgb(outline) if outline else fill_rgb

    # Body rectangle
    draw.rectangle((x0, y0 + ellipse_h // 2, x1, y1 - ellipse_h // 2), fill=fill_rgb)
    # Top ellipse
    draw.ellipse((x0, y0, x1, y0 + ellipse_h), fill=fill_rgb, outline=outline_rgb)
    # Bottom ellipse
    draw.ellipse((x0, y1 - ellipse_h, x1, y1), fill=fill_rgb, outline=outline_rgb)
    # Side lines
    draw.line([(x0, y0 + ellipse_h // 2), (x0, y1 - ellipse_h // 2)], fill=outline_rgb, width=1)
    draw.line([(x1, y0 + ellipse_h // 2), (x1, y1 - ellipse_h // 2)], fill=outline_rgb, width=1)
    # Top ellipse highlight (lighter shade)
    lighter = tuple(min(c + 30, 255) for c in fill_rgb)
    draw.ellipse((x0 + 2, y0 + 2, x1 - 2, y0 + ellipse_h - 2), fill=lighter)


def draw_hexagon(
    draw: ImageDraw.Draw,
    center: tuple[int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
) -> None:
    cx, cy = center
    points = []
    for i in range(6):
        angle = math.pi / 6 + i * math.pi / 3
        px = cx + int(radius * math.cos(angle))
        py = cy + int(radius * math.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=hex_to_rgb(fill), outline=hex_to_rgb(outline) if outline else None)


def draw_cloud(
    draw: ImageDraw.Draw,
    bbox: tuple[int, int, int, int],
    fill: str,
) -> None:
    """Draw a simplified cloud shape using overlapping ellipses."""
    x0, y0, x1, y1 = bbox
    fill_rgb = hex_to_rgb(fill)
    w, h = x1 - x0, y1 - y0
    cy = y0 + h * 0.55

    # Main body
    draw.ellipse((x0 + w * 0.1, cy - h * 0.25, x0 + w * 0.9, cy + h * 0.35), fill=fill_rgb)
    # Left bump
    draw.ellipse((x0, cy - h * 0.15, x0 + w * 0.45, cy + h * 0.35), fill=fill_rgb)
    # Right bump
    draw.ellipse((x0 + w * 0.55, cy - h * 0.15, x1, cy + h * 0.35), fill=fill_rgb)
    # Top bump
    draw.ellipse((x0 + w * 0.25, y0, x0 + w * 0.65, cy + h * 0.1), fill=fill_rgb)
    # Top-right bump
    draw.ellipse((x0 + w * 0.45, y0 + h * 0.05, x0 + w * 0.8, cy + h * 0.1), fill=fill_rgb)


def draw_dashed_rect(
    draw: ImageDraw.Draw,
    bbox: tuple[int, int, int, int],
    color: str,
    width: int = 2,
    dash: int = 10,
    gap: int = 6,
    radius: int = 8,
) -> None:
    """Draw a dashed rounded rectangle (SwirlAI style section borders)."""
    x0, y0, x1, y1 = bbox
    color_rgb = hex_to_rgb(color)
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)

    # Draw 4 dashed edges (simplified: skip corners for now)
    edges = [
        ((x0 + r, y0), (x1 - r, y0)),  # top
        ((x1, y0 + r), (x1, y1 - r)),  # right
        ((x1 - r, y1), (x0 + r, y1)),  # bottom
        ((x0, y1 - r), (x0, y0 + r)),  # left
    ]
    for start, end in edges:
        sx, sy = start
        ex, ey = end
        dx, dy = ex - sx, ey - sy
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1:
            continue
        ux, uy = dx / length, dy / length
        pos = 0.0
        while pos < length:
            s = (int(sx + ux * pos), int(sy + uy * pos))
            e_pos = min(pos + dash, length)
            e = (int(sx + ux * e_pos), int(sy + uy * e_pos))
            draw.line([s, e], fill=color_rgb, width=width)
            pos += dash + gap

    # Draw corner arcs as small curved sections
    corners = [
        ((x1 - 2 * r, y0, x1, y0 + 2 * r), 270, 360),      # top-right
        ((x1 - 2 * r, y1 - 2 * r, x1, y1), 0, 90),          # bottom-right
        ((x0, y1 - 2 * r, x0 + 2 * r, y1), 90, 180),        # bottom-left
        ((x0, y0, x0 + 2 * r, y0 + 2 * r), 180, 270),       # top-left
    ]
    for arc_bbox, start_angle, end_angle in corners:
        draw.arc(arc_bbox, start_angle, end_angle, fill=color_rgb, width=width)


def draw_section_box(
    draw: ImageDraw.Draw,
    bbox: tuple[int, int, int, int],
    title: str,
    fill_color: str = "#E3F2FD",
    border_color: str = "#2B7DE9",
    text_color: str = "#1565C0",
    dashed: bool = True,
    border_width: int = 2,
) -> None:
    """Draw a labeled section box with optional dashed border (SwirlAI style)."""
    x0, y0, x1, y1 = bbox

    # Fill background
    fill_rgb = hex_to_rgb(fill_color)
    draw.rounded_rectangle(bbox, radius=10, fill=fill_rgb)

    # Border
    if dashed:
        draw_dashed_rect(draw, bbox, border_color, border_width, dash=10, gap=6, radius=10)
    else:
        draw.rounded_rectangle(bbox, radius=10, outline=hex_to_rgb(border_color), width=border_width)

    # Title label in top area
    title_font = get_font(18, "bold")
    tw, th = text_size(draw, title, title_font)
    title_pad = 10
    # Title box
    title_x = x0 + 20
    title_y = y0 - th // 2 - 2  # Straddle the top border
    draw.rounded_rectangle(
        (title_x - title_pad, title_y - 3, title_x + tw + title_pad, title_y + th + 5),
        radius=6,
        fill=hex_to_rgb("#FFFFFF"),
        outline=hex_to_rgb(border_color),
        width=2,
    )
    draw.text(
        (title_x, title_y),
        title,
        fill=hex_to_rgb(text_color),
        font=title_font,
    )


def draw_step_number(
    draw: ImageDraw.Draw,
    center: tuple[int, int],
    number: int,
    bg_color: str = "#FFFFFF",
    border_color: str = "#2B7DE9",
    text_color: str = "#2B7DE9",
    radius: int = 16,
) -> None:
    """Draw a circled step number like ①②③."""
    cx, cy = center
    # Circle with border
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=hex_to_rgb(bg_color),
        outline=hex_to_rgb(border_color),
        width=2,
    )
    # Number text
    num_font = get_font(14, "bold")
    num_text = f"{number}."
    nw, nh = text_size(draw, num_text, num_font)
    draw.text(
        (cx - nw // 2, cy - nh // 2),
        num_text,
        fill=hex_to_rgb(text_color),
        font=num_font,
    )


def draw_outer_border(
    draw: ImageDraw.Draw,
    width: int,
    height: int,
    color: str = "#2B7DE9",
    margin: int = 12,
    border_width: int = 2,
) -> None:
    """Draw a dashed outer border around the entire infographic (SwirlAI style)."""
    draw_dashed_rect(
        draw,
        (margin, margin, width - margin, height - margin),
        color,
        border_width,
        dash=12,
        gap=8,
        radius=12,
    )


def draw_node_with_header(
    img: Image.Image,
    draw: ImageDraw.Draw,
    bbox: tuple[int, int, int, int],
    label: str,
    description: str | None = None,
    icon_name: str | None = None,
    shape: str = "rounded_rect",
    fill_color: str = "#FFFFFF",
    border_color: str = "#5B8DEF",
    text_color: str = "#2D3142",
    text_muted_color: str = "#8D99AE",
    accent_color: str = "#5B8DEF",
    header_bg: str = "#5B8DEF",
    icon_color: str = "#FFFFFF",
) -> None:
    """Draw a node with a colored header band (DailyDoseofDS guidebook style).

    The header band spans the top of the node with the label in white text.
    The body shows description and icon on a light background.
    """
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) // 2
    w, h = x1 - x0, y1 - y0
    radius = 10
    # Compact header — proportional but not too big
    header_h = max(26, min(34, h // 4))

    # Special shapes: fall back to regular draw_node
    if shape in ("cylinder", "diamond", "circle", "hexagon", "cloud"):
        draw_node(
            img, draw, bbox, label, description, icon_name, shape,
            fill_color, border_color, text_color, text_muted_color,
            accent_color, icon_color,
        )
        return

    # Main card with border
    draw.rounded_rectangle(bbox, radius=radius, fill=hex_to_rgb(fill_color), outline=hex_to_rgb(border_color), width=2)

    # Colored header band (top)
    header_box = (x0 + 1, y0 + 1, x1 - 1, y0 + header_h)
    draw.rounded_rectangle(
        header_box, radius=radius, fill=hex_to_rgb(header_bg),
    )
    # Flatten the bottom corners of the header
    draw.rectangle(
        (x0 + 1, y0 + header_h - radius, x1 - 1, y0 + header_h),
        fill=hex_to_rgb(header_bg),
    )

    # Header label — adaptive font: try largest that fits, then truncate
    max_label_w = w - 16
    label_font = get_font(10, "bold")  # fallback
    for fs in range(min(15, max(11, h // 6)), 9, -1):
        label_font = get_font(fs, "bold")
        lw, lh = text_size(draw, label, label_font)
        if lw <= max_label_w:
            break

    display_label = label
    lw, lh = text_size(draw, display_label, label_font)
    if lw > max_label_w:
        while lw > max_label_w and len(display_label) > 3:
            display_label = display_label[:-1]
            lw, lh = text_size(draw, display_label + "..", label_font)
        display_label += ".."
        lw, lh = text_size(draw, display_label, label_font)

    draw.text(
        (cx - lw // 2, y0 + (header_h - lh) // 2),
        display_label,
        fill=hex_to_rgb("#FFFFFF"),
        font=label_font,
    )

    # Body content below header — use space efficiently
    body_top = y0 + header_h + 4
    body_h = h - header_h - 8
    body_w = w - 14
    content_y = body_top

    # Icon in body (smaller, only if enough room)
    if icon_name and body_h > 45:
        icon_size = min(20, body_h // 4)
        paste_icon(img, icon_name, (cx, content_y + icon_size // 2), icon_size, accent_color)
        content_y += icon_size + 3

    # Description — dynamic max_lines based on remaining space
    if description and body_h > 20:
        remaining_h = (y1 - 6) - content_y
        desc_fs = min(11, max(9, h // 10))
        desc_font = get_font(desc_fs, "regular")
        line_h = int(desc_fs * 1.35)
        available_lines = max(1, remaining_h // line_h)
        draw_text_block(
            draw, description,
            (x0 + 7, content_y),
            desc_font,
            hex_to_rgb(text_muted_color),
            body_w,
            line_height=line_h,
            max_lines=available_lines,
            align="center",
        )


def draw_numbered_badge(
    draw: ImageDraw.Draw,
    position: tuple[int, int],
    number: int,
    label: str | None = None,
    bg_color: str = "#5B8DEF",
    text_color: str = "#FFFFFF",
    size: int = 22,
) -> None:
    """Draw a numbered circle badge with optional label (guidebook style).

    Like: (1) Encode  or  (3) Similarity search
    """
    cx, cy = position
    r = size // 2

    # Circle with number
    draw.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        fill=hex_to_rgb(bg_color),
    )
    num_font = get_font(max(10, size // 2), "bold")
    num_text = str(number)
    nw, nh = text_size(draw, num_text, num_font)
    draw.text(
        (cx - nw // 2, cy - nh // 2),
        num_text,
        fill=hex_to_rgb(text_color),
        font=num_font,
    )

    # Optional label text next to the badge
    if label:
        label_font = get_font(11, "semibold")
        lw, lh = text_size(draw, label, label_font)
        draw.text(
            (cx + r + 5, cy - lh // 2),
            label,
            fill=hex_to_rgb(bg_color),
            font=label_font,
        )


def draw_node(
    img: Image.Image,
    draw: ImageDraw.Draw,
    bbox: tuple[int, int, int, int],
    label: str,
    description: str | None = None,
    icon_name: str | None = None,
    shape: str = "rounded_rect",
    fill_color: str = "#1E293B",
    border_color: str = "#334155",
    text_color: str = "#F8FAFC",
    text_muted_color: str = "#94A3B8",
    accent_color: str = "#3B82F6",
    icon_color: str = "#FFFFFF",
) -> None:
    """Draw a complete node with shape, icon, label, and description."""
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) // 2
    w, h = x1 - x0, y1 - y0

    # Draw the shape
    if shape == "cylinder":
        draw_cylinder(draw, bbox, fill_color, border_color)
    elif shape == "diamond":
        draw_diamond(draw, (cx, (y0 + y1) // 2), w, h, fill_color, border_color)
    elif shape == "circle":
        r = min(w, h) // 2
        draw_circle(draw, (cx, (y0 + y1) // 2), r, fill_color, border_color)
    elif shape == "hexagon":
        r = min(w, h) // 2
        draw_hexagon(draw, (cx, (y0 + y1) // 2), r, fill_color, border_color)
    elif shape == "cloud":
        draw_cloud(draw, bbox, fill_color)
    else:
        draw_rounded_rect(draw, bbox, 10, fill_color, border_color, 2)

    # Draw accent bar on top
    if shape in ("rounded_rect", "rectangle"):
        accent_h = 3
        draw.rounded_rectangle(
            (x0 + 1, y0 + 1, x1 - 1, y0 + accent_h + 6),
            radius=10,
            fill=hex_to_rgb(accent_color),
        )
        # Redraw bottom of accent to be flat
        draw.rectangle(
            (x0 + 1, y0 + 6, x1 - 1, y0 + accent_h + 6),
            fill=hex_to_rgb(fill_color),
        )

    # Layout content vertically inside the node
    padding = 12
    content_y = y0 + padding + 6
    content_w = w - padding * 2

    # Icon
    if icon_name:
        icon_size = min(28, h // 4)
        paste_icon(img, icon_name, (cx, content_y + icon_size // 2), icon_size, icon_color)
        content_y += icon_size + 6

    # Label
    label_font = get_font(min(16, max(11, h // 6)), "bold")
    lw, lh = text_size(draw, label, label_font)
    draw.text(
        (cx - lw // 2, content_y),
        label,
        fill=hex_to_rgb(text_color),
        font=label_font,
    )
    content_y += lh + 4

    # Description
    if description and h > 70:
        desc_font = get_font(min(12, max(9, h // 8)), "regular")
        draw_text_block(
            draw, description,
            (x0 + padding, content_y),
            desc_font,
            hex_to_rgb(text_muted_color),
            content_w,
            max_lines=3,
            align="center",
        )
