from __future__ import annotations

import re
from io import BytesIO
from dataclasses import dataclass
from pathlib import Path
from typing import List

from pypdf import PdfReader


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]{2,}")


@dataclass
class Chunk:
    source: str
    text: str


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: List[str] = []
    start = 0
    text_len = len(cleaned)
    while start < text_len:
        end = min(text_len, start + chunk_size)
        chunks.append(cleaned[start:end])
        if end == text_len:
            break
        start = max(0, end - overlap)
    return chunks


def build_chunks(knowledge_dir: str = "knowledge_base") -> List[Chunk]:
    base_path = Path(knowledge_dir)
    if not base_path.exists():
        return []

    all_chunks: List[Chunk] = []
    for file_path in sorted(base_path.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for chunk in _chunk_text(text):
            all_chunks.append(Chunk(source=file_path.name, text=chunk))
    return all_chunks


def build_chunks_from_uploaded_files(uploaded_files) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    if not uploaded_files:
        return all_chunks

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        suffix = Path(filename).suffix.lower()
        if suffix not in {".md", ".txt", ".pdf"}:
            continue

        raw = uploaded_file.getvalue()
        if suffix == ".pdf":
            reader = PdfReader(BytesIO(raw))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text = raw.decode("utf-8", errors="ignore")

        for chunk in _chunk_text(text):
            all_chunks.append(Chunk(source=f"upload:{filename}", text=chunk))

    return all_chunks


def retrieve_chunks(query: str, chunks: List[Chunk], top_k: int = 3) -> List[Chunk]:
    query_tokens = _tokenize(query)
    if not query_tokens or not chunks:
        return []

    scored: List[tuple[int, int, Chunk]] = []
    for chunk in chunks:
        chunk_tokens = _tokenize(chunk.text)
        overlap = len(query_tokens & chunk_tokens)
        if overlap == 0:
            continue
        scored.append((overlap, len(chunk.text), chunk))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in scored[:top_k]]


def format_context(chunks: List[Chunk]) -> str:
    if not chunks:
        return ""
    lines = []
    for idx, chunk in enumerate(chunks, 1):
        lines.append(f"[Source {idx}: {chunk.source}] {chunk.text}")
    return "\n\n".join(lines)
