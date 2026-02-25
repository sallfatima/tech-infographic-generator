"""Serper.dev API client for Google Image Search.

Serper.dev provides a simple REST API for Google Search results.
Free tier: 2500 requests/month.

Usage:
    client = SerperClient()
    results = await client.search_images("RAG pipeline infographic")
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import httpx


SERPER_API_URL = "https://google.serper.dev/images"
SERPER_TIMEOUT = 10.0  # seconds


@dataclass
class SerperImageResult:
    """A single image result from Serper."""

    title: str = ""
    image_url: str = ""
    source: str = ""
    link: str = ""
    width: int = 0
    height: int = 0


@dataclass
class SerperSearchResponse:
    """Response from a Serper image search."""

    query: str = ""
    images: list[SerperImageResult] = field(default_factory=list)
    raw_response: dict = field(default_factory=dict)
    error: str = ""


class SerperClient:
    """Client for Serper.dev Google Image Search API.

    Requires SERPER_API_KEY environment variable.
    """

    def __init__(self, api_key: str | None = None):
        """Initialize the client.

        Args:
            api_key: Serper API key. Falls back to SERPER_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("SERPER_API_KEY", "")
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """Check if the API key is set."""
        return bool(self.api_key)

    async def search_images(
        self,
        query: str,
        num_results: int = 5,
        country: str = "us",
    ) -> SerperSearchResponse:
        """Search Google Images via Serper.dev.

        Args:
            query: Search query string.
            num_results: Number of results to return (max 10).
            country: Country code for localized results.

        Returns:
            SerperSearchResponse with image results.
        """
        if not self.is_configured:
            return SerperSearchResponse(
                query=query,
                error="SERPER_API_KEY not configured"
            )

        try:
            async with httpx.AsyncClient(timeout=SERPER_TIMEOUT) as client:
                response = await client.post(
                    SERPER_API_URL,
                    headers={
                        "X-API-KEY": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "q": query,
                        "num": min(num_results, 10),
                        "gl": country,
                    },
                )

                if response.status_code != 200:
                    return SerperSearchResponse(
                        query=query,
                        error=f"Serper API error: {response.status_code} - {response.text[:200]}",
                    )

                data = response.json()
                images = []

                for item in data.get("images", [])[:num_results]:
                    images.append(SerperImageResult(
                        title=item.get("title", ""),
                        image_url=item.get("imageUrl", ""),
                        source=item.get("source", ""),
                        link=item.get("link", ""),
                        width=item.get("imageWidth", 0),
                        height=item.get("imageHeight", 0),
                    ))

                return SerperSearchResponse(
                    query=query,
                    images=images,
                    raw_response=data,
                )

        except httpx.TimeoutException:
            return SerperSearchResponse(
                query=query,
                error=f"Serper API timeout after {SERPER_TIMEOUT}s",
            )
        except Exception as e:
            return SerperSearchResponse(
                query=query,
                error=f"Serper API error: {str(e)}",
            )

    async def multi_search(
        self,
        queries: list[str],
        num_results_per_query: int = 3,
    ) -> list[SerperSearchResponse]:
        """Run multiple image searches.

        Args:
            queries: List of search queries.
            num_results_per_query: Results per query.

        Returns:
            List of SerperSearchResponse, one per query.
        """
        import asyncio

        tasks = [
            self.search_images(q, num_results=num_results_per_query)
            for q in queries
        ]
        return await asyncio.gather(*tasks)
