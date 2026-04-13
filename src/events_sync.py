from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://www.cfasociety.org/france/home"
CACHE_PATH = Path("data/events_cache.json")

NOISE_LINES = {
    "Skip to main content (Press Enter).",
    "Skip auxiliary navigation (Press Enter).",
    "Skip main navigation (Press Enter).",
    "Quick Links",
    "Join Now",
    "Learn More",
    "Log in Now",
    "*Read More",
    "See More Events",
    "Toggle navigation",
    "®",
}
WEEKDAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
MONTHS = {
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
}
DATE_LINE_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}")


@dataclass
class UpdateItem:
    title: str
    summary: str
    source_url: str


@dataclass
class EventItem:
    title: str
    schedule: str
    location: str
    source_url: str


@dataclass
class EventsPayload:
    source_url: str
    synced_at: str
    updates: List[UpdateItem]
    events: List[EventItem]


def _extract_lines(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    raw_lines = [line.strip() for line in soup.get_text("\n", strip=True).splitlines()]
    lines = [line for line in raw_lines if line and line not in NOISE_LINES]

    merged: List[str] = []
    for line in lines:
        if line in {"Certificate", "Program"} and merged:
            merged[-1] = f"{merged[-1]} {line}"
            continue
        merged.append(line)
    return merged


def _extract_updates(lines: List[str]) -> List[UpdateItem]:
    if "Updates" not in lines:
        return []

    update_indices = [i for i, value in enumerate(lines) if value == "Updates"]
    start = update_indices[-1] + 1
    upcoming_after = [i for i, value in enumerate(lines[start:], start=start) if value == "Upcoming Events"]
    end = upcoming_after[0] if upcoming_after else len(lines)
    segment = lines[start:end]

    updates: List[UpdateItem] = []
    i = 0
    while i < len(segment):
        title = segment[i]
        if len(title) < 8 or title in WEEKDAYS or DATE_LINE_RE.match(title):
            i += 1
            continue

        summary = ""
        if i + 1 < len(segment):
            summary = segment[i + 1]

        if summary and len(summary) > 24 and summary != title:
            updates.append(UpdateItem(title=title, summary=summary, source_url=SOURCE_URL))
            i += 2
        else:
            i += 1
    return updates[:6]


def _is_noise_title(value: str) -> bool:
    if value in WEEKDAYS or value in MONTHS:
        return True
    if value.isdigit():
        return True
    return False


def _extract_events(lines: List[str]) -> List[EventItem]:
    if "Upcoming Events" not in lines:
        return []

    start = lines.index("Upcoming Events") + 1
    end = lines.index("Quick Links") if "Quick Links" in lines[start:] else len(lines)
    segment = lines[start:end]

    events: List[EventItem] = []
    for idx, line in enumerate(segment):
        if not DATE_LINE_RE.match(line):
            continue

        title = ""
        for back in range(1, 5):
            prev_idx = idx - back
            if prev_idx < 0:
                break
            candidate = segment[prev_idx]
            if _is_noise_title(candidate):
                continue
            title = candidate
            break

        location = ""
        if idx + 1 < len(segment) and "," in segment[idx + 1]:
            location = segment[idx + 1]

        if title:
            events.append(
                EventItem(
                    title=title,
                    schedule=line,
                    location=location or "Location TBC",
                    source_url=SOURCE_URL,
                )
            )

    deduped = []
    seen = set()
    for event in events:
        key = (event.title, event.schedule)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)
    return deduped[:10]


def fetch_events_payload() -> EventsPayload:
    response = requests.get(SOURCE_URL, timeout=20)
    response.raise_for_status()

    lines = _extract_lines(response.text)
    payload = EventsPayload(
        source_url=SOURCE_URL,
        synced_at=datetime.now(timezone.utc).isoformat(),
        updates=_extract_updates(lines),
        events=_extract_events(lines),
    )
    return payload


def save_payload(payload: EventsPayload) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "source_url": payload.source_url,
                "synced_at": payload.synced_at,
                "updates": [asdict(item) for item in payload.updates],
                "events": [asdict(item) for item in payload.events],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_cached_payload() -> EventsPayload | None:
    if not CACHE_PATH.exists():
        return None
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return EventsPayload(
        source_url=data.get("source_url", SOURCE_URL),
        synced_at=data.get("synced_at", ""),
        updates=[UpdateItem(**item) for item in data.get("updates", [])],
        events=[EventItem(**item) for item in data.get("events", [])],
    )
