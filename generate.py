#!/usr/bin/env python3
"""CLI tool to generate tech infographic images from text descriptions.

Usage:
    python generate.py "How DNS works" --style infographic
    python generate.py "Step 1: Request\nStep 2: Resolve\nStep 3: Response" --style flowchart
    python generate.py --preset bytebyteai "Machine Learning Pipeline"
    python generate.py --backend dalle "API Gateway Architecture"
"""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.generators.local_generator import LocalInfographicGenerator
from src.styles.presets import get_preset, list_presets, STYLE_PRESETS


def get_generator(backend: str, palette: str = "tech_blue"):
    """Instantiate the right generator based on backend choice."""
    if backend == "dalle":
        from src.generators.dalle_generator import DalleGenerator
        return DalleGenerator()
    elif backend == "stable-diffusion":
        from src.generators.sd_generator import StableDiffusionGenerator
        return StableDiffusionGenerator()
    else:
        return LocalInfographicGenerator(palette=palette)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Image Generator - Create tech infographics from text descriptions."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("description")
@click.option(
    "--style", "-s",
    type=click.Choice(["infographic", "diagram", "flowchart", "comparison", "tech", "minimal"]),
    default="infographic",
    help="Visual style of the generated image.",
)
@click.option(
    "--backend", "-b",
    type=click.Choice(["local", "dalle", "stable-diffusion"]),
    default=None,
    help="Generation backend. Default from .env or 'local'.",
)
@click.option(
    "--preset", "-p",
    type=click.Choice(list_presets()),
    default=None,
    help="Use a predefined style preset.",
)
@click.option("--width", "-w", type=int, default=None, help="Image width in pixels.")
@click.option("--height", "-h", type=int, default=None, help="Image height in pixels.")
@click.option("--palette", type=click.Choice(["tech_blue", "clean_white", "dark_modern"]), default=None)
@click.option("--output", "-o", type=str, default=None, help="Output file path.")
def create(description, style, backend, preset, width, height, palette, output):
    """Generate an image from a text description.

    DESCRIPTION: Text describing the image to generate. Use \\n for line breaks.
    """
    # Handle escaped newlines
    description = description.replace("\\n", "\n")

    # Apply preset if given
    if preset:
        p = get_preset(preset)
        style = style or p["layout"]
        width = width or p["width"]
        height = height or p["height"]
        palette = palette or p["palette"]

    # Defaults
    backend = backend or os.getenv("DEFAULT_BACKEND", "local")
    width = width or 1200
    height = height or 800
    palette = palette or "tech_blue"

    console.print(Panel(
        f"[bold]Description:[/bold] {description[:100]}...\n"
        f"[bold]Style:[/bold] {style}  |  [bold]Backend:[/bold] {backend}\n"
        f"[bold]Size:[/bold] {width}x{height}  |  [bold]Palette:[/bold] {palette}",
        title="Generating Image",
        border_style="blue",
    ))

    generator = get_generator(backend, palette)

    with console.status("[bold blue]Generating image..."):
        result = generator.generate(
            description=description,
            style=style,
            width=width,
            height=height,
            output_path=output,
        )

    console.print(f"\n[green bold]Image saved:[/green bold] {result.image_path}")
    console.print(f"[dim]Backend: {result.backend} | Size: {result.width}x{result.height}[/dim]")


@cli.command()
def presets():
    """List all available style presets."""
    table = Table(title="Available Style Presets")
    table.add_column("Name", style="cyan bold")
    table.add_column("Layout", style="green")
    table.add_column("Size")
    table.add_column("Description")

    for name, p in STYLE_PRESETS.items():
        table.add_row(
            name,
            p["layout"],
            f"{p['width']}x{p['height']}",
            p["description"],
        )

    console.print(table)


@cli.command()
@click.argument("description")
@click.option("--count", "-n", type=int, default=3, help="Number of variations.")
@click.option("--style", "-s", default="infographic")
@click.option("--palette", default=None)
def batch(description, count, style, palette):
    """Generate multiple variations of the same description."""
    description = description.replace("\\n", "\n")
    palettes = ["tech_blue", "clean_white", "dark_modern"]

    console.print(f"[bold]Generating {count} variations...[/bold]\n")

    for i in range(count):
        pal = palette or palettes[i % len(palettes)]
        gen = LocalInfographicGenerator(palette=pal)
        result = gen.generate(
            description=description,
            style=style,
            output_path=f"output/batch_{i + 1}_{pal}.png",
        )
        console.print(f"  [{pal}] {result.image_path}")

    console.print(f"\n[green bold]Done! Generated {count} images in ./output/[/green bold]")


if __name__ == "__main__":
    cli()
