"""On-demand OpenAI helpers for Quiz Lab (never called unless user clicks a button)."""

from __future__ import annotations

import json
import os
from typing import List, Tuple

from openai import OpenAI, OpenAIError

from src.PROMPTS.quiz_ai_prompt import quiz_explain_system, quiz_practice_system, quiz_weakness_system
from src.quiz import QuizQuestion

QuizDetail = Tuple[QuizQuestion, int, bool]

_QUIZ_AI_MODEL = os.getenv("QUIZ_AI_MODEL", "gpt-4o-mini")
_QUIZ_AI_MAX_TOKENS = max(512, int(os.getenv("QUIZ_AI_MAX_TOKENS", "3500")))


def _chat(client: OpenAI, system: str, user: str) -> str | None:
    try:
        response = client.chat.completions.create(
            model=_QUIZ_AI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
            max_tokens=_QUIZ_AI_MAX_TOKENS,
        )
        return response.choices[0].message.content
    except OpenAIError:
        return None
    except Exception:
        return None


def _details_payload(details: List[QuizDetail]) -> str:
    items = []
    for i, (q, picked, ok) in enumerate(details, start=1):
        items.append(
            {
                "index": i,
                "id": q.id,
                "topic": q.topic,
                "stem": q.stem,
                "choices": q.choices,
                "correct_index": q.correct_index,
                "user_picked_index": picked,
                "user_correct": ok,
                "provided_explanation": q.explanation,
            }
        )
    return json.dumps({"questions": items}, ensure_ascii=False)


def explain_all_questions(client: OpenAI, lang: str, details: List[QuizDetail]) -> str | None:
    if not details:
        return None
    return _chat(client, quiz_explain_system(lang), _details_payload(details))


def analyze_wrong_items(client: OpenAI, lang: str, details: List[QuizDetail]) -> str | None:
    wrong = [(q, p, o) for q, p, o in details if not o]
    if not wrong:
        return None
    return _chat(client, quiz_weakness_system(lang), _details_payload(wrong))


def generate_practice_from_wrong(client: OpenAI, lang: str, details: List[QuizDetail]) -> str | None:
    wrong = [(q, p, o) for q, p, o in details if not o]
    if not wrong:
        return None
    return _chat(client, quiz_practice_system(lang), _details_payload(wrong))
