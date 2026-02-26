# tech-infographic-generator — CLAUDE.md

## Règles Git — OBLIGATOIRE
- **Ne JAMAIS ajouter** `Co-Authored-By: Claude` ou toute mention de Claude dans les messages de commit
- Les commits appartiennent uniquement à `sallfatima`

## Projet
Générateur automatisé d'infographies techniques dans le style des meilleures newsletters data/AI.
Input : description textuelle → Output : infographie interactive (React) + export PNG/GIF (Python PIL).

**Architecture : React frontend + Python FastAPI backend.**

## Repo Git
https://github.com/sallfatima/tech-infographic-generator.git

## Sources d'inspiration et références visuelles

### Créateurs de référence

**SwirlAI Newsletter — Aurimas Griciūnas** (@Aurimas_Gr)
- Site : https://www.newsletter.swirlai.com/
- LinkedIn : https://linkedin.com/in/aurimas-griciunas
- Style signature : bordures dashed bleues, flèches courbes, icônes dessinées à la main,
  fond blanc, zones imbriquées avec titre sur la bordure, numéros cerclés ①②③
- Sujets : Kubernetes, Kafka, Spark, AI Agents, MLOps, Data Engineering

**ByteByteGo — Alex Xu**
- Site : https://bytebytego.com/
- Newsletter : https://blog.bytebytego.com/
- GitHub : https://github.com/alex-xu-system/bytebytego
- Style signature : rectangles arrondis colorés (jaune=client, vert=server, bleu=database),
  flèches numérotées ①②③ montrant le flux de données, animations GIF progressives
- Sujets : System Design, distributed systems, API design, database internals

**DailyDoseofDS — Avi Chawla**
- Site : https://www.dailydoseofds.com/ et https://blog.dailydoseofds.com/
- MCP : https://mcp.dailydoseofds.com/
- Style signature : sections horizontales empilées, icônes colorées avec fond,
  palette pastel (vert menthe, bleu clair, orange, violet), pills colorés, personnages cartoon
- Sujets : LLM Training, RAG Architectures, LLM Parameters, Fine-tuning

### Outil de référence clé : Excalidraw
- Site : https://excalidraw.com/
- GitHub : https://github.com/excalidraw/excalidraw
- Premium : https://plus.excalidraw.com/
- L'outil le plus proche visuellement de SwirlAI. Open source, React + TypeScript.
- Notre projet s'inspire de : roughness des traits, fills hachurés, flèches courbes avec labels
- Excalidraw utilise **Rough.js** (https://roughjs.com/) pour le style hand-drawn
  → NOUS AUSSI on utilise Rough.js dans notre frontend React
- Excalidraw a "Text to diagram" AI → nous faisons la même chose via LLM backend

### Familles visuelles identifiées (18 images de référence)

**Famille A : Architecture technique complexe** (K8s, MCP, Spark)
- Zones imbriquées, flèches courbes dashed multicolores, icônes réalistes
- Numéros cerclés ①②③, légende box, densité 15-25 éléments

**Famille B : Sections empilées** (LLM Training, Compression, Parameters)
- Sections horizontales avec titre sur bordure, couleurs par section
- Icônes larges avec fond coloré circulaire, pas de flèches entre sections

**Famille C : Workflow / Agents** (Agentic patterns, Research Analyst)
- Multiple sous-diagrammes, flèches dashed avec labels In/Out
- Style minimaliste noir/blanc avec accents bleu et rose

**Famille D : Hub central / Concept map** (AI Agents Course, LangChain)
- Hub central avec connections radiales, nodes dashed colorés en cercle

**Famille E : Grid catégorisée / Roadmap** (AI Highlights, Roadmaps)
- Lignes de catégories, icônes larges, dark theme avec textes néon

**Famille F : System Design clean** (ByteByteGo)
- Fond blanc ultra-clean, rectangles colorés par rôle, flèches numérotées

### Outils de création utilisés par ces créateurs

**Excalidraw** — Style whiteboard hand-drawn
- https://excalidraw.com/ | GitHub : https://github.com/excalidraw/excalidraw
- Utilisé par : **Dipankar Mazumdar** (Director Dev Advocacy @ Cloudera, data lakehouse),
  **SwirlAI** (Aurimas), et beaucoup d'autres créateurs tech
- Dipankar : https://www.linkedin.com/in/dipankar-mazumdar/ | @Dipankartnt
  "I rely on Excalidraw almost every single day. I have drawn hundreds of diagrams."
- Stack : React + TypeScript + **Rough.js** ← NOUS UTILISONS LA MÊME STACK
- Notre projet automatise ce que ces créateurs font manuellement dans Excalidraw

**Figma** — Infographies polies et carousels LinkedIn
- https://www.figma.com/
- Utilisé par : **ByteByteGo** (Alex Xu) pour ses system design diagrams animés,
  créateurs LinkedIn pour les carousels multi-slides professionnels
- Très poli, pixel-perfect, mais 100% manuel — pas de génération automatique

**Canva** — Roadmaps et cheat sheets colorés
- https://www.canva.com/
- Utilisé par : **DailyDoseofDS** (Avi Chawla) et de nombreux créateurs pour
  les roadmaps, cheat sheets, et infographies colorées avec templates
- Templates drag-and-drop, rapide pour les non-designers
- Limité en personnalisation technique (pas de zones imbriquées, pas de code)

**D2 / Mermaid** — Diagrammes d'architecture générés par code
- D2 : https://d2lang.com/ | Mermaid : https://mermaid.js.org/
- Utilisés par : développeurs, dans les docs techniques, README GitHub, Notion
- Texte → SVG automatique, intégrés dans GitHub et Notion
- Style générique, pas de style hand-drawn, pas de custom icons,
  pas d'animations — mais excellents pour la documentation technique

**Autres outils** : tldraw (https://www.tldraw.com/), Graphviz, PlantUML,
Diagrams Python (https://diagrams.mingrammer.com/), Venngage, Piktochart, Visme, Infogram

**Ce qui nous différencie de TOUS ces outils** :
Aucun ne combine : input texte brut + LLM auto + rendu hand-drawn interactif
(React/Rough.js) + export pixel-perfect (PIL) + animations Framer Motion +
100% programmatique. Excalidraw est le plus proche mais nécessite un travail
manuel. Mermaid/D2 sont auto mais le rendu est générique. Nous combinons les deux.

---

## Architecture du projet — React + Python

### Structure des dossiers
```
tech-infographic-generator/
├── CLAUDE.md
├── .claude/
│   └── analyse-visuelle.md
│
├── frontend/                          ← React + TypeScript + Vite
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── App.tsx                    ← Layout principal
│       ├── main.tsx                   ← Point d'entrée
│       ├── api/
│       │   └── client.ts             ← Appels FastAPI (/analyze, /export)
│       ├── components/
│       │   ├── Editor/
│       │   │   ├── TextInput.tsx      ← Zone de saisie texte brut
│       │   │   ├── Toolbar.tsx        ← Theme, layout, export
│       │   │   └── NodeEditor.tsx     ← Édition d'un node
│       │   ├── Diagram/
│       │   │   ├── DiagramCanvas.tsx  ← SVG container principal
│       │   │   ├── RoughNode.tsx      ← Node rendu avec Rough.js
│       │   │   ├── RoughEdge.tsx      ← Flèche/connection Rough.js
│       │   │   ├── ZoneBox.tsx        ← Zone dashed avec titre
│       │   │   ├── StepNumber.tsx     ← Numéros cerclés ①②③
│       │   │   ├── IconBadge.tsx      ← Icône SVG sur cercle coloré
│       │   │   └── LegendBox.tsx      ← Légende symboles
│       │   └── Export/
│       │       ├── ExportButton.tsx   ← PNG/SVG/GIF via backend
│       │       └── SharePanel.tsx     ← Lien partageable
│       ├── hooks/
│       │   ├── useAnalyze.ts         ← POST /api/analyze
│       │   ├── useDiagramState.ts    ← State InfographicData + édition
│       │   └── useExport.ts          ← POST /api/export
│       ├── lib/
│       │   ├── roughRenderer.ts      ← Wrapper Rough.js
│       │   ├── layoutEngine.ts       ← Layouts : zone-grid, radial, layered, flow
│       │   └── themes.ts             ← Themes : whiteboard, guidebook, dark
│       └── types/
│           └── infographic.ts        ← Types TS miroir des Pydantic models
│
├── backend/                           ← Python FastAPI
│   ├── main.py                        ← FastAPI app, CORS, routes
│   ├── requirements.txt
│   ├── api/
│   │   ├── analyze.py                ← POST /api/analyze
│   │   ├── export.py                 ← POST /api/export/png, /gif, /svg
│   │   └── templates.py             ← GET /api/templates
│   ├── analyzer/
│   │   └── prompts.py               ← Prompt LLM (EXISTANT, déplacé de src/)
│   ├── models/
│   │   └── infographic.py           ← Pydantic models (EXISTANT, déplacé de src/)
│   └── renderer/                     ← PIL renderers (EXISTANT, gardé pour export)
│       ├── engine.py
│       ├── themes.py
│       ├── icons.py
│       ├── arrows.py
│       ├── shapes.py
│       ├── layout.py
│       └── renderers/*.py           ← 9 renderers inchangés
│
└── assets/
    └── icons/                        ← SVG icons partagés (frontend + backend)
```

### Flux de données
```
1. User tape du texte ──→ React TextInput
2. React POST /api/analyze {text} ──→ FastAPI
3. FastAPI ──→ LLM (OpenAI/Anthropic) ──→ InfographicData JSON
4. React reçoit le JSON ──→ DiagramCanvas affiche preview SVG (Rough.js)
5. User interagit : drag-drop nodes, edit labels, change theme
6. User exporte ──→ React POST /api/export/png {infographicData}
7. FastAPI ──→ PIL renderer ──→ PNG/GIF haute qualité
8. User télécharge le fichier final
```

### Stack technique

**Frontend** : React 18+, TypeScript, Vite, Rough.js, Framer Motion, Zustand, Tailwind CSS, shadcn/ui, lucide-react
**Backend** : Python 3.11+, FastAPI, Pydantic, Pillow, uvicorn

### Pourquoi Rough.js
C'est LA librairie qui donne le style "dessiné à la main" d'Excalidraw.
```typescript
import rough from 'roughjs';
const rc = rough.svg(svgElement);
// Rectangle hand-drawn — remplace draw_dashed_rect() PIL (50 lignes → 3 lignes)
rc.rectangle(10, 10, 200, 100, {
  fill: '#E3F2FD', fillStyle: 'hachure',
  stroke: '#2B7DE9', strokeWidth: 2, roughness: 1.5
});
// Flèche bézier — remplace draw_bezier_arrow() PIL (90 lignes → 1 ligne)
rc.path('M 50,200 Q 150,50 250,200', { stroke: '#E8833A', roughness: 0.8 });
```

---

## Ce qui est DÉJÀ FAIT (ne pas refaire)

### Backend Python (code existant à déplacer dans backend/)
- StageGroup model et stage_groups field dans infographic.py
- _render_whiteboard_grouped() dans pipeline.py
- _render_whiteboard_auto_grouped() dans pipeline.py
- Prompt LLM pour stage grouping dans prompts.py
- draw_section_box(), draw_step_number(), draw_dashed_rect() (shapes.py)
- draw_manhattan_arrow(), draw_straight_arrow() (arrows.py)
- paste_icon() et load_icon() avec tinting SVG (icons.py)
- 9 renderers fonctionnels
- 3 themes (whiteboard, guidebook, dark)
- 30+ SVG icons

---

## Plan d'implémentation — 5 phases

### PHASE 0 : Restructurer le repo + FastAPI (1-2h)
Déplacer src/ → backend/. Créer FastAPI app avec /api/analyze et /api/export.

### PHASE 1 : React basique + rendu SVG (2-3h)
Vite + React + TypeScript. DiagramCanvas.tsx. TextInput.tsx. Appel /api/analyze.

### PHASE 2 : Rough.js + style hand-drawn (2-3h)
RoughNode.tsx, RoughEdge.tsx, ZoneBox.tsx, IconBadge.tsx, StepNumber.tsx.

### PHASE 3 : Interactivité (2-3h)
Drag-and-drop, édition inline, switch theme/layout, panneau propriétés.

### PHASE 4 : Animations + export (1-2h)
Framer Motion, export PNG/SVG/GIF, mode présentation.

### PHASE 5 : Polish + déploiement (1-2h)
Responsive, raccourcis clavier, Docker Compose, README.

---

## Règles NON-NÉGOCIABLES

### Architecture
- Frontend = React + TypeScript + Vite (PAS Next.js, PAS CRA)
- Backend = FastAPI (PAS Flask, PAS Django)
- Rough.js pour le rendu hand-drawn (PAS Canvas 2D, PAS d3)
- SVG pour le rendu frontend (PAS Canvas sauf exception)
- Zustand pour le state (PAS Redux, PAS Context API seul)
- Monorepo : frontend/ et backend/ dans le même repo

### Code
- TypeScript strict (pas de `any`)
- Types TS = miroir exact des Pydantic models
- PAS de localStorage/sessionStorage
- PAS de SSR — c'est une SPA
- Layouts DÉTERMINISTES (même input = même output)

### Process
- JAMAIS modifier plus de 3 fichiers simultanément
- Après chaque composant : `npm run build` pour vérifier
- Après chaque route FastAPI : tester avec curl
- Le backend PIL garde ses 9 renderers INTACTS
- Branches par phase, commits conventionnels, push origin

---

## Commandes utiles

```bash
# Backend
cd backend && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev    # :5173

# Test API
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Explain MLOps pipeline"}'
```