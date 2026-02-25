# Image Generator - Tech Infographics from Text

Generate professional tech infographic images from text descriptions.

## Features

- **3 generation backends**:
  - `local` - Pillow-based generator (no API key needed)
  - `dalle` - OpenAI DALL-E 3
  - `stable-diffusion` - Stable Diffusion XL (local GPU)

- **Multiple styles**: infographic, diagram, flowchart, comparison, tech, minimal

- **3 color palettes**: tech_blue (dark), clean_white (light), dark_modern (orange/pink)

- **Predefined presets**: tech_infographic, system_design, process_flow, comparison, course_card, social_media

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Generate an infographic (local, no API key needed)
python generate.py create "How DNS Works\nStep 1: Browser sends request\nStep 2: DNS resolver queries\nStep 3: IP address returned\nStep 4: Browser connects" --style infographic

# Generate a flowchart
python generate.py create "User Authentication Flow\nLogin Page\nValidate Credentials\nCheck 2FA\nGenerate JWT\nReturn Token" --style flowchart

# Generate with a preset
python generate.py create "Machine Learning Pipeline" --preset tech_infographic

# Generate with DALL-E (requires OPENAI_API_KEY)
python generate.py create "Kubernetes Pod Lifecycle" --backend dalle --style diagram

# Generate batch variations
python generate.py batch "API Gateway Architecture\nLoad Balancer\nRate Limiting\nAuth\nRouting\nCaching" -n 3

# List all presets
python generate.py presets
```

## Project Structure

```
.
├── generate.py              # CLI entry point
├── requirements.txt
├── .env.example
├── src/
│   ├── generators/
│   │   ├── base.py          # Abstract base class
│   │   ├── dalle_generator.py
│   │   ├── sd_generator.py
│   │   └── local_generator.py  # No API key needed
│   ├── styles/
│   │   └── presets.py       # Style presets
│   └── templates/
│       └── prompts.py       # Prompt engineering templates
├── output/                  # Generated images
└── examples/                # Example outputs
```

## Backends

### Local (default)
No API key required. Uses Pillow to render structured infographics with cards, badges, gradients. Best for quick prototyping.

### DALL-E 3
Set `OPENAI_API_KEY` in `.env`. Produces photorealistic/artistic images. Best for creative visuals.

### Stable Diffusion XL
Requires GPU (CUDA/MPS) and `HF_TOKEN`. Runs locally. Best for custom model fine-tuning.

## Examples

```bash
# System architecture diagram
python generate.py create "Microservices Architecture\nAPI Gateway: Routes requests\nAuth Service: JWT validation\nUser Service: CRUD operations\nDB: PostgreSQL cluster\nCache: Redis layer\nQueue: RabbitMQ events" --style diagram --palette clean_white

# Comparison chart
python generate.py create "SQL vs NoSQL\nSQL: Structured schema, ACID, joins\nNoSQL: Flexible schema, scalable, fast reads" --style comparison

# Social media post
python generate.py create "5 Tips for System Design Interviews" --preset social_media
```
