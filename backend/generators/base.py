"""Base class for all image generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass


@dataclass
class GenerationResult:
    image_path: Path
    prompt_used: str
    backend: str
    width: int
    height: int


class ImageGenerator(ABC):
    """Abstract base class for image generation backends."""

    @abstractmethod
    def generate(
        self,
        description: str,
        style: str = "infographic",
        width: int = 1200,
        height: int = 800,
        output_path: str | None = None,
    ) -> GenerationResult:
        """Generate an image from a text description.

        Args:
            description: Text description of what to generate.
            style: Visual style (infographic, diagram, flowchart, tech).
            width: Image width in pixels.
            height: Image height in pixels.
            output_path: Where to save the image.

        Returns:
            GenerationResult with the path and metadata.
        """
        ...

    def _build_prompt(self, description: str, style: str) -> str:
        """Enhance the user description with style-specific prompt engineering."""
        style_prompts = {
            "infographic": (
                "Clean, modern infographic style with flat design icons, "
                "structured layout, soft gradients, professional color palette, "
                "clear typography hierarchy, tech-inspired aesthetic similar to "
                "modern tech visual style. "
            ),
            "diagram": (
                "Technical system architecture diagram, clean boxes and arrows, "
                "color-coded components, professional engineering diagram style, "
                "white background, clear labels. "
            ),
            "flowchart": (
                "Professional flowchart with rounded rectangles, diamond decision "
                "nodes, directional arrows, pastel color coding, clean layout. "
            ),
            "tech": (
                "Modern tech illustration, isometric style, vibrant gradients, "
                "code snippets, API endpoints, cloud services icons, developer "
                "documentation style. "
            ),
            "minimal": (
                "Minimalist design, lots of white space, single accent color, "
                "simple geometric shapes, elegant typography. "
            ),
        }
        style_prefix = style_prompts.get(style, style_prompts["infographic"])
        return f"{style_prefix}{description}"
