"""SVG icon loading, tinting, and rendering."""

import io
import re
from pathlib import Path
from functools import lru_cache

from PIL import Image

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

# Try CairoSVG, fall back to PIL-only approach
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


def _tint_svg(svg_content: str, color: str) -> str:
    """Replace fill colors in SVG with the target color."""
    # Replace existing fill attributes
    result = re.sub(r'fill="[^"]*"', f'fill="{color}"', svg_content)
    # Replace existing stroke attributes
    result = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', result)
    # If no fill was set, add it to root svg
    if f'fill="{color}"' not in result:
        result = result.replace("<svg", f'<svg fill="{color}"', 1)
    return result


@lru_cache(maxsize=128)
def load_icon(name: str, size: int = 32, color: str = "#FFFFFF") -> Image.Image | None:
    """Load an SVG icon, tint it, and return as a PIL RGBA Image.

    Returns None if the icon file doesn't exist or can't be loaded.
    """
    svg_path = ICONS_DIR / f"{name}.svg"
    if not svg_path.exists():
        return _create_fallback_icon(size, color)

    svg_content = svg_path.read_text()
    svg_content = _tint_svg(svg_content, color)

    if HAS_CAIROSVG:
        try:
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode(),
                output_width=size,
                output_height=size,
            )
            return Image.open(io.BytesIO(png_data)).convert("RGBA")
        except Exception:
            return _create_fallback_icon(size, color)
    else:
        return _create_fallback_icon(size, color)


def _create_fallback_icon(size: int, color: str) -> Image.Image:
    """Create a simple circle icon as fallback when SVG rendering isn't available."""
    from PIL import ImageDraw
    from .themes import hex_to_rgb

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = size // 6
    fill = hex_to_rgb(color) + (200,)
    draw.ellipse((margin, margin, size - margin, size - margin), fill=fill)
    return img


def paste_icon(
    canvas: Image.Image,
    name: str,
    pos: tuple[int, int],
    size: int = 32,
    color: str = "#FFFFFF",
) -> None:
    """Load and paste an icon onto the canvas at (x, y)."""
    icon = load_icon(name, size, color)
    if icon is None:
        return
    # Center the icon at the position
    x, y = pos
    canvas.paste(icon, (x - size // 2, y - size // 2), icon)
