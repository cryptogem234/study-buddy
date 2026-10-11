"""Grades a written reading response with Claude against the passage's rubric.

Returns None when grading is unavailable (no API key on this computer, or the
request fails), so the page can fall back to showing the model answer.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import anthropic

load_dotenv(Path(__file__).parent / ".env")

MODEL = "claude-sonnet-5-5"

GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer"},
        "went_well": {"type": "string"},
        "to_improve": {"type": "string"},
    },
    "required": ["score", "went_well", "to_improve"],
    "additionalProperties": False,
}

SYSTEM = """\
You are an encouraging but honest 8th grade English teacher grading a short written \
response about a reading passage, the way the Massachusetts MCAS scores short \
responses. Score 0-4:
4 = clear, accurate answer fully supported by relevant evidence from the passage, \
with explanation of how the evidence supports it.
3 = accurate answer with some relevant evidence, but explanation is thin.
2 = partly accurate, or evidence is vague or not explained.
1 = minimal understanding; little or no evidence.
0 = off topic, inaccurate, or blank.
Speak directly to the student (\"you\"), in plain words for a 13-year-old. \
went_well: 1-2 sentences naming something specific she did well. to_improve: 1-3 \
sentences giving the single most useful next step, pointing to a specific part of \
the passage when possible. Do not rewrite her answer for her."""


def grade(passage_text: str, prompt: str, rubric: list[str], model_answer: str, answer: str) -> dict | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    user = (
        f"<passage>\n{passage_text}\n</passage>\n\n"
        f"<question>{prompt}</question>\n\n"
        f"<rubric>\n" + "\n".join(f"- {r}" for r in rubric) + "\n</rubric>\n\n"
        f"<strong_example_answer>{model_answer}</strong_example_answer>\n\n"
        f"<student_answer>{answer}</student_answer>"
    )
    try:
        response = anthropic.Anthropic().beta.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=SYSTEM,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": GRADE_SCHEMA}},
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
        )
        if response.stop_reason in ("refusal", "max_tokens"):
            return None
        data = json.loads(next(b.text for b in response.content if b.type == "text"))
    except Exception:
        return None
    data["score"] = max(0, min(4, data["score"]))
    return data
