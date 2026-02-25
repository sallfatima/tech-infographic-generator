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
- Professional, modern tech aesthetic
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

AI_ENGINEERING_TEMPLATE = """Create a professional AI Engineering infographic showing:

Topic: {topic}
Components:
{points}

Style Requirements:
- Clean white or light blue background (#F8FBFF)
- Colored section boxes with dashed borders (blue, orange, green, red)
- Hexagonal shapes for AI/ML components (LLMs, transformers, agents)
- Cylindrical shapes for databases and vector stores
- Numbered step badges on connections
- Clear data flow arrows with labels (embeddings, queries, context, tokens)
- Icons representing AI concepts: brain for LLM, magnifying glass for search, shield for guardrails
- Professional DailyDoseofDS / ByteByteGo visual style
- Subtitle explaining the system pattern or architecture
"""

RAG_PIPELINE_TEMPLATE = """Create a RAG (Retrieval-Augmented Generation) pipeline diagram:

System: {topic}
Pipeline Stages:
{points}

Style Requirements:
- Horizontal pipeline flow from left to right
- Document/chunk icons for ingestion stages
- Vector/embedding visualization for encoding stages
- Database cylinder for vector store
- Brain/AI icon for the LLM generation stage
- Colored arrows showing data transformation at each stage
- Labels: "raw text" → "chunks" → "embeddings" → "vectors" → "context + query" → "response"
- Professional tech blue color scheme
"""

MULTI_AGENT_TEMPLATE = """Create a multi-agent AI system diagram:

System: {topic}
Agents and Roles:
{points}

Style Requirements:
- Central manager/coordinator agent node (larger, prominent)
- Surrounding specialized agent nodes with distinct colors
- Tool/resource nodes connected to agents with dashed lines
- Bidirectional arrows for agent communication
- Step numbers on connections showing task flow
- Role labels on each agent (Researcher, Coder, Reviewer, etc.)
- Professional whiteboard style with clean layout
"""

COMPARISON_TEMPLATE = """Create a side-by-side comparison chart for:

Topic: {topic}
Options:
{points}

Style Requirements:
- Two or more columns with clear headers
- Color-coded columns (blue vs orange vs green)
- Feature rows with checkmarks or descriptions
- Gradient header backgrounds
- Clean, readable typography
- Professional comparison layout
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
        "ai_engineering": AI_ENGINEERING_TEMPLATE,
        "rag_pipeline": RAG_PIPELINE_TEMPLATE,
        "multi_agent": MULTI_AGENT_TEMPLATE,
        "comparison": COMPARISON_TEMPLATE,
    }

    # Auto-detect AI engineering content
    if style == "infographic":
        lower_desc = description.lower()
        ai_keywords = [
            "llm", "rag", "agent", "embedding", "fine-tun", "finetun",
            "transformer", "prompt engineering", "vector database", "mcp",
            "multi-agent", "react pattern", "context engineering",
            "guardrails", "lora", "rlhf", "grpo", "chunking",
        ]
        if any(kw in lower_desc for kw in ai_keywords):
            style = "ai_engineering"

    template = templates.get(style, INFOGRAPHIC_TEMPLATE)
    return template.format(topic=topic, points=points)
