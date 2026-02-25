"""POST /api/analyze — Analyse texte brut → InfographicData JSON via LLM."""

import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..analyzer.llm_analyzer import LLMAnalyzer

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Corps de la requête /api/analyze."""
    text: str
    infographic_type: str | None = None


class AnalyzeResponse(BaseModel):
    """Réponse /api/analyze — InfographicData sérialisée + temps."""
    data: dict
    analysis_time: float


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """Analyse du texte brut via LLM → retourne InfographicData JSON.

    Le frontend React utilise ce JSON pour afficher la preview SVG (Rough.js).
    """
    start = time.time()
    try:
        analyzer = LLMAnalyzer()
        data = await analyzer.analyze(request.text, request.infographic_type)
        elapsed = time.time() - start

        return AnalyzeResponse(
            data=data.model_dump(),
            analysis_time=round(elapsed, 2),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
