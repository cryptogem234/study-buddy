"""
seed_biology.py
Seeds Biology Grade 8 into the study_buddy DB (NGSS MS-LS: From Molecules to
Organisms, Heredity, and Natural Selection).
Generates detailed lessons and mixed biology questions via Claude Sonnet.

Run from the backend folder:
    python seed_biology.py

Requires backend/.env:
    ANTHROPIC_API_KEY=sk-ant-...
"""
import json
import os
import re
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
db = SessionLocal()

MODEL = "claude-sonnet-4-6"

# ── Curriculum ────────────────────────────────────────────────────────────────

CURRICULUM = [
    {
        "name": "Biology",
        "grade": 8,
        "icon": "\U0001f9eb",  # petri dish
        "description": "Biology — Cells, Body Systems, Heredity & Evolution (NGSS MS-LS)",
        "units": [
            {
                "name": "Cell Structure & Function",
                "term": 1,
                "topics": [
                    "Cell Theory & the Discovery of Cells",
                    "Plant vs. Animal Cells",
                    "Cell Organelles & Their Functions",
                    "Cell Membrane & Transport",
                ],
            },
            {
                "name": "Body Systems & Homeostasis",
                "term": 1,
                "topics": [
                    "Levels of Organization: Cells, Tissues, Organs & Systems",
                    "The Circulatory & Respiratory Systems",
                    "The Digestive & Excretory Systems",
                    "The Nervous System & Homeostasis",
                ],
            },
            {
                "name": "Heredity & Reproduction",
                "term": 2,
                "topics": [
                    "DNA, Genes & Chromosomes",
                    "Heredity & Punnett Squares",
                    "Sexual vs. Asexual Reproduction",
                    "Mutations & Genetic Variation",
                ],
            },
            {
                "name": "Evolution & Ecosystems",
                "term": 2,
                "topics": [
                    "Evidence for Evolution",
                    "Natural Selection & Adaptation",
                    "Ecosystems, Energy Flow & Food Webs",
                ],
            },
        ],
    },
]

# ── Prompts ───────────────────────────────────────────────────────────────────

LESSON_PROMPT = """\
You are writing a biology textbook chapter for a {grade}th grader in a US public \
school (Massachusetts, NGSS curriculum — From Molecules to Organisms, Heredity, and \
Natural Selection, MS-LS).

Topic: {topic}
Unit: {unit}

Write a COMPLETE, DETAILED chapter-length lesson in markdown. This is NOT a summary \
or overview — it is the full lesson the student will read to actually learn the \
topic. Aim for 1500-2000 words.

STRUCTURE (use these exact ## headers):

## Introduction
Open with a vivid 3-5 sentence real-world scenario or story that puts the student \
right in the middle of the concept. No questions — just a compelling scene. Then \
explain what this chapter will cover and why it matters in their life.

## Background: Why This Matters
Explain the broader context. Connect this topic to something the student already \
knows or experiences daily (their own body, a pet, a garden, illness, sports, food). \
Give historical context or a surprising real-world application that makes this feel \
relevant.

## Core Concepts

Break this into 2-4 subsections using ### headers, one per major idea. For each \
subsection:
- Define the concept clearly in plain language
- Use a concrete analogy comparing it to something familiar (food, sports, phones, \
machines, everyday objects)
- Explain the mechanism or process step by step where applicable
- **Bold** every key vocabulary term the first time it appears, followed immediately \
by a plain-English definition in parentheses
- Where helpful, include a simple worked example (e.g. tracing a Punnett square, \
describing a labeled diagram in words, walking through a process step by step)

## Real-World Connections
Give 2-3 specific, detailed examples of this topic in action in the real world. \
These should feel exciting and relevant to a 12-13 year old. Include at least one \
example from medicine, sports/fitness, agriculture, or conservation.

> 💡 **Did You Know?** [One genuinely surprising, specific fact that will make the \
student say "wow"]

## Think About It
Present 2 thought-provoking questions or mini-scenarios (no answers given) that push \
the student to apply what they just learned. Phrase them like "What do you think \
would happen if..." or "Imagine you are a biologist and..."

## Key Vocabulary
List every bolded term from the lesson as a bulleted glossary with a 1-2 sentence \
definition each.

## Summary
Write 5-7 bullet points covering the most important ideas from the chapter. Each \
bullet should be a complete, informative sentence — not just a label.

---

Tone: Enthusiastic, clear, conversational — like a great biology teacher who loves \
their subject. Never dry, never condescending. Speak directly to the student as "you."

Return only the markdown lesson. No preamble, no "here is the lesson", no closing \
remarks.
"""

QUESTIONS_PROMPT = """\
Generate exactly 6 multiple-choice questions for a {grade}th grade biology lesson on \
"{topic}" (unit: {unit}, NGSS MS-LS).

Use this EXACT mix of question types in this order:

Q1 — VOCABULARY/DEFINITION: Ask the student to identify the correct definition or \
correct use of a key biology term directly tied to "{topic}".

Q2 — CONCEPTUAL UNDERSTANDING: Test understanding of the core mechanism or idea \
behind "{topic}" — not memorization, but "why" or "how" it works.

Q3 — APPLICATION/SCENARIO: Describe an original everyday or biological scenario \
(2-4 sentences) and ask the student to apply what they learned about "{topic}" to \
explain or predict what happens.

Q4 — REAL-WORLD CONNECTION: Ask about a real-world example, medical case, organism, \
or natural phenomenon (health, agriculture, conservation, sports) that relates to \
"{topic}".

Q5 — PROCESS/STRUCTURE OR CLASSIFICATION: If "{topic}" involves a process, sequence, \
structure, or classification (e.g. tracing a Punnett square, identifying an \
organelle's function, comparing reproduction types, sequencing a body system's \
pathway), test that skill directly. If not applicable, ask a question that requires \
comparing two related concepts from the lesson.

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
- Grade-appropriate difficulty for a {grade}th grader following NGSS MS-LS standards
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

# ── Helpers ───────────────────────────────────────────────────────────────────

def call_claude(prompt: str, max_tokens: int = 4096, retries: int = 3) -> str:
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


def generate_lesson(topic: str, unit: str, grade: int) -> str:
    prompt = LESSON_PROMPT.format(grade=grade, topic=topic, unit=unit)
    return call_claude(prompt, max_tokens=4096)


def count_longest_is_correct(qs: list[dict]) -> int:
    """How many questions have the correct option as the (strictly) longest by character count."""
    skewed = 0
    for q in qs:
        lens = [len(o) for o in q["options"]]
        if lens.index(max(lens)) == q["correct_index"]:
            skewed += 1
    return skewed


def fetch_and_validate(prompt: str) -> list[dict]:
    raw = call_claude(prompt, max_tokens=3000)
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


def generate_questions(topic: str, unit: str, grade: int) -> list[dict]:
    base_prompt = QUESTIONS_PROMPT.format(grade=grade, topic=topic, unit=unit)

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


# ── Seed ──────────────────────────────────────────────────────────────────────

total_topics = sum(
    len(unit["topics"])
    for subj in CURRICULUM
    for unit in subj["units"]
)

print(f"\nStudy Buddy — Biology Curriculum Seeder")
print(f"Model  : {MODEL}")
print(f"Subjects: {len(CURRICULUM)}  |  Topics: {total_topics}")
print("=" * 60)

failed = []
topic_num = 0

for subj_data in CURRICULUM:
    grade = subj_data["grade"]

    existing_subj = (
        db.query(models.Subject)
        .filter(models.Subject.name == subj_data["name"], models.Subject.grade == grade)
        .first()
    )
    if existing_subj:
        subject = existing_subj
        print(f"\nSubject Biology Grade {grade} already exists (id={subject.id}) — adding missing topics only")
    else:
        subject = models.Subject(
            name=subj_data["name"],
            grade=grade,
            description=subj_data["description"],
            icon=subj_data["icon"],
        )
        db.add(subject)
        db.commit()
        db.refresh(subject)
        print(f"\nCreated subject: Biology Grade {grade} (id={subject.id})")

    existing_names = {
        t.name
        for t in db.query(models.Topic).filter(models.Topic.subject_id == subject.id).all()
    }
    order = db.query(models.Topic).filter(models.Topic.subject_id == subject.id).count()

    print(f"\n{'-' * 60}")

    for unit_data in subj_data["units"]:
        unit_name = unit_data["name"]
        term = unit_data["term"]
        print(f"\n  Unit: {unit_name}  (Term {term})")

        for topic_name in unit_data["topics"]:
            order += 1
            topic_num += 1
            prefix = f"  [{topic_num:>2}/{total_topics}]"

            if topic_name in existing_names:
                print(f"{prefix} {topic_name} -- already exists, skipping")
                continue

            print(f"{prefix} {topic_name}", end="  ", flush=True)

            # Create topic row
            topic = models.Topic(
                subject_id=subject.id,
                name=topic_name,
                order=order,
                term=term,
                unit=unit_name,
            )
            db.add(topic)
            db.flush()  # get topic.id

            # Generate lesson
            try:
                content = generate_lesson(topic_name, unit_name, grade)
                words = len(content.split())
                db.add(models.Lesson(
                    topic_id=topic.id,
                    title=topic_name,
                    content=content,
                    order=1,
                ))
                print(f"lesson OK ({words}w)", end="  ", flush=True)
            except Exception as e:
                db.rollback()
                failed.append(f"Grade {grade} / {topic_name} — lesson: {e}")
                print(f"lesson FAILED: {e}")
                continue

            # Generate questions
            try:
                qs = generate_questions(topic_name, unit_name, grade)
                for q in qs:
                    db.add(models.Question(
                        topic_id=topic.id,
                        stem=q["stem"],
                        options=q["options"],
                        correct_index=q["correct_index"],
                        explanation=q.get("explanation", ""),
                    ))
                print(f"| questions OK ({len(qs)}q)")
            except Exception as e:
                failed.append(f"Grade {grade} / {topic_name} — questions: {e}")
                print(f"| questions FAILED: {e}")
                # Still commit topic + lesson even if questions fail

            db.commit()
            time.sleep(1)

db.close()

print(f"\n{'=' * 60}")
succeeded = total_topics - len([f for f in failed if "lesson" in f])
print(f"Done.  {succeeded}/{total_topics} topics seeded successfully.")
if failed:
    print(f"\nFailed ({len(failed)}):")
    for item in failed:
        print(f"  FAIL  {item}")
else:
    print("No failures!")
