"""Main rendering engine - dispatches to type-specific renderers."""

import time
from pathlib import Path

from PIL import Image

from ..models.infographic import InfographicData, InfographicType
from .themes import get_theme

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
        return renderer_fn(data, width, height, self.theme)
