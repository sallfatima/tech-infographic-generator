"""Research Agent - searches for visual references and style guidance.

This is Agent 1 in the pipeline. It extracts keywords from user text,
searches Google Images for reference infographics, and analyzes the
results to produce style recommendations.

Uses Claude Haiku for lightweight LLM calls (keyword extraction + style analysis).
Uses Serper.dev for Google Image search.

This agent is NON-CRITICAL: if it fails, the pipeline continues with defaults.
"""

import time

from .base import BaseAgent
from .context import (
    ColorPalette,
    ImageReference,
    PipelineContext,
    PipelineStage,
    ResearchFindings,
    StyleGuidance,
)
from .prompts.research_prompts import KEYWORD_EXTRACTION_PROMPT, STYLE_ANALYSIS_PROMPT
from .search.serper_client import SerperClient


# Claude Haiku model for fast/cheap LLM calls
HAIKU_MODEL = "claude-haiku-4-5-20251001"


class ResearchAgent(BaseAgent):
    """Agent that researches visual references for infographic design."""

    name = "research"
    description = "Searches web for visual references and style guidance"

    def __init__(self, provider: str | None = None, serper_api_key: str | None = None):
        super().__init__(provider)
        self.serper = SerperClient(api_key=serper_api_key)

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        """Research visual references and style guidance.

        Steps:
        1. Extract keywords + suggested type from user text (LLM Haiku)
        2. Search Google Images for reference infographics (Serper.dev)
        3. Analyze search results for style guidance (LLM Haiku)

        Reads:
            - ctx.user_text: Raw input text
            - ctx.enable_research: Whether research is enabled

        Writes:
            - ctx.research_findings: ResearchFindings
            - ctx.stage: Updated to RESEARCHING
            - ctx.timings["research"]: Duration in seconds

        Returns:
            Updated PipelineContext (always succeeds - graceful degradation).
        """
        ctx.stage = PipelineStage.RESEARCHING
        start = time.time()

        # If research is disabled, return minimal findings
        if not ctx.enable_research:
            ctx.research_findings = self._default_findings(ctx.user_text)
            ctx.add_warning("Research skipped (disabled)")
            ctx.record_timing("research", time.time() - start)
            return ctx

        try:
            # Step 1: Extract keywords using Haiku
            keywords_data = await self._extract_keywords(ctx.user_text)

            topic_summary = keywords_data.get("topic_summary", "")
            keywords = keywords_data.get("keywords", [])
            suggested_type = keywords_data.get("suggested_type", "")
            search_queries = keywords_data.get("search_queries", [])

            # Step 2: Search images (if Serper is configured)
            reference_images = []
            raw_search_results = []

            if self.serper.is_configured and search_queries:
                search_responses = await self.serper.multi_search(
                    queries=search_queries[:3],  # Max 3 queries
                    num_results_per_query=3,
                )

                for resp in search_responses:
                    if resp.error:
                        ctx.add_warning(f"Search error: {resp.error}")
                        continue

                    raw_search_results.append(resp.raw_response)

                    for img in resp.images:
                        reference_images.append(ImageReference(
                            url=img.image_url,
                            title=img.title,
                            source=img.source,
                            width=img.width,
                            height=img.height,
                        ))
            else:
                if not self.serper.is_configured:
                    ctx.add_warning("SERPER_API_KEY not set - skipping image search")

            # Step 3: Analyze style from search results (if we have results)
            if reference_images:
                style_guidance = await self._analyze_style(
                    topic_summary, reference_images, keywords
                )
            else:
                style_guidance = StyleGuidance()  # defaults

            # Assemble findings
            ctx.research_findings = ResearchFindings(
                topic_summary=topic_summary,
                topic_keywords=keywords,
                reference_images=reference_images[:10],  # cap at 10
                style_guidance=style_guidance,
                suggested_type=suggested_type,
                raw_search_results=raw_search_results,
            )

        except Exception as e:
            # Research is non-critical - log warning and continue with defaults
            ctx.add_warning(f"Research Agent failed: {str(e)}")
            ctx.research_findings = self._default_findings(ctx.user_text)

        finally:
            ctx.record_timing("research", time.time() - start)

        return ctx

    async def _extract_keywords(self, user_text: str) -> dict:
        """Extract keywords and suggested type using Claude Haiku.

        Args:
            user_text: Raw user input text.

        Returns:
            Dict with topic_summary, keywords, suggested_type, search_queries.
        """
        user_prompt = f"Analyze this text and extract infographic keywords:\n\n{user_text}"

        return await self.call_llm_json(
            system_prompt=KEYWORD_EXTRACTION_PROMPT,
            user_prompt=user_prompt,
            model=HAIKU_MODEL,
            max_tokens=512,
        )

    async def _analyze_style(
        self,
        topic_summary: str,
        reference_images: list[ImageReference],
        keywords: list[str],
    ) -> StyleGuidance:
        """Analyze search results and produce style guidance using Claude Haiku.

        Args:
            topic_summary: What the infographic is about.
            reference_images: Found reference images.
            keywords: Topic keywords.

        Returns:
            StyleGuidance with color, layout, and density recommendations.
        """
        # Build a summary of what we found (don't send raw images to Haiku)
        images_summary = "\n".join(
            f"- \"{img.title}\" from {img.source} ({img.width}x{img.height})"
            for img in reference_images[:8]
        )

        user_prompt = (
            f"Topic: {topic_summary}\n"
            f"Keywords: {', '.join(keywords)}\n\n"
            f"Reference images found:\n{images_summary}\n\n"
            f"Based on these references, recommend a visual style."
        )

        try:
            result = await self.call_llm_json(
                system_prompt=STYLE_ANALYSIS_PROMPT,
                user_prompt=user_prompt,
                model=HAIKU_MODEL,
                max_tokens=512,
            )

            # Parse color palette
            palette_data = result.get("color_palette", {})
            palette = ColorPalette(
                primary=palette_data.get("primary", "#2563EB"),
                secondary=palette_data.get("secondary", "#1E40AF"),
                accent=palette_data.get("accent", "#F59E0B"),
                background=palette_data.get("background", "#FFFFFF"),
                text=palette_data.get("text", "#1F2937"),
            )

            return StyleGuidance(
                color_palette=palette,
                layout_style=result.get("layout_style", "layered"),
                visual_density=result.get("visual_density", "moderate"),
                suggested_theme=result.get("suggested_theme", "guidebook"),
                icon_style=result.get("icon_style", "technical"),
                notes=result.get("notes", ""),
            )

        except Exception:
            # Non-critical - return defaults
            return StyleGuidance()

    @staticmethod
    def _default_findings(user_text: str) -> ResearchFindings:
        """Create minimal default findings when research fails or is skipped.

        Args:
            user_text: Original text (used for basic topic extraction).

        Returns:
            ResearchFindings with sensible defaults.
        """
        # Basic topic extraction from first line
        first_line = user_text.strip().split("\n")[0][:100]

        return ResearchFindings(
            topic_summary=first_line,
            topic_keywords=[],
            reference_images=[],
            style_guidance=StyleGuidance(),
            suggested_type="",
        )
