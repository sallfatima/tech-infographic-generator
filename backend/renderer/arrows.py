"""Arrow and connection rendering between nodes.

Uses Manhattan routing (orthogonal paths) for clean architecture diagrams.
Arrows go vertical then horizontal (or vice versa) to avoid crossing nodes.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from .themes import hex_to_rgb
from .typography import get_font, text_size


def _draw_arrowhead(
    draw: ImageDraw.Draw,
    tip: tuple[int, int],
    angle: float,
    size: int,
    color: tuple,
) -> None:
    """Draw a filled triangle arrowhead at the given position and angle."""
    tx, ty = tip
    left_angle = angle + math.pi * 0.82
    right_angle = angle - math.pi * 0.82
    points = [
        (tx, ty),
        (int(tx + size * math.cos(left_angle)), int(ty + size * math.sin(left_angle))),
        (int(tx + size * math.cos(right_angle)), int(ty + size * math.sin(right_angle))),
    ]
    draw.polygon(points, fill=color)


def _draw_polyline(
    draw: ImageDraw.Draw,
    points: list[tuple[int, int]],
    color: tuple,
    width: int,
    dashed: bool = False,
) -> None:
    """Draw a multi-segment polyline (list of points)."""
    for i in range(len(points) - 1):
        if dashed:
            _draw_dashed_line(draw, points[i], points[i + 1], color, width)
        else:
            draw.line([points[i], points[i + 1]], fill=color, width=width)


def _draw_dashed_line(
    draw: ImageDraw.Draw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple,
    width: int,
    dash_length: int = 8,
    gap_length: int = 5,
) -> None:
    """Draw a dashed line segment."""
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = math.sqrt(dx ** 2 + dy ** 2)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    segment = dash_length + gap_length
    pos = 0.0
    while pos < length:
        s = (int(sx + ux * pos), int(sy + uy * pos))
        e_pos = min(pos + dash_length, length)
        e = (int(sx + ux * e_pos), int(sy + uy * e_pos))
        draw.line([s, e], fill=color, width=width)
        pos += segment


def _manhattan_route(
    start: tuple[int, int],
    end: tuple[int, int],
    direction: str = "auto",
) -> list[tuple[int, int]]:
    """Build a Manhattan (orthogonal) route from start to end.

    Returns a list of waypoints including start and end.

    direction:
        "auto"  - pick best based on relative position
        "v_first" - go vertical first, then horizontal
        "h_first" - go horizontal first, then vertical
    """
    sx, sy = start
    ex, ey = end
    dx = abs(ex - sx)
    dy = abs(ey - sy)

    # If points are already aligned, just use a straight line
    if dx < 3:  # Vertically aligned
        return [(sx, sy), (sx, ey)]
    if dy < 3:  # Horizontally aligned
        return [(sx, sy), (ex, sy)]

    if direction == "auto":
        # If mostly vertical movement, go vertical first
        if dy > dx * 0.5:
            direction = "v_first"
        else:
            direction = "h_first"

    if direction == "v_first":
        mid_y = (sy + ey) // 2
        return [
            (sx, sy),
            (sx, mid_y),
            (ex, mid_y),
            (ex, ey),
        ]
    else:
        mid_x = (sx + ex) // 2
        return [
            (sx, sy),
            (mid_x, sy),
            (mid_x, ey),
            (ex, ey),
        ]


def draw_manhattan_arrow(
    draw: ImageDraw.Draw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = "#94A3B8",
    width: int = 2,
    head_size: int = 10,
    dashed: bool = False,
    direction: str = "auto",
    label: str | None = None,
) -> None:
    """Draw an arrow that follows orthogonal (Manhattan) routing."""
    color_rgb = hex_to_rgb(color)
    points = _manhattan_route(start, end, direction)

    # Simplify: remove zero-length segments
    clean_points = [points[0]]
    for p in points[1:]:
        if p != clean_points[-1]:
            clean_points.append(p)
    points = clean_points

    if len(points) < 2:
        return

    _draw_polyline(draw, points, color_rgb, width, dashed)

    # Arrowhead at the final point
    last = points[-1]
    prev = points[-2]
    angle = math.atan2(last[1] - prev[1], last[0] - prev[0])
    _draw_arrowhead(draw, last, angle, head_size, color_rgb)

    # Label at the middle segment
    if label:
        _draw_label_on_path(draw, points, label, color)


def draw_straight_arrow(
    draw: ImageDraw.Draw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = "#94A3B8",
    width: int = 2,
    head_size: int = 10,
    dashed: bool = False,
) -> None:
    """Draw a simple straight arrow from start to end."""
    color_rgb = hex_to_rgb(color)
    if dashed:
        _draw_dashed_line(draw, start, end, color_rgb, width)
    else:
        draw.line([start, end], fill=color_rgb, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    _draw_arrowhead(draw, end, angle, head_size, color_rgb)


def draw_bidirectional_arrow(
    draw: ImageDraw.Draw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = "#94A3B8",
    width: int = 2,
    head_size: int = 10,
    offset: int = 4,
) -> None:
    """Draw two parallel arrows in opposite directions (offset to not overlap)."""
    color_rgb = hex_to_rgb(color)
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = math.sqrt(dx ** 2 + dy ** 2)
    if length == 0:
        return

    # Perpendicular normal for offset
    nx, ny = -dy / length * offset, dx / length * offset

    # Forward arrow (offset left)
    s1 = (int(sx + nx), int(sy + ny))
    e1 = (int(ex + nx), int(ey + ny))
    draw.line([s1, e1], fill=color_rgb, width=width)
    angle_fwd = math.atan2(e1[1] - s1[1], e1[0] - s1[0])
    _draw_arrowhead(draw, e1, angle_fwd, head_size, color_rgb)

    # Backward arrow (offset right)
    s2 = (int(sx - nx), int(sy - ny))
    e2 = (int(ex - nx), int(ey - ny))
    draw.line([e2, s2], fill=color_rgb, width=width)
    angle_bwd = math.atan2(s2[1] - e2[1], s2[0] - e2[0])
    _draw_arrowhead(draw, s2, angle_bwd, head_size, color_rgb)


def _draw_label_on_path(
    draw: ImageDraw.Draw,
    points: list[tuple[int, int]],
    label: str,
    color: str,
) -> None:
    """Draw a label on the middle segment of a polyline path.

    Positions the label offset from the line so it doesn't overlap with nodes:
    - For horizontal segments: label is placed above the line
    - For vertical segments: label is placed to the right of the line
    """
    if len(points) < 2:
        return

    # Find the longest segment to place the label
    best_i = 0
    best_len = 0
    for i in range(len(points) - 1):
        dx = points[i + 1][0] - points[i][0]
        dy = points[i + 1][1] - points[i][1]
        seg_len = math.sqrt(dx ** 2 + dy ** 2)
        if seg_len > best_len:
            best_len = seg_len
            best_i = i

    mx = (points[best_i][0] + points[best_i + 1][0]) // 2
    my = (points[best_i][1] + points[best_i + 1][1]) // 2

    font = get_font(11, "semibold")
    tw, th = text_size(draw, label, font)
    padding = 5

    # Determine if segment is horizontal or vertical and offset label
    seg_dx = abs(points[best_i + 1][0] - points[best_i][0])
    seg_dy = abs(points[best_i + 1][1] - points[best_i][1])

    if seg_dx > seg_dy:
        # Horizontal segment -> place label above
        my -= th // 2 + padding + 5
    else:
        # Vertical segment -> place label to the right
        mx += padding + 5

    # Detect if we're on a light or dark background based on the color luminance
    # Using perceived brightness formula: 0.299*R + 0.587*G + 0.114*B
    color_rgb = hex_to_rgb(color)
    luminance = 0.299 * color_rgb[0] + 0.587 * color_rgb[1] + 0.114 * color_rgb[2]

    # If the line color is vivid/medium (not very dark), we're likely on a light background
    # Colors like #2B7DE9 (blue), #E8833A (orange), #4CAF50 (green) → light bg
    # Colors like #94A3B8 (muted gray on dark) → dark bg
    is_light_bg = luminance > 60  # Most colored lines are >60, muted grays on dark are lower

    if is_light_bg:
        # Light background (whiteboard): white pill with colored border
        pill_fill = "#FFFFFF"
        pill_outline = color
        text_fill = color
    else:
        # Dark background: dark pill
        pill_fill = "#0F172A"
        pill_outline = "#334155"
        text_fill = color

    # Draw background pill
    draw.rounded_rectangle(
        (mx - tw // 2 - padding, my - th // 2 - padding,
         mx + tw // 2 + padding, my + th // 2 + padding),
        radius=5,
        fill=hex_to_rgb(pill_fill),
        outline=hex_to_rgb(pill_outline),
        width=1,
    )
    draw.text(
        (mx - tw // 2, my - th // 2),
        label,
        fill=hex_to_rgb(text_fill),
        font=font,
    )


def draw_numbered_arrow(
    draw: ImageDraw.Draw,
    start: tuple[int, int],
    end: tuple[int, int],
    number: int,
    label: str | None = None,
    color: str = "#5B8DEF",
    width: int = 2,
    head_size: int = 10,
    dashed: bool = True,
    badge_size: int = 20,
) -> None:
    """Draw a dashed arrow with a numbered badge and label (DailyDoseofDS guidebook style).

    Example output: ----①Encode---->
    The numbered circle sits on the arrow path, with the label next to it.
    """
    color_rgb = hex_to_rgb(color)

    # Draw the dashed line
    if dashed:
        _draw_dashed_line(draw, start, end, color_rgb, width)
    else:
        draw.line([start, end], fill=color_rgb, width=width)

    # Arrowhead
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    _draw_arrowhead(draw, end, angle, head_size, color_rgb)

    # Position the badge at ~40% along the line
    t = 0.4
    mx = int(start[0] + t * (end[0] - start[0]))
    my = int(start[1] + t * (end[1] - start[1]))

    # White circle background for the number
    r = badge_size // 2
    draw.ellipse(
        (mx - r - 1, my - r - 1, mx + r + 1, my + r + 1),
        fill=(255, 255, 255),
        outline=color_rgb,
        width=2,
    )

    # Number text
    num_font = get_font(max(9, badge_size // 2), "bold")
    num_text = str(number)
    nw, nh = text_size(draw, num_text, num_font)
    draw.text(
        (mx - nw // 2, my - nh // 2),
        num_text,
        fill=color_rgb,
        font=num_font,
    )

    # Label next to the badge
    if label:
        label_font = get_font(10, "semibold")
        lw, lh = text_size(draw, label, label_font)

        # Position label above or below the line depending on direction
        sx, sy = start
        ex, ey = end
        is_horizontal = abs(ex - sx) > abs(ey - sy)

        if is_horizontal:
            # Label above the line
            lx = mx + r + 4
            ly = my - lh - 3
        else:
            # Label to the right of the line
            lx = mx + r + 4
            ly = my - lh // 2

        # White background for readability
        pad = 3
        draw.rounded_rectangle(
            (lx - pad, ly - pad, lx + lw + pad, ly + lh + pad),
            radius=3,
            fill=(255, 255, 255),
            outline=color_rgb,
            width=1,
        )
        draw.text(
            (lx, ly),
            label,
            fill=color_rgb,
            font=label_font,
        )


def _sample_quadratic_bezier(
    p0: tuple[int, int],
    p1: tuple[int, int],
    p2: tuple[int, int],
    n_points: int = 30,
) -> list[tuple[int, int]]:
    """Sample N points along a quadratic bezier curve P0->P1->P2."""
    pts = []
    for i in range(n_points + 1):
        t = i / n_points
        inv = 1 - t
        x = inv * inv * p0[0] + 2 * inv * t * p1[0] + t * t * p2[0]
        y = inv * inv * p0[1] + 2 * inv * t * p1[1] + t * t * p2[1]
        pts.append((int(x), int(y)))
    return pts


def draw_bezier_arrow(
    draw: ImageDraw.Draw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = "#2B7DE9",
    width: int = 2,
    head_size: int = 10,
    dashed: bool = True,
    curvature: float = 0.25,
    label: str | None = None,
    flip_curve: bool = False,
) -> None:
    """Draw a curved bezier arrow (SwirlAI style).

    The curve bends perpendicular to the start-end line. The `flip_curve`
    flag controls which side the curve bends toward.
    """
    color_rgb = hex_to_rgb(color)

    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 5:
        return

    # Perpendicular offset for control point
    offset = dist * curvature
    if flip_curve:
        offset = -offset
    # Perpendicular direction
    nx, ny = -dy / dist, dx / dist
    # Control point at midpoint + perpendicular offset
    cx_ctrl = (sx + ex) / 2 + nx * offset
    cy_ctrl = (sy + ey) / 2 + ny * offset

    # Sample the curve
    n_samples = max(20, int(dist / 3))
    pts = _sample_quadratic_bezier(
        (sx, sy), (int(cx_ctrl), int(cy_ctrl)), (ex, ey), n_samples
    )

    # Draw as polyline (dashed or solid)
    _draw_polyline(draw, pts, color_rgb, width, dashed=dashed)

    # Arrowhead from last two points
    if len(pts) >= 2:
        angle = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
        _draw_arrowhead(draw, pts[-1], angle, head_size, color_rgb)

    # Label at the curve midpoint (t=0.5)
    if label:
        mid_idx = len(pts) // 2
        _draw_path_label(draw, pts[mid_idx], label, color)


def _draw_path_label(
    draw: ImageDraw.Draw,
    position: tuple[int, int],
    label: str,
    color: str,
) -> None:
    """Draw a connection label at a position with white pill background.

    Uses semibold font to simulate italic style (SwirlAI reference).
    Positioned with slight offset above the point.
    """
    font = get_font(11, "semibold")
    tw, th = text_size(draw, label, font)
    px, py = position
    # Offset slightly above the curve
    py -= th // 2 + 6
    pad = 5

    # White pill bg with subtle border
    draw.rounded_rectangle(
        (px - tw // 2 - pad, py - pad,
         px + tw // 2 + pad, py + th + pad),
        radius=4,
        fill=(255, 255, 255, 230),
        outline=hex_to_rgb(color),
        width=1,
    )
    draw.text(
        (px - tw // 2, py),
        label,
        fill=hex_to_rgb(color),
        font=font,
    )


def draw_connection(
    draw: ImageDraw.Draw,
    start: tuple[int, int],
    end: tuple[int, int],
    style: str = "arrow",
    label: str | None = None,
    color: str = "#94A3B8",
    width: int = 2,
    routing: str = "manhattan",
) -> None:
    """Draw a connection between two points with optional label.

    Args:
        routing: "manhattan" for orthogonal routing, "straight" for direct lines,
                 "bezier" for curved bezier arrows.
    """
    # Handle curved styles regardless of routing
    if style in ("curved_arrow", "curved_dashed"):
        dashed = style == "curved_dashed"
        draw_bezier_arrow(draw, start, end, color, width, dashed=dashed, label=label)
        return

    if routing == "bezier":
        draw_bezier_arrow(draw, start, end, color, width, dashed=True, label=label)
        return

    if routing == "manhattan":
        if style == "bidirectional":
            draw_bidirectional_arrow(draw, start, end, color, width)
            if label:
                mx = (start[0] + end[0]) // 2
                my = (start[1] + end[1]) // 2
                _draw_label_on_path(draw, [start, end], label, color)
        elif style == "dashed_arrow":
            draw_manhattan_arrow(draw, start, end, color, width, dashed=True, label=label)
        elif style == "line":
            points = _manhattan_route(start, end)
            _draw_polyline(draw, points, hex_to_rgb(color), width)
        else:
            draw_manhattan_arrow(draw, start, end, color, width, label=label)
    else:
        # Straight line fallback
        if style == "bidirectional":
            draw_bidirectional_arrow(draw, start, end, color, width)
        elif style == "dashed_arrow":
            draw_straight_arrow(draw, start, end, color, width, dashed=True)
        elif style == "line":
            draw.line([start, end], fill=hex_to_rgb(color), width=width)
        else:
            draw_straight_arrow(draw, start, end, color, width)

        if label:
            _draw_label_on_path(draw, [start, end], label, color)
