"""Structure Agent - converts text + research findings into InfographicData.

This is Agent 2 in the pipeline. It receives the user text enriched
with research findings and produces a validated InfographicData JSON
structure ready for rendering.

Uses Claude Sonnet 4 (same model as the original LLMAnalyzer).
"""

import time

from ..models.infographic import InfographicData
from .base import BaseAgent
from .context import PipelineContext, PipelineStage
from .prompts.structure_prompts import build_user_prompt, get_structure_system_prompt


class StructureAgent(BaseAgent):
    """Agent that converts text into structured InfographicData."""

    name = "structure"
    description = "Converts text + research into structured infographic JSON"

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        """Analyze user text and produce InfographicData.

        Reads:
            - ctx.user_text: Raw input text
            - ctx.type_hint: Optional preferred type
            - ctx.research_findings: Optional research context (from Agent 1)

        Writes:
            - ctx.infographic_data: Validated InfographicData
            - ctx.stage: Updated to STRUCTURING then next stage
            - ctx.timings["structure"]: Duration in seconds

        Returns:
            Updated PipelineContext.
        """
        ctx.stage = PipelineStage.STRUCTURING
        start = time.time()

        try:
            # Build the system prompt (same as original analyzer)
            system_prompt = get_structure_system_prompt()

            # Build enriched user prompt with research context
            research = ctx.research_findings
            user_prompt = build_user_prompt(
                user_text=ctx.user_text,
                type_hint=ctx.type_hint,
                topic_summary=research.topic_summary if research else "",
                topic_keywords=research.topic_keywords if research else None,
                suggested_type=research.suggested_type if research else "",
                layout_style=research.style_guidance.layout_style if research else "",
                visual_density=research.style_guidance.visual_density if research else "",
                style_notes=research.style_guidance.notes if research else "",
            )

            # Call LLM (Claude Sonnet 4 by default)
            raw_json = await self.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
            )

            # Parse and validate response
            data_dict = self.parse_json_response(raw_json)
            ctx.infographic_data = InfographicData.model_validate(data_dict)

        except Exception as e:
            ctx.add_error(f"Structure Agent failed: {str(e)}")
            ctx.stage = PipelineStage.FAILED
            raise

        finally:
            duration = time.time() - start
            ctx.record_timing("structure", duration)

        return ctx

    async def run_with_feedback(
        self, ctx: PipelineContext, feedback: str
    ) -> PipelineContext:
        """Re-run the agent with quality feedback for improvement.

        Called by the Orchestrator when the Render Agent's quality check
        suggests improvements.

        Args:
            ctx: Pipeline context with previous infographic_data.
            feedback: Quality check feedback/suggestions.

        Returns:
            Updated PipelineContext with improved infographic_data.
        """
        ctx.stage = PipelineStage.STRUCTURING
        start = time.time()

        try:
            system_prompt = get_structure_system_prompt()

            # Build prompt with feedback
            research = ctx.research_findings
            base_prompt = build_user_prompt(
                user_text=ctx.user_text,
                type_hint=ctx.type_hint,
                topic_summary=research.topic_summary if research else "",
                topic_keywords=research.topic_keywords if research else None,
                suggested_type=research.suggested_type if research else "",
                layout_style=research.style_guidance.layout_style if research else "",
                visual_density=research.style_guidance.visual_density if research else "",
                style_notes=research.style_guidance.notes if research else "",
            )

            user_prompt = (
                f"{base_prompt}\n\n"
                f"[Quality Improvement Feedback]\n"
                f"The previous version had issues. Please improve based on this feedback:\n"
                f"{feedback}"
            )

            raw_json = await self.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
            )

            data_dict = self.parse_json_response(raw_json)
            ctx.infographic_data = InfographicData.model_validate(data_dict)

        except Exception as e:
            ctx.add_error(f"Structure Agent retry failed: {str(e)}")
            ctx.stage = PipelineStage.FAILED
            raise

        finally:
            duration = time.time() - start
            ctx.record_timing("structure_retry", duration)

        return ctx
