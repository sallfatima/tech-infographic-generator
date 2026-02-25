"""POST /api/generate et /api/generate-pro — Analyse + rendu en une seule requete.

/api/generate     : Mode Standard — LLM analyze + PIL render → image URL
/api/generate-pro : Mode Pro — Pipeline multi-agent (Research → Structure → Render)
"""

from __future__ import annotations

import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..analyzer.llm_analyzer import LLMAnalyzer
from ..renderer.engine import ProRenderer
from ..renderer.animator import InfographicAnimator
from ..agents import InfographicPipeline, PipelineContext

router = APIRouter()

# Dossier de sortie pour les images generees
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# --- Request / Response models ---


class GenerateRequest(BaseModel):
    """Corps de la requete /api/generate."""

    text: str
    infographic_type: str | None = None
    theme: str = "whiteboard"
    width: int = 1400
    height: int = 900
    format: str = "png"
    frame_duration: int = 500


class GenerateResponse(BaseModel):
    """Reponse /api/generate — image URL + metadata."""

    image_url: str
    filename: str
    infographic_data: dict
    generation_time: float
    format: str


class ProGenerateRequest(GenerateRequest):
    """Corps de la requete /api/generate-pro — options pipeline."""

    enable_research: bool = True
    enable_quality_check: bool = False


class ProGenerateResponse(GenerateResponse):
    """Reponse /api/generate-pro — avec resume pipeline."""

    pipeline_summary: dict


# --- Routes ---


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Mode Standard : Analyse LLM + rendu PIL en une seule etape.

    1. LLMAnalyzer.analyze(text) → InfographicData JSON
    2. ProRenderer.render(data) → PNG ou InfographicAnimator → GIF
    3. Retourne l'URL de l'image generee
    """
    start = time.time()

    try:
        # Step 1: Analyze text with LLM
        analyzer = LLMAnalyzer()
        data = await analyzer.analyze(request.text, request.infographic_type)

        # Override theme if specified
        data.color_scheme = request.theme

        # Step 2: Render
        if request.format == "gif":
            animator = InfographicAnimator(request.theme)
            output_path = animator.generate_gif(
                data,
                width=request.width,
                height=request.height,
                frame_duration=request.frame_duration,
            )
        else:
            renderer = ProRenderer(request.theme)
            output_path = renderer.render(
                data,
                width=request.width,
                height=request.height,
            )

        filename = output_path.name
        elapsed = time.time() - start

        return GenerateResponse(
            image_url=f"/output/{filename}",
            filename=filename,
            infographic_data=data.model_dump(),
            generation_time=round(elapsed, 2),
            format=request.format,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pro", response_model=ProGenerateResponse)
async def generate_pro(request: ProGenerateRequest):
    """Mode Pro : Pipeline multi-agent (Research → Structure → Render).

    1. Research Agent : recherche de references visuelles (optionnel)
    2. Structure Agent : texte + research → InfographicData JSON
    3. Render Agent : InfographicData → image PNG/GIF
    4. Retourne l'image + resume du pipeline
    """
    try:
        # Build pipeline context
        ctx = PipelineContext(
            user_text=request.text,
            theme=request.theme,
            type_hint=request.infographic_type,
            width=request.width,
            height=request.height,
            output_format=request.format,
            frame_duration=request.frame_duration,
            enable_research=request.enable_research,
        )

        # Run the multi-agent pipeline
        pipeline = InfographicPipeline(
            enable_quality_check=request.enable_quality_check,
        )
        ctx = await pipeline.run(ctx)

        # Build response
        if ctx.render_result is None:
            raise ValueError("Pipeline completed but no render result")

        return ProGenerateResponse(
            image_url=f"/output/{ctx.render_result.filename}",
            filename=ctx.render_result.filename,
            infographic_data=ctx.infographic_data.model_dump() if ctx.infographic_data else {},
            generation_time=round(ctx.total_time, 2),
            format=ctx.output_format,
            pipeline_summary=ctx.to_summary(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
