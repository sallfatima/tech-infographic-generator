"""FastAPI web application for the tech infographic generator."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..analyzer.llm_analyzer import LLMAnalyzer
from ..renderer.engine import ProRenderer
from ..renderer.animator import InfographicAnimator
from ..renderer.themes import list_themes, THEMES
from ..renderer.render_preset import apply_render_preset
from ..models.infographic import InfographicData
from ..agents import InfographicPipeline, PipelineContext

app = FastAPI(title="Tech Infographic Generator", version="2.0")

# Serve static assets
WEB_DIR = Path(__file__).parent.parent / "web"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


# --- Request/Response models ---

class GenerateRequest(BaseModel):
    text: str
    infographic_type: str | None = None
    theme: str = "whiteboard"
    width: int = 1400
    height: int = 900
    format: str = "png"  # "png" or "gif"
    frame_duration: int = 500
    render_preset: str | None = None


class GenerateResponse(BaseModel):
    image_url: str
    filename: str
    infographic_data: dict
    generation_time: float
    format: str


class AnalyzeResponse(BaseModel):
    data: dict
    analysis_time: float


class ProGenerateRequest(BaseModel):
    """Request model for the multi-agent Pro pipeline."""
    text: str
    infographic_type: str | None = None
    theme: str = "guidebook"
    width: int = 1400
    height: int = 900
    format: str = "png"
    frame_duration: int = 500
    enable_research: bool = True
    enable_quality_check: bool = False
    render_preset: str | None = None


class ProGenerateResponse(BaseModel):
    """Response model for the multi-agent Pro pipeline."""
    image_url: str
    filename: str
    infographic_data: dict
    generation_time: float
    format: str
    pipeline_summary: dict


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main frontend page."""
    html_path = WEB_DIR / "index.html"
    return HTMLResponse(html_path.read_text())


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Analyze text with LLM and render an infographic."""
    start = time.time()

    try:
        # Step 1: Analyze text with LLM
        analyzer = LLMAnalyzer()
        data = await analyzer.analyze(request.text, request.infographic_type)

        # Override theme if specified
        data.color_scheme = request.theme
        data = apply_render_preset(
            data,
            request.render_preset,
            for_gif=(request.format == "gif"),
        )

        # Step 2: Render
        if request.format == "gif":
            animator = InfographicAnimator(request.theme)
            output_path = animator.generate_gif(
                data,
                width=request.width,
                height=request.height,
                frame_duration=request.frame_duration,
            )
            filename = output_path.name
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


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_only(request: GenerateRequest):
    """Analyze text and return structured JSON without rendering."""
    start = time.time()

    try:
        analyzer = LLMAnalyzer()
        data = await analyzer.analyze(request.text, request.infographic_type)
        elapsed = time.time() - start

        return AnalyzeResponse(
            data=data.model_dump(),
            analysis_time=round(elapsed, 2),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-pro", response_model=ProGenerateResponse)
async def generate_pro(request: ProGenerateRequest):
    """Generate infographic using the multi-agent Pro pipeline.

    Pipeline: Research Agent → Structure Agent → Render Agent
    - Research Agent searches for visual references (non-critical, skipped if no API key)
    - Structure Agent converts text + research into structured JSON
    - Render Agent produces the final image
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
            render_preset=request.render_preset,
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


@app.get("/api/themes")
async def get_themes():
    """Return available color themes."""
    return {
        name: {"name": t["name"], "bg": t["bg"], "accent": t["accent"], "accent2": t["accent2"]}
        for name, t in THEMES.items()
    }
