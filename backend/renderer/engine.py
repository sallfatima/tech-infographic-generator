"""Main rendering engine - dispatches to type-specific renderers."""

from __future__ import annotations

import time
from pathlib import Path

from PIL import Image, ImageChops

from ..models.infographic import InfographicData, InfographicType
from .themes import get_theme, hex_to_rgb

from .renderers.architecture import render_architecture
from .renderers.flowchart import render_flowchart
from .renderers.comparison import render_comparison
from .renderers.process import render_process
from .renderers.pipeline import render_pipeline
from .renderers.concept_map import render_concept_map
from .renderers.infographic import render_infographic
from .renderers.multi_agent import render_multi_agent
from .renderers.rag_pipeline import render_rag_pipeline


RENDERERS = {
    InfographicType.ARCHITECTURE: render_architecture,
    InfographicType.FLOWCHART: render_flowchart,
    InfographicType.COMPARISON: render_comparison,
    InfographicType.PROCESS: render_process,
    InfographicType.PIPELINE: render_pipeline,
    InfographicType.CONCEPT_MAP: render_concept_map,
    InfographicType.INFOGRAPHIC: render_infographic,
    InfographicType.TIMELINE: render_process,  # Reuse process renderer for now
    InfographicType.MULTI_AGENT: render_multi_agent,
    InfographicType.RAG_PIPELINE: render_rag_pipeline,
}


def _auto_crop(img: Image.Image, bg_color: tuple[int, int, int], margin: int = 20) -> Image.Image:
    """Crop empty space from the bottom and right edges of the image.

    Scans from the bottom-right inward to find where actual content ends,
    then crops to that boundary + a small margin.
    Preserves the top-left area (title, header) untouched.
    Only crops if at least 15% of the image would be removed.
    """
    width, height = img.size

    # Create a background image of the same size filled with bg_color
    bg = Image.new(img.mode, img.size, bg_color)

    # Find the difference
    diff = ImageChops.difference(img, bg)
    # Convert to grayscale for simpler thresholding
    diff_gray = diff.convert("L")

    # Get bounding box of non-background content (threshold=5 for anti-aliasing)
    # point() maps pixel values: 0 if < threshold, 255 otherwise
    threshold = 5
    diff_binary = diff_gray.point(lambda p: 255 if p > threshold else 0)
    content_bbox = diff_binary.getbbox()

    if content_bbox is None:
        # Entirely blank — return as-is
        return img

    _, _, content_right, content_bottom = content_bbox

    # Only crop if we'd save at least 15% of pixels
    new_w = min(width, content_right + margin)
    new_h = min(height, content_bottom + margin)

    saved_area = (width * height) - (new_w * new_h)
    total_area = width * height
    if saved_area < total_area * 0.15:
        # Not enough savings — return as-is to avoid tiny crops
        return img

    # Crop (keep top-left, trim bottom-right)
    return img.crop((0, 0, new_w, new_h))


class ProRenderer:
    """Professional infographic renderer.

    Takes structured InfographicData and produces high-quality PNG or GIF.
    """

    def __init__(self, theme_name: str = "whiteboard"):
        self.theme = get_theme(theme_name)
        self.theme_name = theme_name

    def render(
        self,
        data: InfographicData,
        width: int = 1400,
        height: int = 900,
        output_path: str | None = None,
    ) -> Path:
        """Render an infographic to PNG.

        Args:
            data: Structured infographic data from the LLM analyzer.
            width: Output width in pixels.
            height: Output height in pixels.
            output_path: Where to save. Auto-generated if None.

        Returns:
            Path to the saved PNG file.
        """
        renderer_fn = RENDERERS.get(data.type, render_infographic)
        img = renderer_fn(data, width, height, self.theme)

        # Auto-crop empty space from bottom/right
        bg_color = hex_to_rgb(self.theme.get("bg", "#FFFFFF"))
        img = _auto_crop(img, bg_color, margin=25)

        if output_path is None:
            Path("output").mkdir(exist_ok=True)
            output_path = f"output/pro_{int(time.time())}.png"

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(path), "PNG", quality=95)
        return path

    def render_to_image(
        self,
        data: InfographicData,
        width: int = 1400,
        height: int = 900,
    ) -> Image.Image:
        """Render and return the PIL Image (no file save)."""
        renderer_fn = RENDERERS.get(data.type, render_infographic)
        img = renderer_fn(data, width, height, self.theme)

        # Auto-crop empty space from bottom/right
        bg_color = hex_to_rgb(self.theme.get("bg", "#FFFFFF"))
        img = _auto_crop(img, bg_color, margin=25)

        return img
