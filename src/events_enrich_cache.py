"""Disk cache for LLM-enriched / localized events (avoids repeat API calls on unchanged source data)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

CACHE_DIR = Path("data/events_enrich_cache")


def _snapshot_hash(snapshot: str) -> str:
    return hashlib.sha256(snapshot.encode("utf-8")).hexdigest()


def _cache_path(snapshot: str, lang: str) -> Path:
    short = _snapshot_hash(snapshot)[:20]
    safe_lang = lang.replace("/", "_")
    return CACHE_DIR / f"{short}_{safe_lang}.json"


def load_enriched_display(snapshot: str, lang: str, ttl_seconds: int) -> Optional[Dict[str, Any]]:
    path = _cache_path(snapshot, lang)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if raw.get("snapshot_sha256") != _snapshot_hash(snapshot):
        return None
    try:
        enriched_at = datetime.fromisoformat(raw["enriched_at"])
    except (KeyError, ValueError):
        return None
    age = (datetime.now(timezone.utc) - enriched_at).total_seconds()
    if age > ttl_seconds:
        return None
    events = raw.get("events")
    updates = raw.get("updates")
    if not isinstance(events, list) or not isinstance(updates, list):
        return None
    return {"events": events, "updates": updates}


def save_enriched_display(snapshot: str, lang: str, display_rows: Dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(snapshot, lang)
    payload = {
        "snapshot_sha256": _snapshot_hash(snapshot),
        "lang": lang,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "events": display_rows.get("events", []),
        "updates": display_rows.get("updates", []),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
