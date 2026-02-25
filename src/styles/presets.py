"""Predefined style presets for different image types."""

STYLE_PRESETS = {
    "tech_infographic": {
        "description": "Clean tech infographic, dark background, blue/purple accents",
        "palette": "tech_blue",
        "layout": "infographic",
        "width": 1200,
        "height": 800,
        "prompt_prefix": (
            "Professional tech infographic, dark navy background, "
            "blue and purple gradient accents, clean card-based layout, "
            "numbered sections with badge icons, modern sans-serif typography, "
            "subtle shadows, structured grid layout. "
        ),
    },
    "system_design": {
        "description": "System architecture diagram with boxes and arrows",
        "palette": "clean_white",
        "layout": "diagram",
        "width": 1400,
        "height": 900,
        "prompt_prefix": (
            "Clean system architecture diagram, white background, "
            "colored boxes connected by arrows, microservices layout, "
            "cloud infrastructure icons, professional engineering style. "
        ),
    },
    "process_flow": {
        "description": "Step-by-step flowchart",
        "palette": "tech_blue",
        "layout": "flowchart",
        "width": 1400,
        "height": 600,
        "prompt_prefix": (
            "Professional flowchart, horizontal flow, rounded rectangles, "
            "directional arrows, color-coded steps, clean and minimal. "
        ),
    },
    "comparison": {
        "description": "Side-by-side comparison chart",
        "palette": "dark_modern",
        "layout": "comparison",
        "width": 1200,
        "height": 800,
        "prompt_prefix": (
            "Side-by-side comparison chart, columns with headers, "
            "checkmarks and icons, clean table-like layout. "
        ),
    },
    "course_card": {
        "description": "Course or product showcase card",
        "palette": "tech_blue",
        "layout": "infographic",
        "width": 800,
        "height": 600,
        "prompt_prefix": (
            "Modern course card, dark background, gradient accent, "
            "project number badge, concise description, professional. "
        ),
    },
    "social_media": {
        "description": "Social media sized tech post",
        "palette": "dark_modern",
        "layout": "infographic",
        "width": 1080,
        "height": 1080,
        "prompt_prefix": (
            "Eye-catching social media post, bold headline, "
            "tech-themed icons, vibrant accents on dark background. "
        ),
    },
}


def get_preset(name: str) -> dict:
    return STYLE_PRESETS.get(name, STYLE_PRESETS["tech_infographic"])


def list_presets() -> list[str]:
    return list(STYLE_PRESETS.keys())
