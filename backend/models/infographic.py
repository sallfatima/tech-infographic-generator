"""Pydantic data models for structured infographic representation.

These models form the contract between the LLM analyzer (which produces them)
and the rendering engine (which consumes them).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class InfographicType(str, Enum):
    ARCHITECTURE = "architecture"
    FLOWCHART = "flowchart"
    COMPARISON = "comparison"
    PROCESS = "process"
    CONCEPT_MAP = "concept_map"
    INFOGRAPHIC = "infographic"
    PIPELINE = "pipeline"
    TIMELINE = "timeline"
    MULTI_AGENT = "multi_agent"
    RAG_PIPELINE = "rag_pipeline"


class ConnectionStyle(str, Enum):
    ARROW = "arrow"
    DASHED_ARROW = "dashed_arrow"
    BIDIRECTIONAL = "bidirectional"
    LINE = "line"
    CURVED_ARROW = "curved_arrow"
    CURVED_DASHED = "curved_dashed"


class NodeShape(str, Enum):
    ROUNDED_RECT = "rounded_rect"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    DIAMOND = "diamond"
    CYLINDER = "cylinder"
    HEXAGON = "hexagon"
    CLOUD = "cloud"
    PARALLELOGRAM = "parallelogram"
    PERSON = "person"


class IconName(str, Enum):
    DATABASE = "database"
    SERVER = "server"
    CLOUD = "cloud"
    USER = "user"
    LOCK = "lock"
    API = "api"
    NETWORK = "network"
    CODE = "code"
    BRAIN = "brain"
    CHART = "chart"
    GEAR = "gear"
    LIGHTNING = "lightning"
    CONTAINER = "container"
    QUEUE = "queue"
    CACHE = "cache"
    MONITOR = "monitor"
    SHIELD = "shield"
    GLOBE = "globe"
    ARROW_RIGHT = "arrow_right"
    CHECK = "check"
    STAR = "star"
    FOLDER = "folder"
    CPU = "cpu"
    MEMORY = "memory"
    SEARCH = "search"
    FILTER = "filter"
    LAYERS = "layers"
    WORKFLOW = "workflow"
    DOCUMENT = "document"
    PLAY = "play"
    # AI Engineering icons
    AGENT = "agent"
    RAG = "rag"
    PROMPT = "prompt"
    FINETUNE = "finetune"
    EMBEDDING = "embedding"
    VECTOR_DB = "vector_db"
    LLM = "llm"
    TRANSFORMER = "transformer"
    EVALUATION = "evaluation"
    GUARDRAILS = "guardrails"
    CONTEXT = "context"
    TOOL_USE = "tool_use"
    MCP = "mcp"
    MULTI_AGENT = "multi_agent"
    REASONING = "reasoning"
    # Additional visual icons
    PERSON_LAPTOP = "person_laptop"
    CHAT = "chat"
    PIPELINE_ICON = "pipeline_icon"


class Node(BaseModel):
    id: str = Field(description="Unique lowercase ID, e.g. 'api_gateway'")
    label: str = Field(max_length=40, description="Short display label")
    description: Optional[str] = Field(default=None, max_length=250)
    icon: Optional[IconName] = None
    shape: NodeShape = NodeShape.ROUNDED_RECT
    color: Optional[str] = Field(default=None, description="Hex color override")
    layer: Optional[int] = Field(default=None, description="Layer index (0=top)")
    group: Optional[str] = Field(default=None, description="Grouping label")
    zone: Optional[str] = Field(default=None, description="Zone name for visual grouping")
    size: Optional[str] = Field(default=None, description="Node size: small/medium/large")


class Connection(BaseModel):
    from_node: str
    to_node: str
    label: Optional[str] = Field(default=None, max_length=30)
    style: ConnectionStyle = ConnectionStyle.ARROW


class Layer(BaseModel):
    name: str = Field(max_length=30)
    color: Optional[str] = None
    nodes: list[str] = Field(description="Node IDs in this layer")


class InfographicData(BaseModel):
    """Complete structured representation of an infographic.

    Produced by the LLM analyzer, consumed by the rendering engine.
    """

    title: str = Field(max_length=80)
    subtitle: Optional[str] = Field(default=None, max_length=120)
    type: InfographicType
    nodes: list[Node]
    connections: list[Connection] = []
    layers: list[Layer] = []
    zones: list[dict] = Field(default=[], description="Zone defs: [{name, color, nodes}]")
    color_scheme: str = "tech_blue"
    footer: Optional[str] = None
    metadata: dict = {}
