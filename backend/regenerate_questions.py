"""
regenerate_questions.py
Deletes and regenerates all quiz questions for every topic in a given subject,
using a length-balanced, count-bumped question prompt (fixes both the "longest
option is always correct" guessability bug and the "same questions every time"
thin-pool problem found in early Science/ELA question sets).

Only touches the `questions` table — never `topics` or `lessons` — so existing
lesson-completion and quiz-attempt history (which reference topic_id/lesson_id,
not question_id) stay valid across a regeneration.

Run from the backend folder:
    python regenerate_questions.py Science7
    python regenerate_questions.py Science8
    python regenerate_questions.py ELA7
    python regenerate_questions.py ELA8
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

MODEL = "claude-haiku-4-5"
QUESTIONS_PER_TOPIC = 15

# slug -> (db subject name, db grade, subject_word, standard)
SUBJECT_CONFIG = {
    "Science7": ("7th Grade Science", 7, "science", "NGSS Grade 7 Science"),
    "Science8": ("8th Grade Science", 8, "science", "NGSS Grade 8 Science"),
    "ELA7": ("ELA", 7, "English Language Arts", "Common Core ELA (Grade 7)"),
    "ELA8": ("ELA", 8, "English Language Arts", "Common Core ELA (Grade 8)"),
    "Chemistry": ("Chemistry", 8, "chemistry", "NGSS MS-PS1"),
    "Biology": ("Biology", 8, "biology", "NGSS MS-LS"),
}

QUESTION_TYPES = """\
- VOCABULARY/DEFINITION: identify the correct definition or correct use of a key term.
- CONCEPTUAL UNDERSTANDING: test the "why" or "how" behind the idea, not memorization.
- APPLICATION/SCENARIO: an original 2-4 sentence scenario the student must apply the \
concept to.
- REAL-WORLD CONNECTION: a real-world example, technology, or phenomenon tied to the \
topic.
- PROCESS/CLASSIFICATION OR COMPARISON: a process, sequence, or classification skill, \
or a comparison between two related concepts.
- MISCONCEPTION CHECK: a common misconception appears as a distractor; the student \
must pick the correct statement."""

QUESTIONS_PROMPT = """\
Generate exactly {n} multiple-choice questions for a {grade}th grade {subject_word} \
lesson on "{topic}" (unit: {unit}, {standard}).

Cycle through this mix of question types roughly evenly across the {n} questions — \
do not write two questions that test the same fact in the same way:

{question_types}

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
- Vary which option position (0-3) holds the correct answer across the {n} questions \
— do not always put it in the same slot
- correct_index is 0-based (0 = first option, 1 = second, etc.)
- Include a 2-3 sentence explanation for the correct answer — explain WHY it is \
correct and why the distractors are wrong
- Grade-appropriate difficulty for a {grade}th grader following {standard} standards
- All scenarios must be original — do not reproduce copyrighted material
- Questions should feel like real classroom or standardized test practice
- No two questions should be near-duplicates of each other

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


def call_claude(prompt: str, max_tokens: int = 12000, retries: int = 3) -> str:
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


def fetch_and_validate(prompt: str, n: int, max_tokens: int = 4500) -> list[dict]:
    raw = call_claude(prompt, max_tokens=max_tokens)
    data = extract_json(raw)
    qs = data["questions"]
    if len(qs) != n:
        raise ValueError(f"Expected {n} questions, got {len(qs)}")
    for q in qs:
        if len(q["options"]) != 4:
            raise ValueError(f"Question has {len(q['options'])} options, expected 4")
        if not (0 <= q["correct_index"] <= 3):
            raise ValueError(f"correct_index {q['correct_index']} out of range")
    return qs


BATCH_SIZE = 5  # small batches converge to a balanced length/position mix far more
                # reliably than asking for QUESTIONS_PER_TOPIC at once


def generate_question_batch(
    topic: str, unit: str, grade: int, subject_word: str, standard: str,
    batch_size: int, avoid_stems: list[str],
) -> list[dict]:
    base_prompt = QUESTIONS_PROMPT.format(
        grade=grade, topic=topic, unit=unit, subject_word=subject_word, standard=standard,
        n=batch_size, question_types=QUESTION_TYPES,
    )
    if avoid_stems:
        avoid_text = "\n".join(f"- {s}" for s in avoid_stems)
        base_prompt += f"\n\nDo NOT repeat or closely rephrase any of these already-used questions:\n{avoid_text}"

    best_qs, best_skew = None, 999
    prompt = base_prompt
    max_acceptable_skew = max(1, round(batch_size * 0.3))
    last_error = None

    for attempt in range(4):
        try:
            qs = fetch_and_validate(prompt, batch_size)
        except ValueError as e:
            last_error = e
            prompt = (
                base_prompt
                + f"\n\nYour previous response was rejected: {e}. Return EXACTLY {batch_size} "
                f"questions, each with EXACTLY 4 options — count them before responding."
            )
            continue

        skew = count_longest_is_correct(qs)
        if skew < best_skew:
            best_qs, best_skew = qs, skew
        if skew <= max_acceptable_skew:
            return qs
        prompt = (
            base_prompt
            + f"\n\nYour previous attempt made the correct answer the longest option in "
            f"{skew} of {batch_size} questions — that is a guessable pattern a student can "
            f"exploit without knowing the material. Rewrite every distractor so its length "
            f"and level of detail closely matches the correct answer, even if that means "
            f"adding plausible specific-sounding detail to the wrong options."
        )

    if best_qs is not None:
        return best_qs
    raise last_error


def generate_questions(topic: str, unit: str, grade: int, subject_word: str, standard: str) -> list[dict]:
    n = QUESTIONS_PER_TOPIC
    assert n % BATCH_SIZE == 0
    all_qs: list[dict] = []
    stems_seen: list[str] = []
    for _ in range(n // BATCH_SIZE):
        batch = generate_question_batch(topic, unit, grade, subject_word, standard, BATCH_SIZE, stems_seen)
        all_qs.extend(batch)
        stems_seen.extend(q["stem"] for q in batch)
        time.sleep(1)
    return all_qs


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SUBJECT_CONFIG:
        print(f"Usage: python regenerate_questions.py <{'|'.join(SUBJECT_CONFIG)}>")
        exit(1)

    slug = sys.argv[1]
    subject_name, grade, subject_word, standard = SUBJECT_CONFIG[slug]

    db = SessionLocal()
    subject = (
        db.query(models.Subject)
        .filter(models.Subject.name == subject_name, models.Subject.grade == grade)
        .first()
    )
    if not subject:
        print(f"No subject named '{subject_name}' grade {grade} found.")
        return

    topics = (
        db.query(models.Topic)
        .filter(models.Topic.subject_id == subject.id)
        .order_by(models.Topic.order)
        .all()
    )

    total = len(topics)
    print(f"Regenerating questions for {total} {subject_name} (grade {grade}) topics "
          f"with Claude {MODEL}, {QUESTIONS_PER_TOPIC} questions/topic...\n")

    failed = []

    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{total}] {topic.name} ... ", end="", flush=True)
        try:
            qs = generate_questions(topic.name, topic.unit, grade, subject_word, standard)

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
