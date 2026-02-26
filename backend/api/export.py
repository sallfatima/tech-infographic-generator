"""POST /api/export/png et /api/export/gif — Export haute qualité via PIL."""

import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..models.infographic import InfographicData
from ..renderer.engine import ProRenderer
from ..renderer.animator import InfographicAnimator
from ..renderer.render_preset import apply_render_preset

router = APIRouter()


class ExportRequest(BaseModel):
    """Corps de la requête /api/export/*.

    infographic_data: le JSON InfographicData complet (issu de /api/analyze).
    theme: nom du thème ('whiteboard', 'guidebook', 'dark_modern').
    width/height: dimensions en pixels de l'export.
    """
    infographic_data: dict
    theme: str = "whiteboard"
    width: int = 1400
    height: int = 900
    render_preset: str | None = None


class ExportGifRequest(ExportRequest):
    """Paramètres supplémentaires pour l'export GIF."""
    frame_duration: int = 500


@router.post("/export/png")
async def export_png(request: ExportRequest):
    """Reçoit InfographicData JSON → retourne image PNG en streaming.

    Le frontend envoie le JSON qu'il a reçu de /api/analyze,
    le backend le rend en PNG haute qualité via PIL + le thème choisi.
    """
    try:
        data = InfographicData(**request.infographic_data)
        data = apply_render_preset(data, request.render_preset, for_gif=False)
        renderer = ProRenderer(request.theme)
        img = renderer.render_to_image(data, request.width, request.height)

        # Encode en PNG dans un buffer mémoire
        buf = io.BytesIO()
        img.save(buf, format="PNG", quality=95)
        buf.seek(0)

        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=infographic.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/gif")
async def export_gif(request: ExportGifRequest):
    """Reçoit InfographicData JSON → retourne GIF animé en streaming.

    Utilise InfographicAnimator pour générer l'animation progressive.
    """
    try:
        data = InfographicData(**request.infographic_data)
        data = apply_render_preset(data, request.render_preset, for_gif=True)
        animator = InfographicAnimator(request.theme)

        # generate_gif retourne un Path, on lit le fichier
        output_path = animator.generate_gif(
            data,
            width=request.width,
            height=request.height,
            frame_duration=request.frame_duration,
        )

        return StreamingResponse(
            open(str(output_path), "rb"),
            media_type="image/gif",
            headers={"Content-Disposition": "attachment; filename=infographic.gif"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/svg")
async def export_svg():
    """Placeholder pour l'export SVG (Phase 2 — React frontend).

    L'export SVG sera fait côté frontend car le rendu Rough.js est en SVG.
    Ce endpoint est réservé pour un usage futur si nécessaire.
    """
    raise HTTPException(
        status_code=501,
        detail="SVG export is handled client-side by the React frontend (Rough.js).",
    )
