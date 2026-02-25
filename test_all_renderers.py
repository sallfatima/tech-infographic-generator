"""Test all 9 renderers × 3 themes with varying content lengths."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.infographic import (
    InfographicData, InfographicType, Node, Connection,
    ConnectionStyle, Layer, NodeShape, IconName,
)
from src.renderer.engine import ProRenderer
from src.renderer.themes import get_theme

W, H = 1400, 900

# ==== HELPER: create test data for each type ====

def make_process_data():
    nodes = [
        Node(id="p1", label="Data Collection", icon=IconName.DATABASE,
             description="Gather raw data from multiple sources including APIs, databases, web scraping, and manual uploads. Validate quality."),
        Node(id="p2", label="Preprocessing", icon=IconName.GEAR,
             description="Clean, normalize, and transform the data for downstream tasks."),
        Node(id="p3", label="Feature Engineering", icon=IconName.BRAIN,
             description="Create meaningful features from raw data using domain knowledge, statistical methods, and automated extraction."),
        Node(id="p4", label="Model Training", icon=IconName.TRANSFORMER,
             description="Train ML models using cross-validation and hyperparameter tuning."),
        Node(id="p5", label="Evaluation", icon=IconName.CHART,
             description="Evaluate model performance using accuracy, precision, recall, F1 score."),
        Node(id="p6", label="Deployment", icon=IconName.CLOUD,
             description="Deploy to production using containerized microservices."),
    ]
    return InfographicData(
        title="ML Pipeline Process",
        subtitle="End-to-end machine learning workflow",
        type=InfographicType.PROCESS,
        nodes=nodes, connections=[],
    )

def make_pipeline_data():
    nodes = [
        Node(id="s1", label="Ingestion", icon=IconName.DATABASE,
             description="Collect documents from various sources: PDFs, web pages, databases."),
        Node(id="s2", label="Chunking", icon=IconName.FILTER,
             description="Split documents into overlapping chunks of 500 tokens with semantic boundaries."),
        Node(id="s3", label="Embedding", icon=IconName.EMBEDDING,
             description="Convert text chunks into dense vectors using transformer models."),
        Node(id="s4", label="Vector Store", icon=IconName.VECTOR_DB,
             description="Store embeddings in a vector database for fast similarity search."),
    ]
    return InfographicData(
        title="RAG Data Pipeline",
        subtitle="From documents to searchable knowledge",
        type=InfographicType.PIPELINE,
        nodes=nodes,
        connections=[
            Connection(from_node="s1", to_node="s2", label="split"),
            Connection(from_node="s2", to_node="s3", label="encode"),
            Connection(from_node="s3", to_node="s4", label="index"),
        ],
    )

def make_architecture_data():
    nodes = [
        Node(id="ui", label="Web UI", icon=IconName.USER, description="React frontend with real-time updates"),
        Node(id="api", label="API Gateway", icon=IconName.API, description="FastAPI with rate limiting and auth middleware"),
        Node(id="llm", label="LLM Service", icon=IconName.BRAIN, description="Claude/GPT orchestration with fallback and retry"),
        Node(id="db", label="PostgreSQL", icon=IconName.DATABASE, description="Primary data store with pgvector extension"),
        Node(id="cache", label="Redis Cache", icon=IconName.CACHE, description="Caching layer for frequent queries"),
    ]
    layers = [
        Layer(name="Frontend", nodes=["ui"]),
        Layer(name="Backend", nodes=["api", "llm"]),
        Layer(name="Data", nodes=["db", "cache"]),
    ]
    return InfographicData(
        title="AI Application Architecture",
        subtitle="Three-tier system with LLM integration",
        type=InfographicType.ARCHITECTURE,
        nodes=nodes,
        connections=[
            Connection(from_node="ui", to_node="api", label="REST/WS", style=ConnectionStyle.ARROW),
            Connection(from_node="api", to_node="llm", label="invoke", style=ConnectionStyle.ARROW),
            Connection(from_node="api", to_node="db", label="query", style=ConnectionStyle.ARROW),
            Connection(from_node="api", to_node="cache", label="cache", style=ConnectionStyle.DASHED_ARROW),
        ],
        layers=layers,
    )

def make_comparison_data():
    nodes = [
        Node(id="c1", label="Supervised Learning", group="Traditional ML", icon=IconName.BRAIN,
             description="Learn from labeled training data with explicit input-output mappings"),
        Node(id="c2", label="Feature Engineering", group="Traditional ML", icon=IconName.GEAR,
             description="Manually design features using domain expertise"),
        Node(id="c3", label="Interpretability", group="Traditional ML",
             description="Models are generally more interpretable and explainable"),
        Node(id="c4", label="Self-Supervised", group="Deep Learning", icon=IconName.TRANSFORMER,
             description="Learn representations from unlabeled data through pretext tasks"),
        Node(id="c5", label="Auto Features", group="Deep Learning", icon=IconName.CHART,
             description="Automatic hierarchical feature learning from raw data"),
        Node(id="c6", label="Scale", group="Deep Learning",
             description="Performance improves with more data and compute resources"),
    ]
    return InfographicData(
        title="Traditional ML vs Deep Learning",
        subtitle="Key differences in approach",
        type=InfographicType.COMPARISON,
        nodes=nodes, connections=[],
    )

def make_concept_map_data():
    nodes = [
        Node(id="center", label="Transformer", icon=IconName.TRANSFORMER,
             description="Self-attention based neural architecture"),
        Node(id="n1", label="Attention", icon=IconName.BRAIN,
             description="Multi-head self-attention mechanism computing relevance scores"),
        Node(id="n2", label="Encoder", icon=IconName.LAYERS,
             description="Processes input sequence bidirectionally"),
        Node(id="n3", label="Decoder", icon=IconName.CODE,
             description="Generates output sequence autoregressively"),
        Node(id="n4", label="Feed-Forward", icon=IconName.WORKFLOW,
             description="Two-layer MLP applied to each position"),
        Node(id="n5", label="Positional Encoding",
             description="Injects sequence order information"),
    ]
    return InfographicData(
        title="Transformer Architecture",
        subtitle="Core components of the transformer model",
        type=InfographicType.CONCEPT_MAP,
        nodes=nodes,
        connections=[
            Connection(from_node="center", to_node="n1", label="core", style=ConnectionStyle.ARROW),
            Connection(from_node="center", to_node="n2", style=ConnectionStyle.ARROW),
            Connection(from_node="center", to_node="n3", style=ConnectionStyle.ARROW),
            Connection(from_node="center", to_node="n4", style=ConnectionStyle.ARROW),
            Connection(from_node="center", to_node="n5", style=ConnectionStyle.DASHED_ARROW),
        ],
    )

def make_flowchart_data():
    nodes = [
        Node(id="f1", label="User Query", icon=IconName.USER,
             description="Natural language question from the user about any topic"),
        Node(id="f2", label="Intent Classification", icon=IconName.BRAIN,
             description="Classify the query intent and extract entities using NLU"),
        Node(id="f3", label="Knowledge Retrieval", icon=IconName.SEARCH,
             description="Search vector database for relevant context documents"),
        Node(id="f4", label="LLM Generation", icon=IconName.LLM,
             description="Generate response using retrieved context and history"),
        Node(id="f5", label="Response", icon=IconName.CODE,
             description="Formatted answer returned to user with citations"),
    ]
    return InfographicData(
        title="RAG Query Flow",
        subtitle="Step-by-step query processing",
        type=InfographicType.FLOWCHART,
        nodes=nodes,
        connections=[
            Connection(from_node="f1", to_node="f2", style=ConnectionStyle.ARROW),
            Connection(from_node="f2", to_node="f3", style=ConnectionStyle.ARROW),
            Connection(from_node="f3", to_node="f4", style=ConnectionStyle.ARROW),
            Connection(from_node="f4", to_node="f5", style=ConnectionStyle.ARROW),
        ],
    )

def make_multi_agent_data():
    nodes = [
        Node(id="orch", label="Orchestrator", icon=IconName.BRAIN,
             description="Central coordinator routing tasks to specialized agents"),
        Node(id="a1", label="Research Agent", icon=IconName.SEARCH,
             description="Searches web and knowledge bases for relevant information"),
        Node(id="a2", label="Code Agent", icon=IconName.CODE,
             description="Writes, reviews, and refactors code using AST analysis"),
        Node(id="a3", label="Data Agent", icon=IconName.DATABASE,
             description="Queries databases and processes structured data"),
        Node(id="a4", label="Review Agent", icon=IconName.EVALUATION,
             description="Quality checks outputs from other agents"),
    ]
    return InfographicData(
        title="Multi-Agent System",
        subtitle="Collaborative AI agent architecture",
        type=InfographicType.MULTI_AGENT,
        nodes=nodes,
        connections=[
            Connection(from_node="orch", to_node="a1", label="delegate", style=ConnectionStyle.ARROW),
            Connection(from_node="orch", to_node="a2", label="delegate", style=ConnectionStyle.ARROW),
            Connection(from_node="orch", to_node="a3", label="delegate", style=ConnectionStyle.ARROW),
            Connection(from_node="orch", to_node="a4", label="review", style=ConnectionStyle.DASHED_ARROW),
        ],
    )

def make_infographic_data():
    nodes = [
        Node(id="i1", label="GPT-4", icon=IconName.BRAIN,
             description="OpenAI's flagship large language model with multimodal inputs and 1.7T parameters"),
        Node(id="i2", label="Claude", icon=IconName.LLM,
             description="Anthropic's constitutional AI assistant, trained with RLHF and focused on safety"),
        Node(id="i3", label="Gemini", icon=IconName.CHART,
             description="Google DeepMind's multimodal model supporting text, images, audio, and video"),
        Node(id="i4", label="LLaMA", icon=IconName.CODE,
             description="Meta's open-source foundation model family"),
        Node(id="i5", label="Mistral", icon=IconName.TRANSFORMER,
             description="Efficient open-weight models from Mistral AI with MoE architecture"),
        Node(id="i6", label="Cohere", icon=IconName.API,
             description="Enterprise-focused LLM API with RAG and embedding capabilities"),
    ]
    return InfographicData(
        title="Leading AI Foundation Models",
        subtitle="Major players in the LLM landscape 2024",
        type=InfographicType.INFOGRAPHIC,
        nodes=nodes, connections=[],
    )

def make_rag_pipeline_data():
    nodes = [
        Node(id="r1", label="Documents", icon=IconName.DOCUMENT,
             description="Source documents: PDFs, web pages, Markdown files, and structured data"),
        Node(id="r2", label="Chunking", icon=IconName.FILTER,
             description="Split into semantic chunks with overlap for context preservation"),
        Node(id="r3", label="Embedding", icon=IconName.EMBEDDING,
             description="Dense vector encoding using sentence transformers"),
        Node(id="r4", label="Vector DB", icon=IconName.VECTOR_DB,
             description="Indexed in Pinecone or Weaviate for approximate nearest neighbor search"),
        Node(id="r5", label="Retrieval", icon=IconName.SEARCH,
             description="Top-k similarity search with reranking"),
        Node(id="r6", label="LLM", icon=IconName.LLM,
             description="Context-augmented generation with Claude or GPT-4"),
    ]
    return InfographicData(
        title="Full RAG Pipeline",
        subtitle="Retrieval-Augmented Generation end to end",
        type=InfographicType.RAG_PIPELINE,
        nodes=nodes,
        connections=[
            Connection(from_node="r1", to_node="r2"),
            Connection(from_node="r2", to_node="r3"),
            Connection(from_node="r3", to_node="r4"),
            Connection(from_node="r4", to_node="r5"),
            Connection(from_node="r5", to_node="r6"),
        ],
    )


def make_zone_rag_data():
    """Test with zones and curved arrows (new viral features)."""
    nodes = [
        Node(id="user", label="User", icon=IconName.USER,
             description="Sends questions through a chat interface",
             zone="Query Phase"),
        Node(id="docs", label="Documents", icon=IconName.DOCUMENT,
             description="Source PDFs, web pages, knowledge base articles",
             zone="Ingestion Phase"),
        Node(id="chunker", label="Chunking", icon=IconName.FILTER,
             description="Splits documents into semantic chunks with overlap",
             zone="Ingestion Phase"),
        Node(id="embedder", label="Embedding", icon=IconName.EMBEDDING,
             shape=NodeShape.HEXAGON,
             description="Converts chunks into vectors using transformers",
             zone="Ingestion Phase"),
        Node(id="vectordb", label="Vector DB", icon=IconName.VECTOR_DB,
             shape=NodeShape.CYLINDER,
             description="Stores and indexes embeddings for fast search",
             zone="Ingestion Phase"),
        Node(id="retriever", label="Retriever", icon=IconName.SEARCH,
             description="Semantic similarity search for relevant context",
             zone="Query Phase"),
        Node(id="llm", label="LLM", icon=IconName.LLM,
             shape=NodeShape.HEXAGON,
             description="Generates response using retrieved chunks and query",
             zone="Query Phase"),
        Node(id="response", label="Response", icon=IconName.CHAT,
             description="Final answer with source citations",
             zone="Query Phase"),
    ]
    return InfographicData(
        title="RAG Chatbot Architecture",
        subtitle="Two-phase: ingestion and real-time query",
        type=InfographicType.ARCHITECTURE,
        nodes=nodes,
        zones=[
            {"name": "Ingestion Phase", "color": "#2B7DE9", "nodes": ["docs", "chunker", "embedder", "vectordb"]},
            {"name": "Query Phase", "color": "#E8833A", "nodes": ["user", "retriever", "llm", "response"]},
        ],
        connections=[
            Connection(from_node="docs", to_node="chunker", label="raw text", style=ConnectionStyle.DASHED_ARROW),
            Connection(from_node="chunker", to_node="embedder", label="chunks", style=ConnectionStyle.DASHED_ARROW),
            Connection(from_node="embedder", to_node="vectordb", label="vectors", style=ConnectionStyle.DASHED_ARROW),
            Connection(from_node="user", to_node="retriever", label="query", style=ConnectionStyle.CURVED_ARROW),
            Connection(from_node="vectordb", to_node="retriever", label="top-k", style=ConnectionStyle.CURVED_DASHED),
            Connection(from_node="retriever", to_node="llm", label="context", style=ConnectionStyle.DASHED_ARROW),
            Connection(from_node="llm", to_node="response", label="answer", style=ConnectionStyle.DASHED_ARROW),
            Connection(from_node="response", to_node="user", label="reply", style=ConnectionStyle.CURVED_DASHED),
        ],
    )


# ==== RUN TESTS ====

themes = ["guidebook", "whiteboard", "dark_modern"]

test_cases = [
    ("process", make_process_data),
    ("pipeline", make_pipeline_data),
    ("architecture", make_architecture_data),
    ("comparison", make_comparison_data),
    ("concept_map", make_concept_map_data),
    ("flowchart", make_flowchart_data),
    ("multi_agent", make_multi_agent_data),
    ("infographic", make_infographic_data),
    ("rag_pipeline", make_rag_pipeline_data),
    ("zone_rag", make_zone_rag_data),
]

errors = []
successes = []

for name, make_data in test_cases:
    for theme_name in themes:
        data = make_data()
        try:
            renderer = ProRenderer(theme_name=theme_name)
            out_path = f"output/test_{name}_{theme_name}.png"
            path = renderer.render(data, width=W, height=H, output_path=out_path)
            print(f"  ✅ {name} × {theme_name} → {path}")
            successes.append(f"{name}_{theme_name}")
        except Exception as e:
            import traceback
            print(f"  ❌ {name} × {theme_name} → {e}")
            traceback.print_exc()
            errors.append(f"{name}_{theme_name}: {e}")

print(f"\n{'='*60}")
print(f"Results: {len(successes)} passed, {len(errors)} failed")
if errors:
    print("\nFailed:")
    for e in errors:
        print(f"  ❌ {e}")
else:
    total = len(test_cases) * len(themes)
    print(f"All {total} renderer combinations working correctly!")
