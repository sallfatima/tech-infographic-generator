# tech-infographic-generator — CLAUDE.md

## Projet
Générateur automatisé d'infographies techniques dans le style des meilleures newsletters data/AI.
Input : description textuelle → Output : image PNG (statique) ou GIF (animé).

## Sources d'inspiration et références visuelles

### Créateurs de référence
Les infographies que ce projet cherche à automatiser viennent de 2 créateurs principaux :

**SwirlAI Newsletter — Aurimas Griciūnas** (@Aurimas_Gr)
- Site : https://www.newsletter.swirlai.com/
- LinkedIn : https://linkedin.com/in/aurimas-griciunas
- Style signature : bordures dashed bleues, flèches courbes, icônes dessinées à la main,
  fond blanc, zones imbriquées avec titre sur la bordure, numéros cerclés ①②③
- Sujets : Kubernetes, Kafka, Spark, AI Agents, MLOps, Data Engineering
- Caractéristique unique : chaque concept est dessiné manuellement avec un style "whiteboard"
  organique, pas de grille rigide

**ByteByteGo — Alex Xu**
- Site : https://bytebytego.com/
- Newsletter : https://blog.bytebytego.com/
- GitHub : https://github.com/alex-xu-system/bytebytego
- Twitter : @alexxubyte
- Style signature : diagrammes animés avec fond blanc ou bleu clair, composants
  en rectangles arrondis colorés (jaune=client, vert=server, bleu=database),
  flèches numérotées ①②③ montrant le flux de données, style clean et minimaliste,
  labels sur chaque flèche, légende claire
- Sujets : System Design (URL shortener, rate limiter, chat system, YouTube, etc.),
  distributed systems, API design, database internals
- Caractéristique unique : approche "visual-first" — chaque concept complexe (HTTPS,
  OAuth, message queues) est expliqué en UN SEUL diagramme lisible en 30 secondes.
  Plus de 1M d'abonnés. Animations GIF avec apparition progressive des composants.

**DailyDoseofDS — Avi Chawla**
- Site : https://www.dailydoseofds.com/ et https://blog.dailydoseofds.com/
- MCP : https://mcp.dailydoseofds.com/
- Référence article : https://www.dailydoseofds.com/where-did-the-assumptions-of-linear-regression-originate-from/
- Style signature : sections horizontales empilées, icônes colorées avec fond,
  bordures douces, palette pastel (vert menthe, bleu clair, orange, violet),
  titres dans des pills colorés, personnages cartoon (dev avec laptop)
- Sujets : LLM Training, RAG Architectures, LLM Parameters, Fine-tuning, AI Engineering Roadmap
- Caractéristique unique : multi-sous-diagrammes dans une même image (ex: "8 RAG Architectures"
  avec 8 mini-diagrammes dans une grille 3×3)

### Familles visuelles identifiées (18 images de référence analysées)

**Famille A : Architecture technique complexe** (K8s, MCP, Spark, SFT/RFT)
- Zones imbriquées : rectangle dans rectangle (K8s Control Plane contient kube-apiserver, etc.)
- Flèches courbes dashed multicolores (bleu, violet, vert, rouge)
- Icônes réalistes (logos Kubernetes, Docker, Deepseek)
- Numéros cerclés ①②③④⑤⑥ indiquant l'ordre des opérations
- Légende box expliquant la signification des symboles
- Labels italiques sur les flèches
- Densité élevée : 15-25 éléments visibles
- Exemples : K8s for ML/DE (SwirlAI), MCP/A2A, SFT vs RFT (DailyDoseofDS)

**Famille B : Sections empilées / Catégories** (LLM Training, Compression, Parameters)
- Sections horizontales empilées avec titre centré sur la bordure
- Couleurs par section (vert/bleu/orange/violet)
- Icônes larges avec fond coloré circulaire
- Pas de flèches entre sections — l'empilement vertical EST le flux
- Texte varié : titres gras, descriptions, labels colorés
- Exemples : 4 Stages of LLM Training, ML Model Compression, 7 LLM Parameters (DailyDoseofDS)

**Famille C : Workflow / Agents** (Agentic patterns, Research Analyst, CrewAI)
- Multiple sous-diagrammes dans une même image
- Zones rectangulaires simples (bordure, pas de fill)
- Icônes style hand-drawn (cerveau, personne verte, laptop)
- Flèches dashed noires avec labels "In"/"Out"/"Pass"/"Fail"
- Légende en bas (🧠 = LLM Call, [Text] = Application logic)
- Style minimaliste noir/blanc avec accents bleu et rose
- Exemples : Workflow Patterns in Agentic Systems (SwirlAI), Agent roles, Research Analyst

**Famille D : Hub central / Concept map** (AI Agents Course, LangChain, Roadmaps)
- Hub central avec connections radiales
- Nodes dashed colorés disposés en cercle autour du centre
- Icônes colorées dans chaque node
- Flèches bidirectionnelles centre→périphérie
- Fond blanc ou fond coloré plein
- Exemples : AI Agents Course, Ollama/LangChain, AI Engineering Roadmap (DailyDoseofDS)

**Famille E : Learning Roadmap / Grid catégorisée** (AI Highlights dark, Roadmap)
- Lignes de catégories avec icône à gauche et éléments à droite
- Icônes larges colorées avec fond (style app icons)
- Dark theme avec textes néon (cyan, violet, orange)
- Grille structurée mais organique
- Exemples : AI Highlights dark theme, AI Engineering Learning Roadmap (DailyDoseofDS)

**Famille F : System Design clean (ByteByteGo)**
- Fond blanc ou bleu très clair, ultra-clean et minimaliste
- Composants en rectangles arrondis colorés par rôle :
  jaune=client, vert=server, bleu=database, orange=cache, rose=queue
- Flèches droites ou courbes, TOUJOURS numérotées ①②③④⑤
- Label descriptif sur CHAQUE flèche ("1. Send request", "2. Check cache")
- Flux lisible en 30 secondes, gauche→droite ou haut→bas
- Pas de zones imbriquées — layout plat et aéré
- Animation GIF : composants apparaissent un par un
- Exemples : "How HTTPS works", "Rate Limiter", "Chat System"
- Site : https://bytebytego.com/

### Plateformes et outils de création d'infographies (pour référence)

**Outils de diagrammes programmatiques (ce que fait notre projet)**
- Mermaid.js : diagrammes en texte → SVG (flowchart, sequence, gantt). Limité en style visuel.
  Site : https://mermaid.js.org/
- D2 : langage déclaratif pour diagrammes. Plus joli que Mermaid mais moins répandu.
  Site : https://d2lang.com/
- Graphviz/DOT : le classique pour les graphs. Layout automatique mais style austère.
- PlantUML : UML et architecture diagrams en texte.
- Diagrams (Python) : Infrastructure as Diagram. Icônes cloud (AWS, GCP, Azure).
  Site : https://diagrams.mingrammer.com/

**Outils de design visuel (ce dont on s'inspire)**
- Figma : design collaboratif, utilisé par SwirlAI pour ses infographies hand-drawn.
  Site : https://www.figma.com/
- Canva : templates d'infographies drag-and-drop. Bon pour les non-designers.
  Site : https://www.canva.com/
- Excalidraw : whiteboard collaboratif style hand-drawn. Très proche du style SwirlAI.
  Site : https://excalidraw.com/
- tldraw : similaire à Excalidraw, open source.
  Site : https://www.tldraw.com/

**Plateformes d'infographies spécialisées**
- Venngage : templates infographies business. https://venngage.com/
- Piktochart : infographies pour reports et présentations. https://piktochart.com/
- Visme : infographies interactives. https://www.visme.co/
- Infogram : data visualization et infographies. https://infogram.com/

**Ce qui nous différencie de ces outils**
Notre projet est le seul qui combine :
1. Input texte brut (pas de drag-and-drop, pas de template à remplir)
2. LLM pour comprendre le contenu et choisir le layout automatiquement
3. Rendu PIL/Python style SwirlAI/DailyDoseofDS (pas du SVG générique)
4. Animation GIF en bonus
5. 100% programmatique (intégrable dans un pipeline CI/CD)

## Architecture du projet
```
src/
  analyzer/prompts.py     — Prompt LLM pour parser le texte → InfographicData
  models/infographic.py   — Pydantic models (Node, Connection, StageGroup, InfographicData)
  renderer/
    engine.py             — Dispatcher: type → renderer, theme → fonction
    themes.py             — 3 themes: whiteboard, guidebook, dark
    icons.py              — SVG loading, tinting, pasting
    arrows.py             — Manhattan routing, dashed lines, arrowheads, labels
    shapes.py             — Rectangles, circles, cylinders, section boxes, nodes
    layout.py             — Grid, layered, radial, flow layouts
    renderers/
      pipeline.py         — Pipeline diagrams (HAS stage_groups support)
      architecture.py     — Architecture diagrams (layered) → Famille A
      multi_agent.py      — Multi-agent systems (radial) → Famille C/D
      rag_pipeline.py     — RAG pipelines (2-zone vertical) → Famille A
      flowchart.py        — Flowcharts (flow layout) → Famille C
      process.py          — Process diagrams (step-by-step) → Famille B
      concept_map.py      — Concept maps (radial) → Famille D
      comparison.py       — Side-by-side comparisons → Famille B
      infographic.py      — General infographics → Famille E
assets/icons/             — 30+ SVG icons (brain, database, api, container, etc.)
```

## Style visuel cible
- Bordures dashed colorées (rectangles arrondis)
- Flèches courbes dashed avec labels italiques
- Icônes dans cercles colorés (blanc sur fond de couleur)
- Numéros cerclés ①②③ le long du flux
- Zones de regroupement colorées avec titres SUR la bordure
- Zéro chevauchement de texte/rectangles
- Fond blanc avec outer border dashed bleu
- Palette : bleu #2B7DE9, orange #E8833A, vert #4CAF50, rouge #E53935, violet #9C27B0, cyan #00ACC1
- Style DailyDoseofDS : personnages cartoon, pills colorés, sections pastel, multi-diagrammes

## Ce qui est DÉJÀ FAIT (ne pas refaire)
- StageGroup model et stage_groups field dans infographic.py
- _render_whiteboard_grouped() dans pipeline.py (layout vertical groupé)
- _render_whiteboard_auto_grouped() dans pipeline.py (auto-groupement)
- _render_whiteboard_horizontal() dans pipeline.py (fallback ≤6 nodes)
- Hauteur adaptive dans pipeline.py
- Prompt LLM pour stage grouping dans prompts.py
- draw_section_box() avec titre sur bordure (shapes.py)
- draw_step_number() pour numéros cerclés (shapes.py)
- draw_dashed_rect() avec coins arrondis (shapes.py)
- _draw_label_on_path() pour labels sur flèches (arrows.py)
- draw_manhattan_arrow() et draw_straight_arrow() (arrows.py)
- paste_icon() et load_icon() avec tinting SVG (icons.py)

## Plan d'implémentation — 4 phases

### PHASE 1 : Briques visuelles (PRIORITÉ ABSOLUE)
Ordre strict : 1 → 2 → 3, tester après chaque fichier.

#### 1. icons.py — draw_icon_with_bg()
Ajouter ~40 lignes. Cercle coloré derrière icône SVG blanche.
Impact : immédiat sur TOUTES les familles visuelles.

#### 2. arrows.py — draw_bezier_arrow()
Ajouter ~90 lignes. Courbe quadratique bézier dashed avec arrowhead et label.
Impact : transforme le look de Famille A et C (architecture + workflow).
IMPORTANT : direction de courbure DÉTERMINISTE via hash(), PAS random().

#### 3. themes.py — Enrichir whiteboard
Ajouter use_bezier_arrows, use_icon_backgrounds, 8 section_colors au lieu de 6.

### PHASE 2 : Layout + zones imbriquées
#### 4. layout.py — layout_zone_grid() + resolve_overlaps()
PAS de force-directed — placement déterministe par zones.
Impact : Famille A (architecture technique), Famille D (concept map).

#### 5. shapes.py — draw_nested_zone()
Zones dans zones, style K8s Control Plane.

### PHASE 3 : Intégration renderers (UN PAR UN)
Ordre : pipeline.py → multi_agent.py → architecture.py → les 6 autres.
Pour chaque renderer : icon_with_bg + bezier arrows + resolve_overlaps.

### PHASE 4 : Prompt LLM
Enrichir prompts.py : curved_arrow, labels, zones, variété shapes.

## Règles NON-NÉGOCIABLES
- JAMAIS modifier plus de 2 fichiers simultanément
- Après chaque modif : `python -c "import src.renderer"` pour vérifier
- Après chaque renderer : générer image test + VÉRIFIER visuellement
- Layouts DÉTERMINISTES (même input = même output)
- PAS de random() — utiliser hash() pour alternatives
- PAS de force-directed (instable pour 4-8 nodes)
- Backward compat : anciens InfographicData marchent toujours
- Themes guidebook/dark ne sont PAS modifiés

## Fonctions existantes à réutiliser (ne pas recréer)
```
shapes.py   : draw_rounded_rect, draw_circle, draw_diamond, draw_cylinder,
              draw_hexagon, draw_cloud, draw_dashed_rect, draw_section_box,
              draw_step_number, draw_outer_border, draw_node_with_header,
              draw_numbered_badge, draw_node
arrows.py   : _draw_arrowhead, _draw_polyline, _draw_dashed_line,
              _manhattan_route, draw_manhattan_arrow, draw_straight_arrow,
              draw_bidirectional_arrow, _draw_label_on_path,
              draw_numbered_arrow, draw_connection
icons.py    : load_icon, _tint_svg, _create_fallback_icon, paste_icon
layout.py   : layout_layered, layout_flow_horizontal, layout_flow_vertical,
              layout_grid, layout_columns, layout_radial,
              get_node_center, get_node_edge, get_node_bottom, get_node_top
themes.py   : get_theme, hex_to_rgb, list_themes
```

## Commandes utiles
```bash
python -c "from src.renderer.engine import render_infographic; print('OK')"
python test_all_renderers.py
```