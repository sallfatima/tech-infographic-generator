"""Prompts for the Render Agent's optional quality check."""

QUALITY_CHECK_PROMPT = """You are a visual infographic quality reviewer.
Given the structured data for an infographic, evaluate its quality and suggest improvements.

Rate the following criteria from 0.0 to 1.0:
1. **Clarity**: Are labels clear and concise? Are descriptions helpful?
2. **Structure**: Is the type appropriate? Are nodes well-organized?
3. **Completeness**: Does it cover the key concepts from the original text?
4. **Connections**: Do the connections make logical sense? Is the flow clear?

Return ONLY valid JSON:
{{
    "score": 0.85,
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1"],
    "passed": true
}}

Rules:
- "passed" is true if score >= 0.7
- Keep issues and suggestions concise (max 100 chars each)
- Maximum 3 issues and 3 suggestions
- Be constructive, not overly critical
"""


# Map visual density + research guidance to theme selection
THEME_MAPPING = {
    # (visual_density, general_style) -> theme_name
    ("minimal", "clean"): "whiteboard",
    ("minimal", "technical"): "whiteboard",
    ("moderate", "clean"): "guidebook",
    ("moderate", "technical"): "guidebook",
    ("moderate", "dark"): "dark_modern",
    ("detailed", "clean"): "guidebook",
    ("detailed", "technical"): "guidebook",
    ("detailed", "dark"): "dark_modern",
}

DEFAULT_THEME = "guidebook"


def select_theme(
    user_theme: str,
    visual_density: str = "moderate",
    icon_style: str = "technical",
    suggested_theme: str = "",
) -> str:
    """Select the best rendering theme based on research and user preference.

    Priority:
    1. User explicitly chose a theme -> use it
    2. Research Agent suggested a theme -> use it if valid
    3. Default mapping based on visual density/style

    Args:
        user_theme: Theme selected by the user.
        visual_density: Research Agent's visual density suggestion.
        icon_style: Research Agent's icon style suggestion.
        suggested_theme: Research Agent's suggested theme name.

    Returns:
        Theme name to use for rendering.
    """
    from ...renderer.themes import THEMES

    # 1. User preference takes priority (if it's a valid theme)
    if user_theme and user_theme in THEMES:
        return user_theme

    # 2. Research Agent suggestion
    if suggested_theme and suggested_theme in THEMES:
        return suggested_theme

    # 3. Default mapping
    style_key = "dark" if "dark" in icon_style.lower() else (
        "clean" if icon_style in ("playful", "minimal") else "technical"
    )
    density = visual_density if visual_density in ("minimal", "moderate", "detailed") else "moderate"
    return THEME_MAPPING.get((density, style_key), DEFAULT_THEME)
