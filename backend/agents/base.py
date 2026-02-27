"""Base agent class with shared LLM calling logic.

All agents inherit from BaseAgent and get:
- Async LLM calls (Anthropic/OpenAI)
- JSON response parsing with fallbacks
- Logging and error handling
"""

from __future__ import annotations

import json
import os
import re
import time
from abc import ABC, abstractmethod

from .context import PipelineContext


class BaseAgent(ABC):
    """Abstract base class for all pipeline agents.

    Provides shared LLM calling infrastructure (extracted from LLMAnalyzer).
    Each agent must implement `run()` which reads from and writes to the
    shared PipelineContext.
    """

    # Subclasses set these
    name: str = "base"
    description: str = "Base agent"

    def __init__(self, provider: str | None = None):
        """Initialize the agent.

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
            self.provider = "anthropic"

    @abstractmethod
    async def run(self, ctx: PipelineContext) -> PipelineContext:
        """Execute the agent's task.

        Args:
            ctx: Shared pipeline context with inputs and outputs.

        Returns:
            The updated PipelineContext.
        """
        ...

    # ---- Shared LLM calling methods ----

    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        """Call the LLM and return raw response text.

        Args:
            system_prompt: System message.
            user_prompt: User message.
            model: Model override. If None, uses agent's default.
            max_tokens: Max tokens in response.
            json_mode: If True, request JSON output (OpenAI only).

        Returns:
            Raw response text from the LLM.
        """
        if self.provider == "anthropic":
            return await self._call_anthropic(
                system_prompt, user_prompt, model=model, max_tokens=max_tokens
            )
        else:
            return await self._call_openai(
                system_prompt, user_prompt, model=model,
                max_tokens=max_tokens, json_mode=json_mode
            )

    async def call_llm_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Call the LLM and parse the response as JSON.

        Args:
            system_prompt: System message.
            user_prompt: User message.
            model: Model override.
            max_tokens: Max tokens in response.

        Returns:
            Parsed JSON dict.

        Raises:
            ValueError: If response cannot be parsed as JSON.
        """
        raw = await self.call_llm(
            system_prompt, user_prompt,
            model=model, max_tokens=max_tokens, json_mode=True,
        )
        return self.parse_json_response(raw)

    async def _call_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        """Call Anthropic API (Claude)."""
        import anthropic

        if model is None:
            model = "claude-haiku-4-5-20251001"

        client = anthropic.AsyncAnthropic()
        message = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    async def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> str:
        """Call OpenAI API."""
        from openai import AsyncOpenAI

        if model is None:
            model = "gpt-4o-mini"

        client = AsyncOpenAI()
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    # ---- JSON parsing utilities ----

    @staticmethod
    def parse_json_response(raw: str) -> dict:
        """Parse a JSON response from the LLM, handling markdown fences.

        Args:
            raw: Raw LLM response text.

        Returns:
            Parsed dict.

        Raises:
            ValueError: If JSON cannot be extracted.
        """
        cleaned = raw.strip()

        # Strip markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to extract JSON object from response
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Could not parse LLM response as JSON: {e}")

    # ---- Timing utility ----

    @staticmethod
    def timer():
        """Return a simple timer context for measuring duration.

        Usage:
            start = time.time()
            ... do work ...
            duration = time.time() - start
        """
        return time.time()
