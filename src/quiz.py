"""Load and score CFA demo quiz questions from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

DEFAULT_QUIZ_PATH = Path("knowledge_base/quiz_level1_demo.json")


@dataclass
class QuizQuestion:
    id: str
    level: str
    topic: str
    stem: str
    choices: List[str]
    correct_index: int
    explanation: str


def load_questions(path: Path | str | None = None) -> List[QuizQuestion]:
    quiz_path = Path(path) if path else DEFAULT_QUIZ_PATH
    if not quiz_path.is_file():
        return []
    data = json.loads(quiz_path.read_text(encoding="utf-8"))
    out: List[QuizQuestion] = []
    for raw in data.get("questions", []):
        try:
            out.append(
                QuizQuestion(
                    id=str(raw["id"]),
                    level=str(raw.get("level", "")),
                    topic=str(raw.get("topic", "")),
                    stem=str(raw["stem"]),
                    choices=[str(c) for c in raw["choices"]],
                    correct_index=int(raw["correct_index"]),
                    explanation=str(raw.get("explanation", "")),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return out


def grade(questions: List[QuizQuestion], picked_by_id: dict[str, int]) -> tuple[int, List[tuple[QuizQuestion, int, bool]]]:
    """Return (correct_count, list of (question, picked_index, is_correct))."""
    details = []
    correct = 0
    for q in questions:
        picked = picked_by_id.get(q.id, -1)
        ok = picked == q.correct_index
        if ok:
            correct += 1
        details.append((q, picked, ok))
    return correct, details
