"""Orchestrator - coordinates the multi-agent pipeline.

The InfographicPipeline runs 3 agents sequentially:
1. Research Agent -> visual references + style guidance
2. Structure Agent -> InfographicData JSON
3. Render Agent -> final PNG/GIF image

Features:
- Graceful degradation (Research Agent failure doesn't block pipeline)
- Optional quality check with retry loop
- Timing and error tracking via PipelineContext
"""

import time

from .context import PipelineContext, PipelineStage
from .research_agent import ResearchAgent
from .structure_agent import StructureAgent
from .render_agent import RenderAgent


class InfographicPipeline:
    """Orchestrates the multi-agent infographic generation pipeline.

    Usage:
        pipeline = InfographicPipeline()
        ctx = PipelineContext(user_text="How RAG works...", theme="guidebook")
        ctx = await pipeline.run(ctx)

        # Access results
        print(ctx.render_result.file_path)
        print(ctx.to_summary())
    """

    def __init__(
        self,
        provider: str | None = None,
        enable_quality_check: bool = False,
    ):
        """Initialize the pipeline with all 3 agents.

        Args:
            provider: LLM provider ("anthropic" or "openai"). Auto-detected if None.
            enable_quality_check: Whether to run quality check after rendering.
        """
        self.research_agent = ResearchAgent(provider=provider)
        self.structure_agent = StructureAgent(provider=provider)
        self.render_agent = RenderAgent(provider=provider)
        self.enable_quality_check = enable_quality_check

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        """Execute the full pipeline.

        Runs the 3 agents sequentially, with graceful degradation
        for the Research Agent and optional retry for quality issues.

        Args:
            ctx: Pipeline context with user input.

        Returns:
            Updated PipelineContext with all results.

        Raises:
            Exception: If Structure Agent or Render Agent fails.
        """
        pipeline_start = time.time()

        try:
            # ---- Agent 1: Research (non-critical) ----
            ctx = await self._run_research(ctx)

            # ---- Agent 2: Structure (critical) ----
            ctx = await self._run_structure(ctx)

            # ---- Agent 3: Render (critical) ----
            ctx = await self._run_render(ctx)

            # ---- Optional: Quality check + retry ----
            if self.enable_quality_check and ctx.retry_count < ctx.max_retries:
                ctx = await self._quality_check_and_retry(ctx)

            # Mark as completed
            ctx.stage = PipelineStage.COMPLETED

        except Exception as e:
            ctx.stage = PipelineStage.FAILED
            if str(e) not in " | ".join(ctx.errors):
                ctx.add_error(f"Pipeline failed: {str(e)}")
            raise

        finally:
            total = time.time() - pipeline_start
            ctx.record_timing("total_pipeline", total)

        return ctx

    async def _run_research(self, ctx: PipelineContext) -> PipelineContext:
        """Run the Research Agent with graceful degradation.

        If research fails, the pipeline continues with default findings.
        """
        try:
            ctx = await self.research_agent.run(ctx)
        except Exception as e:
            # Research is non-critical
            ctx.add_warning(f"Research skipped due to error: {str(e)}")
            ctx.research_findings = ResearchAgent._default_findings(ctx.user_text)
        return ctx

    async def _run_structure(self, ctx: PipelineContext) -> PipelineContext:
        """Run the Structure Agent (critical).

        Raises:
            Exception: If structure generation fails.
        """
        ctx = await self.structure_agent.run(ctx)
        return ctx

    async def _run_render(self, ctx: PipelineContext) -> PipelineContext:
        """Run the Render Agent (critical).

        Raises:
            Exception: If rendering fails.
        """
        ctx = await self.render_agent.run(ctx)
        return ctx

    async def _quality_check_and_retry(self, ctx: PipelineContext) -> PipelineContext:
        """Run quality check and retry structure if quality is low.

        If the quality check fails (score < 0.7), re-runs the Structure
        Agent with improvement feedback, then re-renders.
        """
        report = await self.render_agent.quality_check(ctx)

        if report.passed:
            # Quality is good
            if ctx.render_result:
                ctx.render_result.quality_report = report
            return ctx

        # Quality check failed - retry with feedback
        ctx.retry_count += 1
        feedback = "\n".join(
            [f"Issues: {', '.join(report.issues)}"]
            + [f"Suggestions: {', '.join(report.suggestions)}"]
        )

        ctx.add_warning(f"Quality check failed (score={report.score:.2f}), retrying...")

        # Re-run Structure Agent with feedback
        ctx = await self.structure_agent.run_with_feedback(ctx, feedback)

        # Re-render
        ctx = await self._run_render(ctx)

        # Store quality report
        if ctx.render_result:
            ctx.render_result.quality_report = report

        return ctx
