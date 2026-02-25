"""Stable Diffusion image generation backend using HuggingFace diffusers."""

from __future__ import annotations

import os
import time
from pathlib import Path

from .base import ImageGenerator, GenerationResult


class StableDiffusionGenerator(ImageGenerator):
    """Generate images using Stable Diffusion (local or HF Inference)."""

    def __init__(
        self,
        model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
        device: str = "auto",
        hf_token: str | None = None,
    ):
        self.model_id = model_id
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self._pipe = None

        if device == "auto":
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device

    def _load_pipeline(self):
        if self._pipe is not None:
            return self._pipe

        from diffusers import StableDiffusionXLPipeline
        import torch

        self._pipe = StableDiffusionXLPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            use_auth_token=self.hf_token,
        )
        self._pipe = self._pipe.to(self.device)

        if self.device == "cuda":
            self._pipe.enable_model_cpu_offload()

        return self._pipe

    def generate(
        self,
        description: str,
        style: str = "infographic",
        width: int = 1024,
        height: int = 1024,
        output_path: str | None = None,
    ) -> GenerationResult:
        prompt = self._build_prompt(description, style)
        negative_prompt = (
            "blurry, low quality, distorted text, watermark, "
            "ugly, deformed, noisy, overexposed"
        )

        pipe = self._load_pipeline()

        # Round to multiples of 8
        width = (width // 8) * 8
        height = (height // 8) * 8

        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=30,
            guidance_scale=7.5,
        ).images[0]

        if output_path is None:
            output_path = f"output/sd_{int(time.time())}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)

        return GenerationResult(
            image_path=Path(output_path),
            prompt_used=prompt,
            backend="stable-diffusion-xl",
            width=width,
            height=height,
        )
