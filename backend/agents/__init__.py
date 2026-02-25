"""Multi-agent pipeline for professional infographic generation.

This package contains 3 specialized agents that collaborate sequentially:
1. Research Agent - searches for visual references and style guidance
2. Structure Agent - converts text + research into structured InfographicData
3. Render Agent - renders the final image with optimal theme selection

Usage:
    from backend.agents import InfographicPipeline, PipelineContext

    ctx = PipelineContext(user_text="How RAG works...", theme="guidebook")
    pipeline = InfographicPipeline()
    result = await pipeline.run(ctx)
"""

from .context import (
    ColorPalette,
    ImageReference,
    PipelineContext,
    PipelineStage,
    QualityReport,
    RenderResult,
    ResearchFindings,
    StyleGuidance,
)
from .orchestrator import InfographicPipeline
from .research_agent import ResearchAgent
from .structure_agent import StructureAgent
from .render_agent import RenderAgent

__all__ = [
    # Pipeline
    "InfographicPipeline",
    # Agents
    "ResearchAgent",
    "StructureAgent",
    "RenderAgent",
    # Context & data models
    "PipelineContext",
    "PipelineStage",
    "ResearchFindings",
    "StyleGuidance",
    "ColorPalette",
    "ImageReference",
    "QualityReport",
    "RenderResult",
]
