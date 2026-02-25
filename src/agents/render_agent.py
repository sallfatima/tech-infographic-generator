"""Render Agent - renders InfographicData into a final image.

This is Agent 3 in the pipeline. It takes the validated InfographicData,
selects the optimal theme, renders the image via ProRenderer, and
optionally runs a quality check.

Mostly programmatic (delegates to existing ProRenderer/InfographicAnimator),
with optional LLM quality check using Claude Haiku.
"""

import time
from pathlib import Path

from ..models.infographic import InfographicData
from ..renderer.engine import ProRenderer
from ..renderer.animator import InfographicAnimator
from .base import BaseAgent
from .context import (
    PipelineContext,
    PipelineStage,
    QualityReport,
    RenderResult,
)
from .prompts.render_prompts import QUALITY_CHECK_PROMPT, select_theme


class RenderAgent(BaseAgent):
    """Agent that renders InfographicData into PNG/GIF images."""

    name = "render"
    description = "Renders structured data into final infographic image"

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        """Render the infographic.

        Reads:
            - ctx.infographic_data: Validated InfographicData (from Agent 2)
            - ctx.theme: User's theme preference
            - ctx.width, ctx.height: Output dimensions
            - ctx.output_format: "png" or "gif"
            - ctx.research_findings: Optional style guidance

        Writes:
            - ctx.render_result: RenderResult with file path and quality report
            - ctx.stage: Updated to RENDERING then next stage
            - ctx.timings["render"]: Duration in seconds

        Returns:
            Updated PipelineContext.
        """
        ctx.stage = PipelineStage.RENDERING
        start = time.time()

        if ctx.infographic_data is None:
            ctx.add_error("Render Agent: No infographic data to render")
            ctx.stage = PipelineStage.FAILED
            raise ValueError("No infographic data available for rendering")

        try:
            # 1. Select optimal theme
            research = ctx.research_findings
            theme_name = select_theme(
                user_theme=ctx.theme,
                visual_density=research.style_guidance.visual_density if research else "moderate",
                icon_style=research.style_guidance.icon_style if research else "technical",
                suggested_theme=research.style_guidance.suggested_theme if research else "",
            )

            # 2. Render image
            if ctx.output_format == "gif":
                file_path, filename = self._render_gif(
                    ctx.infographic_data, theme_name,
                    ctx.width, ctx.height, ctx.frame_duration,
                )
            else:
                file_path, filename = self._render_png(
                    ctx.infographic_data, theme_name,
                    ctx.width, ctx.height,
                )

            # 3. Build result
            duration = time.time() - start
            ctx.render_result = RenderResult(
                file_path=str(file_path),
                filename=filename,
                format=ctx.output_format,
                theme_used=theme_name,
                render_time=duration,
            )

        except Exception as e:
            ctx.add_error(f"Render Agent failed: {str(e)}")
            ctx.stage = PipelineStage.FAILED
            raise

        finally:
            duration = time.time() - start
            ctx.record_timing("render", duration)

        return ctx

    def _render_png(
        self,
        data: InfographicData,
        theme_name: str,
        width: int,
        height: int,
    ) -> tuple[Path, str]:
        """Render as PNG.

        Returns:
            Tuple of (file_path, filename).
        """
        renderer = ProRenderer(theme_name)
        output_path = renderer.render(data, width=width, height=height)
        return output_path, output_path.name

    def _render_gif(
        self,
        data: InfographicData,
        theme_name: str,
        width: int,
        height: int,
        frame_duration: int,
    ) -> tuple[Path, str]:
        """Render as animated GIF.

        Returns:
            Tuple of (file_path, filename).
        """
        animator = InfographicAnimator(theme_name)
        output_path = animator.generate_gif(
            data,
            width=width,
            height=height,
            frame_duration=frame_duration,
        )
        return output_path, output_path.name

    async def quality_check(self, ctx: PipelineContext) -> QualityReport:
        """Optional quality check using Claude Haiku.

        Evaluates the infographic structure for quality and suggests
        improvements. This is a lightweight check, not a full re-generation.

        Args:
            ctx: Pipeline context with infographic_data.

        Returns:
            QualityReport with score, issues, and suggestions.
        """
        if ctx.infographic_data is None:
            return QualityReport(score=0.0, passed=False, issues=["No data to check"])

        try:
            import json

            data_summary = json.dumps(ctx.infographic_data.model_dump(), indent=2)
            user_prompt = (
                f"Original text:\n{ctx.user_text}\n\n"
                f"Generated infographic structure:\n{data_summary}"
            )

            raw = await self.call_llm(
                system_prompt=QUALITY_CHECK_PROMPT,
                user_prompt=user_prompt,
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
            )

            result = self.parse_json_response(raw)
            return QualityReport(
                score=float(result.get("score", 0.7)),
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", []),
                passed=result.get("passed", True),
            )

        except Exception as e:
            # Quality check is non-critical - don't fail the pipeline
            ctx.add_warning(f"Quality check failed: {str(e)}")
            return QualityReport(score=0.7, passed=True, issues=[], suggestions=[])
