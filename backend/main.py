"""FastAPI entry point — Tech Infographic Generator Backend.

Point d'entrée principal du backend.
Lance avec : cd backend && uvicorn main:app --reload --port 8000

Routes :
  GET  /api/health          → Healthcheck
  GET  /api/themes          → Liste des thèmes disponibles
  POST /api/analyze          → Texte brut → InfographicData JSON (via LLM)
  POST /api/export/png       → InfographicData JSON → PNG haute qualité (via PIL)
  POST /api/export/gif       → InfographicData JSON → GIF animé (via PIL)
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Charger les variables d'environnement depuis .env (racine du projet)
project_root = str(Path(__file__).parent.parent)
load_dotenv(Path(project_root) / ".env")

# Assure que le parent de backend/ est dans sys.path
# pour que les imports `backend.xxx` fonctionnent quand lancé depuis backend/
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi.staticfiles import StaticFiles

from backend.api.analyze import router as analyze_router
from backend.api.export import router as export_router
from backend.api.generate import router as generate_router
from backend.renderer.themes import THEMES

# Dossier de sortie pour les images generees (partage avec generate.py)
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Tech Infographic Generator",
    description="Génère des infographies techniques style SwirlAI/ByteByteGo à partir de texte brut.",
    version="2.0",
)

# CORS — autorise le frontend React (Vite dev server sur :5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Enregistre les routers API
app.include_router(analyze_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(generate_router, prefix="/api")

# Servir les images generees (PNG/GIF) depuis /output/
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


@app.get("/api/health")
async def health():
    """Healthcheck endpoint."""
    return {"status": "ok", "version": "2.0"}


@app.get("/api/themes")
async def get_themes():
    """Retourne la liste des thèmes disponibles avec leurs couleurs.

    Utilisé par le frontend pour afficher le sélecteur de thème.
    """
    return {
        name: {
            "name": t["name"],
            "bg": t["bg"],
            "accent": t["accent"],
            "accent2": t["accent2"],
        }
        for name, t in THEMES.items()
    }
