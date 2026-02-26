"""Render-time content compaction presets for cleaner infographic outputs."""

from __future__ import annotations

import re

from ..models.infographic import InfographicData, InfographicType


def list_render_presets() -> list[str]:
    """Return supported render preset names."""
    return ["reference_clean"]


def apply_render_preset(
    data: InfographicData,
    preset: str | None,
    *,
    for_gif: bool = False,
) -> InfographicData:
    """Apply an optional render preset to reduce visual density before rendering.

    The preset works on a deep copy, so callers can safely pass the original model.
    """
    if not preset:
        return data

    name = preset.strip().lower()
    if name in {"none", "default"}:
        return data
    if name in {"reference_clean", "reference", "clean", "compact"}:
        return _apply_reference_clean(data, for_gif=for_gif)

    raise ValueError(
        f"Unknown render_preset '{preset}'. Supported presets: {', '.join(list_render_presets())}"
    )


def _apply_reference_clean(data: InfographicData, *, for_gif: bool) -> InfographicData:
    out = data.model_copy(deep=True)

    cfg = _type_config(out.type)
    out.title = _compact_title(out.title, cfg["title_max"])
    if out.subtitle:
        out.subtitle = _compact_text(out.subtitle, cfg["subtitle_max"], max_words=14)
    if out.footer:
        out.footer = _compact_text(out.footer, 90, max_words=16)

    # Limit nodes globally (and per layer for architecture-like layouts).
    kept_ids = _limit_nodes(out, cfg)

    # Filter / trim connections
    max_connections = cfg.get("max_connections", 12)
    filtered_connections = []
    for conn in out.connections:
        if conn.from_node not in kept_ids or conn.to_node not in kept_ids:
            continue
        if for_gif:
            conn.label = None  # cleaner animated flow
        elif conn.label:
            conn.label = _compact_text(conn.label, cfg["conn_label_max"], max_words=3)
        filtered_connections.append(conn)
        if len(filtered_connections) >= max_connections:
            break
    out.connections = filtered_connections

    # Compact node text
    for node in out.nodes:
        node.label = _compact_label(node.label, cfg["label_max"], cfg["label_words"])
        if node.description:
            node.description = _compact_description(
                node.description,
                max_chars=cfg["desc_max"],
                max_words=cfg["desc_words"],
                max_sentences=1 if for_gif else cfg["desc_sentences"],
            )
        if node.group:
            node.group = _compact_text(node.group, 20, max_words=3)
        if node.zone:
            node.zone = _compact_text(node.zone, 20, max_words=3)

    # Compact layer / zone names after filtering
    for layer in out.layers:
        layer.name = _compact_text(layer.name, 20, max_words=3)
    for zone in out.zones:
        if isinstance(zone, dict) and "name" in zone and isinstance(zone["name"], str):
            zone["name"] = _compact_text(zone["name"], 20, max_words=3)

    out.metadata = dict(out.metadata or {})
    out.metadata["render_preset"] = "reference_clean"
    if for_gif:
        out.metadata["gif_optimized"] = True
    return out


def _type_config(kind: InfographicType) -> dict:
    base = {
        "title_max": 58,
        "subtitle_max": 90,
        "label_max": 18,
        "label_words": 4,
        "desc_max": 84,
        "desc_words": 14,
        "desc_sentences": 2,
        "conn_label_max": 14,
        "max_nodes": 8,
        "max_connections": 12,
        "max_layers": 4,
        "max_nodes_per_layer": 4,
    }

    if kind in {InfographicType.FLOWCHART, InfographicType.PIPELINE, InfographicType.RAG_PIPELINE}:
        return {
            **base,
            "label_max": 16,
            "label_words": 3,
            "desc_max": 66,
            "desc_words": 10,
            "desc_sentences": 1,
            "conn_label_max": 10,
            "max_nodes": 7,
            "max_connections": 10,
        }
    if kind in {InfographicType.PROCESS, InfographicType.TIMELINE}:
        return {
            **base,
            "label_max": 18,
            "label_words": 4,
            "desc_max": 72,
            "desc_words": 11,
            "desc_sentences": 1,
            "max_nodes": 8,
        }
    if kind in {InfographicType.ARCHITECTURE, InfographicType.MULTI_AGENT}:
        return {
            **base,
            "label_max": 17,
            "label_words": 3,
            "desc_max": 62,
            "desc_words": 9,
            "desc_sentences": 1,
            "conn_label_max": 10,
            "max_nodes": 10,
            "max_connections": 14,
            "max_layers": 4,
            "max_nodes_per_layer": 4,
        }
    if kind == InfographicType.CONCEPT_MAP:
        return {
            **base,
            "label_max": 18,
            "label_words": 3,
            "desc_max": 58,
            "desc_words": 9,
            "desc_sentences": 1,
            "max_nodes": 7,
            "max_connections": 10,
        }
    if kind == InfographicType.COMPARISON:
        return {
            **base,
            "label_max": 18,
            "label_words": 3,
            "desc_max": 60,
            "desc_words": 9,
            "desc_sentences": 1,
            "max_nodes": 8,
            "max_connections": 2,
        }
    return base


def _limit_nodes(data: InfographicData, cfg: dict) -> set[str]:
    """Limit nodes while keeping layer/zone references consistent."""
    max_nodes = cfg.get("max_nodes", len(data.nodes))
    max_layers = cfg.get("max_layers", len(data.layers))
    max_nodes_per_layer = cfg.get("max_nodes_per_layer", 99)

    # Limit layers first when present (architecture-like diagrams)
    if data.layers:
        data.layers = data.layers[:max_layers]
        ordered_ids: list[str] = []
        for layer in data.layers:
            layer.nodes = layer.nodes[:max_nodes_per_layer]
            for nid in layer.nodes:
                if nid not in ordered_ids:
                    ordered_ids.append(nid)
        # Include nodes not referenced by layers at the end (rare, but preserve).
        for node in data.nodes:
            if node.id not in ordered_ids:
                ordered_ids.append(node.id)
        ordered_ids = ordered_ids[:max_nodes]
        allowed = set(ordered_ids)
        for layer in data.layers:
            layer.nodes = [nid for nid in layer.nodes if nid in allowed]
        data.layers = [layer for layer in data.layers if layer.nodes]
    else:
        ordered_ids = [node.id for node in data.nodes[:max_nodes]]
        allowed = set(ordered_ids)

    data.nodes = [node for node in data.nodes if node.id in allowed]

    # Keep node order aligned with chosen IDs.
    order_idx = {nid: i for i, nid in enumerate(ordered_ids)}
    data.nodes.sort(key=lambda n: order_idx.get(n.id, 9999))

    # Filter zones if present
    filtered_zones = []
    for zone in data.zones:
        if not isinstance(zone, dict):
            continue
        zone_nodes = [nid for nid in zone.get("nodes", []) if nid in allowed]
        if not zone_nodes:
            continue
        z = dict(zone)
        z["nodes"] = zone_nodes[:max_nodes_per_layer]
        filtered_zones.append(z)
    data.zones = filtered_zones[:max_layers]

    return allowed


def _compact_title(text: str, max_chars: int) -> str:
    text = _normalize_whitespace(text)
    # Prefer a meaningful prefix before separators.
    for sep in (" - ", " | ", ": "):
        if sep in text:
            left = text.split(sep, 1)[0].strip()
            if 6 <= len(left) <= max_chars:
                return left
    return _truncate_chars(text, max_chars)


def _compact_label(text: str, max_chars: int, max_words: int) -> str:
    text = _normalize_whitespace(text)
    text = re.sub(r"^\d+[\).\-\s]+", "", text).strip()
    text = _truncate_words(text, max_words)
    return _truncate_chars(text, max_chars)


def _compact_description(
    text: str,
    *,
    max_chars: int,
    max_words: int,
    max_sentences: int,
) -> str:
    text = _normalize_whitespace(text)
    text = re.sub(r"^[\-\*\u2022]\s*", "", text)
    # Prefer the first sentence(s) and cut enumerations.
    parts = re.split(r"(?<=[.!?;])\s+|\s+[>\u2192]\s+|\s+\|\s+", text)
    parts = [p.strip() for p in parts if p.strip()]
    if parts:
        text = " ".join(parts[:max_sentences])
    text = _truncate_words(text, max_words)
    return _truncate_chars(text, max_chars)


def _compact_text(text: str, max_chars: int, max_words: int) -> str:
    return _truncate_chars(_truncate_words(_normalize_whitespace(text), max_words), max_chars)


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _truncate_chars(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[: max_chars - 3].rstrip(" ,;:-") + "..."
