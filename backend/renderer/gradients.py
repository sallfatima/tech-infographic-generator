"""Gradient rendering for backgrounds and shapes."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from .themes import hex_to_rgb


def draw_full_gradient(
    img: Image.Image,
    start_color: str,
    end_color: str,
    direction: str = "top_to_bottom",
) -> None:
    """Fill the entire canvas with a smooth gradient in-place."""
    w, h = img.size
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)

    for y in range(h):
        for x in range(w):
            if direction == "top_to_bottom":
                ratio = y / max(h - 1, 1)
            elif direction == "left_to_right":
                ratio = x / max(w - 1, 1)
            elif direction == "diagonal":
                ratio = (x / max(w - 1, 1) + y / max(h - 1, 1)) / 2
            elif direction == "radial":
                cx, cy = w / 2, h / 2
                max_dist = math.sqrt(cx**2 + cy**2)
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                ratio = min(dist / max_dist, 1.0)
            else:
                ratio = y / max(h - 1, 1)

            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            img.putpixel((x, y), (r, g, b))


def draw_gradient_bar(
    img: Image.Image,
    bbox: tuple[int, int, int, int],
    start_color: str,
    end_color: str,
    horizontal: bool = True,
) -> None:
    """Draw a gradient bar (horizontal or vertical) within a bounding box."""
    x0, y0, x1, y1 = bbox
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)

    if horizontal:
        length = x1 - x0
        for i in range(length):
            ratio = i / max(length - 1, 1)
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            for y in range(y0, y1):
                img.putpixel((x0 + i, y), (r, g, b))
    else:
        length = y1 - y0
        for j in range(length):
            ratio = j / max(length - 1, 1)
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            for x in range(x0, x1):
                img.putpixel((x, y0 + j), (r, g, b))


def draw_gradient_rect(
    img: Image.Image,
    bbox: tuple[int, int, int, int],
    start_color: str,
    end_color: str,
    radius: int = 0,
) -> None:
    """Draw a filled rectangle with a vertical gradient. Supports rounded corners via masking."""
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0

    # Create gradient strip
    grad = Image.new("RGB", (w, h))
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)
    for j in range(h):
        ratio = j / max(h - 1, 1)
        r = int(start[0] + (end[0] - start[0]) * ratio)
        g = int(start[1] + (end[1] - start[1]) * ratio)
        b = int(start[2] + (end[2] - start[2]) * ratio)
        for i in range(w):
            grad.putpixel((i, j), (r, g, b))

    if radius > 0:
        # Create rounded rectangle mask
        mask = Image.new("L", (w, h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
        img.paste(grad, (x0, y0), mask)
    else:
        img.paste(grad, (x0, y0))
