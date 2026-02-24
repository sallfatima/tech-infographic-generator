"""Local infographic/diagram generator using Pillow + matplotlib.

No API key required. Generates structured infographic-style images
from text descriptions using layout templates.
"""

import math
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .base import ImageGenerator, GenerationResult

# Color palettes inspired by ByteByteAI / tech infographic style
PALETTES = {
    "tech_blue": {
        "bg": "#0F172A",
        "card": "#1E293B",
        "accent": "#3B82F6",
        "accent2": "#8B5CF6",
        "text": "#F8FAFC",
        "text_muted": "#94A3B8",
        "border": "#334155",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "gradient_start": "#3B82F6",
        "gradient_end": "#8B5CF6",
    },
    "clean_white": {
        "bg": "#FFFFFF",
        "card": "#F8FAFC",
        "accent": "#2563EB",
        "accent2": "#7C3AED",
        "text": "#1E293B",
        "text_muted": "#64748B",
        "border": "#E2E8F0",
        "success": "#16A34A",
        "warning": "#D97706",
        "gradient_start": "#2563EB",
        "gradient_end": "#7C3AED",
    },
    "dark_modern": {
        "bg": "#18181B",
        "card": "#27272A",
        "accent": "#F97316",
        "accent2": "#EC4899",
        "text": "#FAFAFA",
        "text_muted": "#A1A1AA",
        "border": "#3F3F46",
        "success": "#4ADE80",
        "warning": "#FBBF24",
        "gradient_start": "#F97316",
        "gradient_end": "#EC4899",
    },
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


class LocalInfographicGenerator(ImageGenerator):
    """Generate infographic-style images locally with Pillow."""

    def __init__(self, palette: str = "tech_blue"):
        self.colors = PALETTES.get(palette, PALETTES["tech_blue"])
        self.palette_name = palette

    def generate(
        self,
        description: str,
        style: str = "infographic",
        width: int = 1200,
        height: int = 800,
        output_path: str | None = None,
    ) -> GenerationResult:
        # Parse the description to extract structured content
        sections = self._parse_description(description)

        if style == "flowchart":
            img = self._render_flowchart(sections, width, height)
        elif style == "diagram":
            img = self._render_diagram(sections, width, height)
        elif style == "comparison":
            img = self._render_comparison(sections, width, height)
        else:
            img = self._render_infographic(sections, width, height)

        if output_path is None:
            output_path = f"output/local_{int(time.time())}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG", quality=95)

        return GenerationResult(
            image_path=Path(output_path),
            prompt_used=description,
            backend=f"local-pillow ({self.palette_name})",
            width=width,
            height=height,
        )

    def _parse_description(self, description: str) -> list[dict]:
        """Parse a text description into structured sections.

        Supports formats:
          - "Title: content" lines
          - "1. item" numbered lists
          - "- item" bullet lists
          - Plain paragraphs (split by sentence)
        """
        lines = [l.strip() for l in description.strip().split("\n") if l.strip()]
        sections = []

        for line in lines:
            if ":" in line and len(line.split(":")[0]) < 40:
                title, content = line.split(":", 1)
                sections.append({"title": title.strip(), "content": content.strip()})
            elif line[0].isdigit() and "." in line[:4]:
                content = line.split(".", 1)[1].strip()
                sections.append({"title": f"Step {line[0]}", "content": content})
            elif line.startswith("- ") or line.startswith("* "):
                sections.append({"title": "", "content": line[2:]})
            else:
                sections.append({"title": "", "content": line})

        if not sections:
            sections = [{"title": "Info", "content": description}]

        return sections

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Try to load a system font, fallback to default."""
        font_paths = [
            "/System/Library/Fonts/SFPro-Bold.otf" if bold else "/System/Library/Fonts/SFPro-Regular.otf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNS.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()

    def _draw_rounded_rect(
        self, draw: ImageDraw.Draw, xy: tuple, radius: int, fill: str, outline: str | None = None
    ):
        x0, y0, x1, y1 = xy
        r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
        fill_rgb = hex_to_rgb(fill)
        outline_rgb = hex_to_rgb(outline) if outline else None
        draw.rounded_rectangle(xy, radius=r, fill=fill_rgb, outline=outline_rgb)

    def _draw_gradient_bar(self, img: Image.Image, xy: tuple):
        """Draw a horizontal gradient bar."""
        x0, y0, x1, y1 = xy
        start = hex_to_rgb(self.colors["gradient_start"])
        end = hex_to_rgb(self.colors["gradient_end"])
        width = x1 - x0

        for x in range(width):
            ratio = x / max(width - 1, 1)
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            for y in range(y0, y1):
                img.putpixel((x0 + x, y), (r, g, b))

    def _render_infographic(
        self, sections: list[dict], width: int, height: int
    ) -> Image.Image:
        img = Image.new("RGB", (width, height), hex_to_rgb(self.colors["bg"]))
        draw = ImageDraw.Draw(img)

        # Top gradient accent bar
        self._draw_gradient_bar(img, (0, 0, width, 6))

        # Title
        title_font = self._get_font(36, bold=True)
        title_text = sections[0]["title"] or sections[0]["content"][:50]
        draw.text((60, 40), title_text, fill=hex_to_rgb(self.colors["text"]), font=title_font)

        # Subtitle line
        subtitle_font = self._get_font(18)
        if sections[0]["content"] and sections[0]["title"]:
            draw.text(
                (60, 90),
                sections[0]["content"][:80],
                fill=hex_to_rgb(self.colors["text_muted"]),
                font=subtitle_font,
            )

        # Cards grid
        cards = sections[1:] if len(sections) > 1 else sections
        if not cards:
            return img

        margin = 60
        card_gap = 20
        top_offset = 140
        available_w = width - 2 * margin
        available_h = height - top_offset - margin

        cols = min(len(cards), 3)
        rows = math.ceil(len(cards) / cols)
        card_w = (available_w - (cols - 1) * card_gap) // cols
        card_h = min((available_h - (rows - 1) * card_gap) // rows, 250)

        accent_colors = [
            self.colors["accent"],
            self.colors["accent2"],
            self.colors["success"],
            self.colors["warning"],
        ]

        for i, section in enumerate(cards):
            col = i % cols
            row = i // cols
            x = margin + col * (card_w + card_gap)
            y = top_offset + row * (card_h + card_gap)

            # Card background
            self._draw_rounded_rect(
                draw, (x, y, x + card_w, y + card_h), 12, self.colors["card"], self.colors["border"]
            )

            # Left accent bar on card
            accent = accent_colors[i % len(accent_colors)]
            self._draw_rounded_rect(draw, (x, y, x + 4, y + card_h), 2, accent)

            # Number badge
            badge_r = 18
            badge_cx = x + 30
            badge_cy = y + 30
            draw.ellipse(
                (badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r),
                fill=hex_to_rgb(accent),
            )
            num_font = self._get_font(18, bold=True)
            draw.text(
                (badge_cx - 6, badge_cy - 10),
                str(i + 1),
                fill=hex_to_rgb("#FFFFFF"),
                font=num_font,
            )

            # Card title
            card_title_font = self._get_font(20, bold=True)
            t = section["title"] or f"Point {i + 1}"
            draw.text(
                (x + 60, y + 18),
                t[:30],
                fill=hex_to_rgb(self.colors["text"]),
                font=card_title_font,
            )

            # Card content (word wrap)
            content_font = self._get_font(14)
            content = section["content"]
            self._draw_wrapped_text(
                draw, content, (x + 20, y + 55), card_w - 40, content_font,
                hex_to_rgb(self.colors["text_muted"]), line_height=22, max_lines=(card_h - 70) // 22,
            )

        return img

    def _render_flowchart(
        self, sections: list[dict], width: int, height: int
    ) -> Image.Image:
        img = Image.new("RGB", (width, height), hex_to_rgb(self.colors["bg"]))
        draw = ImageDraw.Draw(img)

        self._draw_gradient_bar(img, (0, 0, width, 4))

        n = len(sections)
        box_w = min(220, (width - 100) // max(n, 1) - 30)
        box_h = 80
        gap = 40
        total_w = n * box_w + (n - 1) * gap
        start_x = (width - total_w) // 2
        cy = height // 2

        font = self._get_font(16, bold=True)
        small_font = self._get_font(12)
        arrow_color = hex_to_rgb(self.colors["accent"])

        for i, section in enumerate(sections):
            x = start_x + i * (box_w + gap)
            y = cy - box_h // 2

            accent = self.colors["accent"] if i % 2 == 0 else self.colors["accent2"]
            self._draw_rounded_rect(draw, (x, y, x + box_w, y + box_h), 10, self.colors["card"], accent)

            label = section["title"] or section["content"][:25]
            draw.text((x + 15, y + 15), label[:20], fill=hex_to_rgb(self.colors["text"]), font=font)

            if section["content"] and section["title"]:
                draw.text(
                    (x + 15, y + 42),
                    section["content"][:30],
                    fill=hex_to_rgb(self.colors["text_muted"]),
                    font=small_font,
                )

            # Arrow to next box
            if i < n - 1:
                ax = x + box_w + 5
                draw.line(
                    [(ax, cy), (ax + gap - 10, cy)], fill=arrow_color, width=2
                )
                # Arrowhead
                draw.polygon(
                    [(ax + gap - 10, cy - 6), (ax + gap - 2, cy), (ax + gap - 10, cy + 6)],
                    fill=arrow_color,
                )

        return img

    def _render_diagram(
        self, sections: list[dict], width: int, height: int
    ) -> Image.Image:
        img = Image.new("RGB", (width, height), hex_to_rgb(self.colors["bg"]))
        draw = ImageDraw.Draw(img)

        self._draw_gradient_bar(img, (0, 0, width, 4))

        title_font = self._get_font(28, bold=True)
        title = sections[0]["title"] or "System Architecture"
        draw.text((40, 30), title, fill=hex_to_rgb(self.colors["text"]), font=title_font)

        items = sections[1:] if len(sections) > 1 else sections
        n = len(items)
        if n == 0:
            return img

        cx, cy = width // 2, height // 2 + 20
        radius = min(width, height) // 3
        box_w, box_h = 160, 70
        font = self._get_font(14, bold=True)
        line_color = hex_to_rgb(self.colors["border"])

        # Central node
        self._draw_rounded_rect(
            draw, (cx - 70, cy - 35, cx + 70, cy + 35), 10, self.colors["accent"]
        )
        draw.text((cx - 40, cy - 10), "Core", fill=hex_to_rgb("#FFFFFF"), font=font)

        for i, section in enumerate(items):
            angle = (2 * math.pi * i) / n - math.pi / 2
            bx = int(cx + radius * math.cos(angle))
            by = int(cy + radius * math.sin(angle))

            draw.line([(cx, cy), (bx, by)], fill=line_color, width=2)

            color = self.colors["accent"] if i % 2 == 0 else self.colors["accent2"]
            self._draw_rounded_rect(
                draw, (bx - box_w // 2, by - box_h // 2, bx + box_w // 2, by + box_h // 2),
                8, self.colors["card"], color,
            )

            label = section["title"] or section["content"][:20]
            draw.text(
                (bx - box_w // 2 + 10, by - 10),
                label[:18],
                fill=hex_to_rgb(self.colors["text"]),
                font=font,
            )

        return img

    def _render_comparison(
        self, sections: list[dict], width: int, height: int
    ) -> Image.Image:
        img = Image.new("RGB", (width, height), hex_to_rgb(self.colors["bg"]))
        draw = ImageDraw.Draw(img)

        self._draw_gradient_bar(img, (0, 0, width, 4))

        n = min(len(sections), 3)
        margin = 60
        gap = 30
        col_w = (width - 2 * margin - (n - 1) * gap) // n

        title_font = self._get_font(22, bold=True)
        body_font = self._get_font(14)
        colors = [self.colors["accent"], self.colors["accent2"], self.colors["success"]]

        for i, section in enumerate(sections[:n]):
            x = margin + i * (col_w + gap)
            y_top = 40

            # Column header
            self._draw_rounded_rect(
                draw, (x, y_top, x + col_w, y_top + 50), 8, colors[i % len(colors)]
            )
            t = section["title"] or f"Option {i + 1}"
            draw.text((x + 15, y_top + 12), t[:25], fill=hex_to_rgb("#FFFFFF"), font=title_font)

            # Column body
            self._draw_rounded_rect(
                draw, (x, y_top + 55, x + col_w, height - 40), 8, self.colors["card"], self.colors["border"]
            )
            self._draw_wrapped_text(
                draw, section["content"], (x + 15, y_top + 70), col_w - 30,
                body_font, hex_to_rgb(self.colors["text_muted"]), line_height=22,
                max_lines=(height - y_top - 120) // 22,
            )

        return img

    def _draw_wrapped_text(
        self,
        draw: ImageDraw.Draw,
        text: str,
        pos: tuple,
        max_width: int,
        font: ImageFont.FreeTypeFont,
        fill: tuple,
        line_height: int = 20,
        max_lines: int = 10,
    ):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        x, y = pos
        for i, line in enumerate(lines[:max_lines]):
            draw.text((x, y + i * line_height), line, fill=fill, font=font)
