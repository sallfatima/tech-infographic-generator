"""LLM-powered text analyzer that converts free text to InfographicData."""

from __future__ import annotations

import json
import os
import re

from ..models.infographic import InfographicData
from .prompts import get_system_prompt


class LLMAnalyzer:
    """Analyzes text descriptions using Claude or OpenAI and returns structured infographic data."""

    def __init__(self, provider: str | None = None):
        """Initialize the analyzer.

        Args:
            provider: "anthropic" or "openai". Auto-detected from env vars if None.
        """
        if provider:
            self.provider = provider
        elif os.getenv("ANTHROPIC_API_KEY"):
            self.provider = "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
        else:
            self.provider = "anthropic"  # default

    async def analyze(self, text: str, type_hint: str | None = None) -> InfographicData:
        """Parse raw text into structured InfographicData.

        Args:
            text: Raw input text (LinkedIn post or description).
            type_hint: Optional infographic type hint.

        Returns:
            Validated InfographicData instance.
        """
        user_prompt = text.strip()
        if type_hint:
            user_prompt += f"\n\n[Preferred infographic type: {type_hint}]"

        system_prompt = get_system_prompt()

        raw_json = await self._call_llm(system_prompt, user_prompt)
        return self._parse_response(raw_json)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM API and return raw response text."""
        if self.provider == "anthropic":
            return await self._call_anthropic(system_prompt, user_prompt)
        else:
            return await self._call_openai(system_prompt, user_prompt)

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        import anthropic
        import httpx

        client = anthropic.AsyncAnthropic(
            timeout=httpx.Timeout(60.0, connect=10.0),
        )
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(timeout=60.0)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=4096,
        )
        return response.choices[0].message.content

    def _parse_response(self, raw: str) -> InfographicData:
        """Parse and validate the LLM response into InfographicData."""
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Remove ```json or ``` wrapping
            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to extract JSON from the response
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                data = json.loads(match.group())
            else:
                raise ValueError(f"Could not parse LLM response as JSON: {e}")

        return InfographicData.model_validate(data)

    def analyze_sync(self, text: str, type_hint: str | None = None) -> InfographicData:
        """Synchronous version of analyze() for CLI usage."""
        import asyncio
        return asyncio.run(self.analyze(text, type_hint))
