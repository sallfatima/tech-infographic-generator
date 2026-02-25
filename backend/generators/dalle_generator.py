"""DALL-E image generation backend using OpenAI API."""

from __future__ import annotations

import os
import time
from pathlib import Path

from openai import OpenAI

from .base import ImageGenerator, GenerationResult


class DalleGenerator(ImageGenerator):
    """Generate images using OpenAI's DALL-E 3."""

    def __init__(self, api_key: str | None = None, model: str = "dall-e-3"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate(
        self,
        description: str,
        style: str = "infographic",
        width: int = 1024,
        height: int = 1024,
        output_path: str | None = None,
    ) -> GenerationResult:
        prompt = self._build_prompt(description, style)

        # DALL-E 3 supports: 1024x1024, 1792x1024, 1024x1792
        size = self._pick_dalle_size(width, height)

        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            n=1,
            size=size,
            quality="hd",
            style="natural",
        )

        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt

        # Download the image
        import urllib.request

        if output_path is None:
            output_path = f"output/dalle_{int(time.time())}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(image_url, output_path)

        w, h = map(int, size.split("x"))
        return GenerationResult(
            image_path=Path(output_path),
            prompt_used=revised_prompt or prompt,
            backend="dall-e-3",
            width=w,
            height=h,
        )

    @staticmethod
    def _pick_dalle_size(width: int, height: int) -> str:
        if width > height * 1.3:
            return "1792x1024"
        elif height > width * 1.3:
            return "1024x1792"
        return "1024x1024"
