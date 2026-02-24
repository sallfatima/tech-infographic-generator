"""Prompt templates for different AI generation backends.

These templates help transform simple user descriptions into
detailed prompts that produce better results with DALL-E / SD.
"""

INFOGRAPHIC_TEMPLATE = """Create a professional tech infographic with the following content:

Topic: {topic}
Key Points:
{points}

Style Requirements:
- Dark navy (#0F172A) background with soft gradients
- Card-based layout with rounded corners
- Blue (#3B82F6) and purple (#8B5CF6) accent colors
- Clean sans-serif typography with clear hierarchy
- Numbered badge icons for each section
- Subtle drop shadows on cards
- Horizontal gradient accent bar at the top
- Professional, modern tech aesthetic similar to ByteByteGo
"""

DIAGRAM_TEMPLATE = """Create a system architecture diagram showing:

System: {topic}
Components:
{points}

Style Requirements:
- White or light gray background
- Color-coded boxes for different component types
- Clear directional arrows showing data flow
- Labels on all connections
- Cloud/database/server icons where appropriate
- Professional engineering documentation style
"""

FLOWCHART_TEMPLATE = """Create a process flowchart for:

Process: {topic}
Steps:
{points}

Style Requirements:
- Horizontal left-to-right flow
- Rounded rectangles for process steps
- Diamond shapes for decision points
- Clear directional arrows
- Pastel color coding for different step types
- Clean, minimal design
"""


def build_prompt(description: str, style: str = "infographic") -> str:
    """Build a detailed prompt from a user description."""
    lines = [l.strip() for l in description.strip().split("\n") if l.strip()]
    topic = lines[0] if lines else description
    points = "\n".join(f"- {l}" for l in lines[1:]) if len(lines) > 1 else f"- {topic}"

    templates = {
        "infographic": INFOGRAPHIC_TEMPLATE,
        "diagram": DIAGRAM_TEMPLATE,
        "flowchart": FLOWCHART_TEMPLATE,
    }

    template = templates.get(style, INFOGRAPHIC_TEMPLATE)
    return template.format(topic=topic, points=points)
