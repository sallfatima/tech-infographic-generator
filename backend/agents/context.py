"""Shared pipeline context and data models for the multi-agent system.

The PipelineContext is the shared state object passed between all agents.
Each agent reads from it and writes its output back to it.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ..models.infographic import InfographicData


class PipelineStage(str, Enum):
    """Current stage of the multi-agent pipeline."""

    INITIALIZED = "initialized"
    RESEARCHING = "researching"
    STRUCTURING = "structuring"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ColorPalette:
    """Suggested color palette from visual research."""

    primary: str = "#2563EB"    # Blue
    secondary: str = "#1E40AF"  # Darker blue
    accent: str = "#F59E0B"     # Amber
    background: str = "#FFFFFF"
    text: str = "#1F2937"


@dataclass
class ImageReference:
    """A reference image found during research."""

    url: str
    title: str
    source: str = ""
    width: int = 0
    height: int = 0


@dataclass
class StyleGuidance:
    """Visual style recommendations from the Research Agent."""

    color_palette: ColorPalette = field(default_factory=ColorPalette)
    layout_style: str = "layered"       # layered, horizontal, radial, grid
    visual_density: str = "moderate"    # minimal, moderate, detailed
    suggested_theme: str = "guidebook"  # maps to an existing theme name
    icon_style: str = "technical"       # technical, playful, minimal
    notes: str = ""                     # free-form style notes


@dataclass
class ResearchFindings:
    """Output of the Research Agent."""

    topic_summary: str = ""
    topic_keywords: list[str] = field(default_factory=list)
    reference_images: list[ImageReference] = field(default_factory=list)
    style_guidance: StyleGuidance = field(default_factory=StyleGuidance)
    suggested_type: str = ""            # e.g. "architecture", "flowchart"
    raw_search_results: list[dict] = field(default_factory=list)


@dataclass
class QualityReport:
    """Quality assessment from the Render Agent's optional check."""

    score: float = 0.0          # 0.0 - 1.0
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    passed: bool = True


@dataclass
class RenderResult:
    """Output of the Render Agent."""

    file_path: str = ""
    filename: str = ""
    format: str = "png"
    theme_used: str = "guidebook"
    quality_report: Optional[QualityReport] = None
    render_time: float = 0.0


@dataclass
class PipelineContext:
    """Shared state object for the multi-agent pipeline.

    Created at the start of a generation request, passed through
    each agent sequentially. Each agent reads its inputs and writes
    its outputs here.
    """

    # --- Input (set at creation) ---
    user_text: str = ""
    theme: str = "guidebook"
    type_hint: Optional[str] = None
    width: int = 1400
    height: int = 900
    output_format: str = "png"
    frame_duration: int = 600       # for GIF format
    enable_research: bool = True    # can disable research agent

    # --- Pipeline state ---
    stage: PipelineStage = PipelineStage.INITIALIZED
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 1

    # --- Agent outputs ---
    research_findings: Optional[ResearchFindings] = None   # Agent 1 output
    infographic_data: Optional[InfographicData] = None     # Agent 2 output
    render_result: Optional[RenderResult] = None           # Agent 3 output

    def add_error(self, error: str) -> None:
        """Record an error."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Record a non-fatal warning."""
        self.warnings.append(warning)

    def record_timing(self, step: str, duration: float) -> None:
        """Record how long a step took."""
        self.timings[step] = duration

    @property
    def total_time(self) -> float:
        """Total pipeline execution time."""
        return sum(self.timings.values())

    @property
    def is_failed(self) -> bool:
        """Check if the pipeline is in a failed state."""
        return self.stage == PipelineStage.FAILED

    def to_summary(self) -> dict:
        """Generate a summary dict for the API response."""
        steps = []
        for step_name in ["research", "structure", "render"]:
            if step_name in self.timings:
                steps.append({
                    "name": step_name,
                    "duration": round(self.timings[step_name], 2),
                    "status": "completed",
                })
            elif self.stage == PipelineStage.FAILED:
                steps.append({
                    "name": step_name,
                    "duration": 0,
                    "status": "failed" if step_name not in self.timings else "completed",
                })

        summary = {
            "pipeline_steps": steps,
            "total_time": round(self.total_time, 2),
            "errors": self.errors,
            "warnings": self.warnings,
        }

        if self.research_findings:
            summary["research_summary"] = {
                "topic": self.research_findings.topic_summary,
                "keywords": self.research_findings.topic_keywords,
                "references_found": len(self.research_findings.reference_images),
                "suggested_type": self.research_findings.suggested_type,
            }

        return summary
