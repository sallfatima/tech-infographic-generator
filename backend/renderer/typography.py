"""Font management and text rendering utilities."""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

from PIL import ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# System font fallbacks by platform
SYSTEM_FONTS = {
    "regular": [
        FONTS_DIR / "Inter-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
    "bold": [
        FONTS_DIR / "Inter-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ],
    "semibold": [
        FONTS_DIR / "Inter-SemiBold.ttf",
        FONTS_DIR / "Inter-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "mono": [
        FONTS_DIR / "JetBrainsMono-Regular.ttf",
        "/System/Library/Fonts/SFMono-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ],
}


@lru_cache(maxsize=64)
def get_font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    """Load a font with caching. Falls back through system fonts."""
    paths = SYSTEM_FONTS.get(weight, SYSTEM_FONTS["regular"])
    for path in paths:
        path = Path(path)
        try:
            if path.exists():
                return ImageFont.truetype(str(path), size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def wrap_text(
    draw: ImageDraw.Draw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Word-wrap text to fit within max_width pixels.

    Handles long words that exceed max_width by breaking them with hyphens.
    """
    if max_width < 10:
        return [text]
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            # Check if the single word itself exceeds max_width
            word_bbox = draw.textbbox((0, 0), word, font=font)
            word_w = word_bbox[2] - word_bbox[0]
            if word_w > max_width:
                # Character-level break with hyphen for long words
                part = ""
                for char in word:
                    test_part = part + char + "-"
                    pw = draw.textbbox((0, 0), test_part, font=font)[2]
                    if pw > max_width and part:
                        lines.append(part + "-")
                        part = char
                    else:
                        part += char
                current = part
            else:
                current = word
    if current:
        lines.append(current)
    return lines


def draw_text_block(
    draw: ImageDraw.Draw,
    text: str,
    pos: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    max_width: int,
    line_height: int = 0,
    max_lines: int = 50,
    align: str = "left",
) -> int:
    """Draw wrapped text and return the total height used."""
    if not line_height:
        line_height = int(font.size * 1.4)

    lines = wrap_text(draw, text, font, max_width)
    x, y = pos

    # Add ellipsis to last visible line if text was truncated
    total_lines = len(lines)
    visible = lines[:max_lines]
    if total_lines > max_lines and visible:
        last = visible[-1].rstrip() + "..."
        # Shrink ellipsis text if it exceeds max_width
        ew = draw.textbbox((0, 0), last, font=font)[2]
        while ew > max_width and len(last) > 4:
            last = last[:-4] + "..."
            ew = draw.textbbox((0, 0), last, font=font)[2]
        visible[-1] = last

    for i, line in enumerate(visible):
        if align == "center":
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            draw.text((x + (max_width - lw) // 2, y + i * line_height), line, fill=fill, font=font)
        elif align == "right":
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            draw.text((x + max_width - lw, y + i * line_height), line, fill=fill, font=font)
        else:
            draw.text((x, y + i * line_height), line, fill=fill, font=font)

    return len(visible) * line_height


def text_size(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    """Get the width and height of a text string."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def fit_text(
    draw: ImageDraw.Draw,
    text: str,
    max_width: int,
    max_size: int = 36,
    min_size: int = 10,
    weight: str = "bold",
) -> ImageFont.FreeTypeFont:
    """Find the largest font size that fits text within max_width."""
    for size in range(max_size, min_size - 1, -1):
        font = get_font(size, weight)
        w, _ = text_size(draw, text, font)
        if w <= max_width:
            return font
    return get_font(min_size, weight)
