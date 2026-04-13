"""Enrich CFA France homepage events with inferred speaker/highlights and localize to UI language."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI

from src.events_sync import EventsPayload


@dataclass
class DisplayEvent:
    title: str
    schedule: str
    location: str
    speaker: str
    highlights: List[str]
    source_url: str


@dataclass
class DisplayUpdate:
    title: str
    summary: str
    source_url: str


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _payload_fingerprint(payload: EventsPayload) -> str:
    parts = [payload.synced_at, payload.source_url]
    for e in payload.events:
        parts.extend([e.title, e.schedule, e.location])
    for u in payload.updates:
        parts.extend([u.title, u.summary])
    return "|".join(parts)


def enrich_and_localize(
    payload: EventsPayload,
    lang: str,
    client: OpenAI,
    model: str = "gpt-4o-mini",
) -> tuple[List[DisplayEvent], List[DisplayUpdate]]:
    """Use LLM to translate + add speaker (or TBC) and bullet highlights for each event."""
    lang_name = {"en": "English", "fr": "French", "zh": "Simplified Chinese"}.get(lang, "English")

    raw_events = [
        {"title": e.title, "schedule": e.schedule, "location": e.location, "source_url": e.source_url}
        for e in payload.events
    ]
    raw_updates = [{"title": u.title, "summary": u.summary, "source_url": u.source_url} for u in payload.updates]

    user_payload = {"events": raw_events, "updates": raw_updates}

    system = f"""You enrich CFA Society France homepage listings for a multilingual UI.
Source text is mostly English from the official site.
Output valid JSON only, no markdown fences.

Rules:
1. Translate ALL user-facing strings into {lang_name} when lang is not English; if lang is English, keep natural English.
2. For each event, provide:
   - title: localized title
   - schedule: localized line (keep times accurate; translate month/day labels if appropriate)
   - location: localized place names when natural (e.g. Paris stays Paris in French; use 巴黎 for Chinese if you localize)
   - speaker: if the source does NOT name speakers, use a clear localized phrase meaning "Not listed on homepage" — do NOT invent real person names.
   - highlights: exactly 3 short bullet strings (themes inferred only from title/schedule/location). Prefix mentally with "typical focus:" — no fabricated facts.
3. For each update: localized title and summary.
4. Preserve source_url unchanged.
5. JSON shape: {{"events":[...],"updates":[...]}}
Each event object keys: title, schedule, location, speaker, highlights (array of 3 strings), source_url
Each update object keys: title, summary, source_url
"""

    user = json.dumps(user_payload, ensure_ascii=False)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=2500,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        content = _strip_json_fence(content)
        data = json.loads(content)
        if isinstance(data, dict) and "events" not in data and "updates" not in data and len(data) == 1:
            inner = next(iter(data.values()))
            if isinstance(inner, dict):
                data = inner
        if not isinstance(data, dict):
            raise ValueError("Invalid JSON shape")
    except Exception:
        return fallback_display(payload, lang)

    events_out: List[DisplayEvent] = []
    for item in data.get("events", []):
        try:
            events_out.append(
                DisplayEvent(
                    title=str(item.get("title", "")),
                    schedule=str(item.get("schedule", "")),
                    location=str(item.get("location", "")),
                    speaker=str(item.get("speaker", "")),
                    highlights=[str(h) for h in item.get("highlights", [])][:4],
                    source_url=str(item.get("source_url", payload.source_url)),
                )
            )
        except Exception:
            continue

    updates_out: List[DisplayUpdate] = []
    for item in data.get("updates", []):
        try:
            updates_out.append(
                DisplayUpdate(
                    title=str(item.get("title", "")),
                    summary=str(item.get("summary", "")),
                    source_url=str(item.get("source_url", payload.source_url)),
                )
            )
        except Exception:
            continue

    if not events_out and not updates_out:
        return fallback_display(payload, lang)

    return events_out, updates_out


def fallback_display(payload: EventsPayload, lang: str) -> tuple[List[DisplayEvent], List[DisplayUpdate]]:
    """If LLM fails, show raw scraped strings (English) as display fields."""
    events = [
        DisplayEvent(
            title=e.title,
            schedule=e.schedule,
            location=e.location,
            speaker="—",
            highlights=[],
            source_url=e.source_url,
        )
        for e in payload.events
    ]
    updates = [DisplayUpdate(title=u.title, summary=u.summary, source_url=u.source_url) for u in payload.updates]
    return events, updates


def fingerprint_for_cache(payload: EventsPayload) -> str:
    return _payload_fingerprint(payload)
