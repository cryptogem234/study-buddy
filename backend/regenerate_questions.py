"""
regenerate_questions.py
Deletes and regenerates all quiz questions for every topic in a given subject,
using the length-balanced question prompt (fixes the "longest option is always
correct" guessability bug found in early Chemistry/Biology question sets).

Run from the backend folder:
    python regenerate_questions.py Chemistry
    python regenerate_questions.py Biology

Requires backend/.env:
    ANTHROPIC_API_KEY=sk-ant-...
"""
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import anthropic
from database import SessionLocal
import models

load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in backend/.env")
    exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

MODEL = "claude-sonnet-4-6"

NGSS_BY_SUBJECT = {
    "Chemistry": ("chemistry", "NGSS MS-PS1"),
    "Biology": ("biology", "NGSS MS-LS"),
}

QUESTIONS_PROMPT = """\
Generate exactly 6 multiple-choice questions for a {grade}th grade {subject_word} \
lesson on "{topic}" (unit: {unit}, {standard}).

Use this EXACT mix of question types in this order:

Q1 — VOCABULARY/DEFINITION: Ask the student to identify the correct definition or \
correct use of a key {subject_word} term directly tied to "{topic}".

Q2 — CONCEPTUAL UNDERSTANDING: Test understanding of the core mechanism or idea \
behind "{topic}" — not memorization, but "why" or "how" it works.

Q3 — APPLICATION/SCENARIO: Describe an original everyday or real-world scenario \
(2-4 sentences) and ask the student to apply what they learned about "{topic}" to \
explain or predict what happens.

Q4 — REAL-WORLD CONNECTION: Ask about a real-world example, technology, organism, \
or natural phenomenon that relates to "{topic}".

Q5 — PROCESS/STRUCTURE OR CLASSIFICATION: If "{topic}" involves a process, sequence, \
structure, or classification, test that skill directly. If not applicable, ask a \
question that requires comparing two related concepts from the lesson.

Q6 — MISCONCEPTION CHECK: Present a common misconception about "{topic}" as one of \
the wrong answers, and ask the student to identify the scientifically correct \
statement.

Rules for ALL questions:
- Exactly 4 answer options each (no more, no less)
- One clearly correct answer; the 3 distractors must be plausible but wrong
- CRITICAL — every option (the correct answer AND all three distractors) must be \
between 6 and 14 words long. Count the words as you write each one. This is a hard \
limit, not a guideline: do not write a 4-word distractor next to a 16-word correct \
answer. If the correct answer needs more words to be accurate, add comparable \
plausible-sounding specific detail to each distractor so they all land in the same \
6-14 word range. A student must not be able to spot the correct answer just by it \
being the longest or most detailed option.
- Vary which option position (0-3) holds the correct answer across the 6 questions \
— do not always put it in the same slot
- correct_index is 0-based (0 = first option, 1 = second, etc.)
- Include a 2-3 sentence explanation for the correct answer — explain WHY it is \
correct and why the distractors are wrong
- Grade-appropriate difficulty for a {grade}th grader following {standard} standards
- All scenarios must be original — do not reproduce copyrighted material
- Questions should feel like real classroom or standardized test practice

Return ONLY valid JSON with no markdown code fences, no preamble, no explanation:
{{
  "questions": [
    {{
      "stem": "...",
      "options": ["...", "...", "...", "..."],
      "correct_index": 0,
      "explanation": "..."
    }}
  ]
}}
"""


def call_claude(prompt: str, max_tokens: int = 3000, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text.strip()
        except Exception as e:
            if attempt < retries - 1:
                wait = 15 * (attempt + 1)
                print(f"\n  [retry {attempt + 1}/{retries - 1}] {e} — waiting {wait}s", flush=True)
                time.sleep(wait)
            else:
                raise


def extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"```\s*$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text.strip())


def count_longest_is_correct(qs: list[dict]) -> int:
    """How many questions have the correct option as the (strictly) longest by character count."""
    skewed = 0
    for q in qs:
        lens = [len(o) for o in q["options"]]
        if lens.index(max(lens)) == q["correct_index"]:
            skewed += 1
    return skewed


def fetch_and_validate(prompt: str) -> list[dict]:
    raw = call_claude(prompt)
    data = extract_json(raw)
    qs = data["questions"]
    if len(qs) != 6:
        raise ValueError(f"Expected 6 questions, got {len(qs)}")
    for q in qs:
        if len(q["options"]) != 4:
            raise ValueError(f"Question has {len(q['options'])} options, expected 4")
        if not (0 <= q["correct_index"] <= 3):
            raise ValueError(f"correct_index {q['correct_index']} out of range")
    return qs


def generate_questions(topic: str, unit: str, grade: int, subject_word: str, standard: str) -> list[dict]:
    base_prompt = QUESTIONS_PROMPT.format(
        grade=grade, topic=topic, unit=unit, subject_word=subject_word, standard=standard
    )

    best_qs, best_skew = None, 999
    prompt = base_prompt
    max_acceptable_skew = 2  # at most 2/6 (~33%) — close to the 25% chance baseline for 4 options

    for attempt in range(3):
        qs = fetch_and_validate(prompt)
        skew = count_longest_is_correct(qs)
        if skew < best_skew:
            best_qs, best_skew = qs, skew
        if skew <= max_acceptable_skew:
            return qs
        prompt = (
            base_prompt
            + f"\n\nYour previous attempt made the correct answer the longest option in "
            f"{skew} of 6 questions — that is a guessable pattern a student can exploit "
            f"without knowing the material. Rewrite every distractor so its length and "
            f"level of detail closely matches the correct answer, even if that means "
            f"adding plausible specific-sounding detail to the wrong options."
        )

    return best_qs


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in NGSS_BY_SUBJECT:
        print(f"Usage: python regenerate_questions.py <{'|'.join(NGSS_BY_SUBJECT)}>")
        exit(1)

    subject_name = sys.argv[1]
    subject_word, standard = NGSS_BY_SUBJECT[subject_name]

    db = SessionLocal()
    subject = db.query(models.Subject).filter(models.Subject.name == subject_name).first()
    if not subject:
        print(f"No subject named '{subject_name}' found.")
        return

    topics = (
        db.query(models.Topic)
        .filter(models.Topic.subject_id == subject.id)
        .order_by(models.Topic.order)
        .all()
    )

    total = len(topics)
    print(f"Regenerating questions for {total} {subject_name} topics with Claude {MODEL}...\n")

    failed = []

    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{total}] {topic.name} ... ", end="", flush=True)
        try:
            qs = generate_questions(topic.name, topic.unit, subject.grade, subject_word, standard)

            db.query(models.Question).filter(models.Question.topic_id == topic.id).delete()
            for q in qs:
                db.add(models.Question(
                    topic_id=topic.id,
                    stem=q["stem"],
                    options=q["options"],
                    correct_index=q["correct_index"],
                    explanation=q.get("explanation", ""),
                ))
            db.commit()
            print(f"OK ({len(qs)}q)")
        except Exception as e:
            db.rollback()
            failed.append(topic.name)
            print(f"FAILED — {e}")

        time.sleep(1)

    db.close()

    print(f"\n{'=' * 50}")
    print(f"Done. {total - len(failed)}/{total} topics regenerated.")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name in failed:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
