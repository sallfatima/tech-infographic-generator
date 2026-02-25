"""Prompts for the Structure Agent.

The Structure Agent converts user text + research findings into
structured InfographicData JSON. Its system prompt is based on
the original analyzer/prompts.py with research context injection.
"""

from ...models.infographic import InfographicData

# Same core prompt as analyzer/prompts.py — the full system prompt with
# JSON schema, icon guidelines, 9 infographic types, and 5 examples.
# We import and reuse it to avoid duplication.
from ...analyzer.prompts import ANALYZER_SYSTEM_PROMPT


def get_structure_system_prompt() -> str:
    """Build the Structure Agent's system prompt with JSON schema."""
    import json

    schema = InfographicData.model_json_schema()
    schema_str = json.dumps(schema, indent=2)
    return ANALYZER_SYSTEM_PROMPT.format(schema=schema_str)


def build_user_prompt(
    user_text: str,
    type_hint: str | None = None,
    topic_summary: str = "",
    topic_keywords: list[str] | None = None,
    suggested_type: str = "",
    layout_style: str = "",
    visual_density: str = "",
    style_notes: str = "",
) -> str:
    """Build the enriched user prompt with optional research context.

    Args:
        user_text: Original user text.
        type_hint: Explicit type preference from user.
        topic_summary: Research Agent's topic summary.
        topic_keywords: Research Agent's extracted keywords.
        suggested_type: Research Agent's suggested infographic type.
        layout_style: Research Agent's layout suggestion.
        visual_density: Research Agent's visual density suggestion.
        style_notes: Research Agent's free-form style notes.

    Returns:
        Complete user prompt for the Structure Agent.
    """
    prompt = user_text.strip()

    # Add research context if available
    research_parts = []

    if topic_summary:
        research_parts.append(f"Topic: {topic_summary}")
    if topic_keywords:
        research_parts.append(f"Key concepts: {', '.join(topic_keywords)}")
    if suggested_type:
        research_parts.append(f"Suggested infographic type: {suggested_type}")
    if layout_style:
        research_parts.append(f"Suggested layout: {layout_style}")
    if visual_density:
        research_parts.append(f"Visual density: {visual_density}")
    if style_notes:
        research_parts.append(f"Style notes: {style_notes}")

    if research_parts:
        prompt += "\n\n[Visual Research Context]\n"
        prompt += "\n".join(f"- {part}" for part in research_parts)

    # Add explicit type hint if user specified one
    if type_hint:
        prompt += f"\n\n[Preferred infographic type: {type_hint}]"

    return prompt
