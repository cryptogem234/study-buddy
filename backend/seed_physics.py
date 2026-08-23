"""
seed_physics.py
Seeds Physics Grade 8 into the study_buddy DB (NGSS MS-PS2/MS-PS3/MS-PS4: Motion &
Forces, Energy, Electricity & Magnetism, Waves). Generates detailed lessons and
length-balanced, count-bumped questions via Claude Haiku 4.5.

Run from the backend folder:
    python seed_physics.py

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

MODEL = "claude-haiku-4-5"
QUESTIONS_PER_TOPIC = 15

# ── Curriculum ────────────────────────────────────────────────────────────────

CURRICULUM = [
    {
        "name": "Physics",
        "grade": 8,
        "icon": "⚛️",  # atom symbol
        "description": "Physics — Motion, Forces, Energy, Electricity & Waves (NGSS MS-PS2/PS3/PS4)",
        "units": [
            {
                "name": "Motion & Forces",
                "term": 1,
                "topics": [
                    "Describing Motion: Speed, Velocity & Acceleration",
                    "Newton's First Law: Inertia",
                    "Newton's Second Law: Force, Mass & Acceleration",
                    "Newton's Third Law: Action & Reaction",
                ],
            },
            {
                "name": "Energy",
                "term": 1,
                "topics": [
                    "Kinetic & Potential Energy",
                    "Conservation of Energy",
                    "Work, Power & Simple Machines",
                    "Thermal Energy & Heat Transfer",
                ],
            },
            {
                "name": "Electricity & Magnetism",
                "term": 2,
                "topics": [
                    "Electric Charge & Static Electricity",
                    "Electric Circuits & Current",
                    "Magnetism & Electromagnets",
                ],
            },
            {
                "name": "Waves, Sound & Light",
                "term": 2,
                "topics": [
                    "Wave Properties: Amplitude, Wavelength & Frequency",
                    "Sound Waves & How We Hear",
                    "Light, Reflection & Refraction",
                    "The Electromagnetic Spectrum",
                ],
            },
        ],
    },
]

# ── Prompts ───────────────────────────────────────────────────────────────────

LESSON_PROMPT = """\
You are writing a physics textbook chapter for a {grade}th grader in a US public \
school (Massachusetts, NGSS curriculum — Motion, Forces, Energy & Waves).

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
knows or experiences daily (sports, roller coasters, cars, phones, video games, \
music, kitchen appliances). Give historical context or a surprising real-world \
application that makes this feel relevant.

## Core Concepts

Break this into 2-4 subsections using ### headers, one per major idea. For each \
subsection:
- Define the concept clearly in plain language
- Use a concrete analogy comparing it to something familiar (sports, video games, \
amusement park rides, the human body, everyday objects)
- Explain the mechanism or process step by step where applicable
- **Bold** every key vocabulary term the first time it appears, followed immediately \
by a plain-English definition in parentheses
- Where helpful, include a simple worked example (e.g. a sample calculation, a \
labeled diagram described in words, a step-by-step trace of forces or energy)

## Real-World Connections
Give 2-3 specific, detailed examples of this topic in action in the real world. \
These should feel exciting and relevant to a 12-13 year old. Include at least one \
example from sports, transportation, technology, or entertainment.

> 💡 **Did You Know?** [One genuinely surprising, specific fact that will make the \
student say "wow"]

## Think About It
Present 2 thought-provoking questions or mini-scenarios (no answers given) that push \
the student to apply what they just learned. Phrase them like "What do you think \
would happen if..." or "Imagine you are designing a roller coaster and..."

## Key Vocabulary
List every bolded term from the lesson as a bulleted glossary with a 1-2 sentence \
definition each.

## Summary
Write 5-7 bullet points covering the most important ideas from the chapter. Each \
bullet should be a complete, informative sentence — not just a label.

---

Tone: Enthusiastic, clear, conversational — like a great physics teacher who loves \
their subject. Never dry, never condescending. Speak directly to the student as "you."

Return only the markdown lesson. No preamble, no "here is the lesson", no closing \
remarks.
"""

QUESTION_TYPES = """\
- VOCABULARY/DEFINITION: identify the correct definition or correct use of a key \
physics term directly tied to the topic.
- CONCEPTUAL UNDERSTANDING: test the "why" or "how" behind the idea, not memorization.
- APPLICATION/SCENARIO: an original 2-4 sentence everyday scenario the student must \
apply the concept to, to explain or predict what happens.
- REAL-WORLD CONNECTION: a real-world example, technology, sport, or phenomenon tied \
to the topic.
- PROCESS/CALCULATION OR CLASSIFICATION: a calculation (e.g. speed, force, energy), \
a step-by-step process, or a classification skill directly tied to the topic. If not \
applicable, a comparison between two related concepts from the lesson.
- MISCONCEPTION CHECK: a common misconception about the topic appears as a \
distractor; the student must pick the scientifically correct statement."""

QUESTIONS_PROMPT = """\
Generate exactly {n} multiple-choice questions for a {grade}th grade physics lesson \
on "{topic}" (unit: {unit}, NGSS MS-PS2/PS3/PS4).

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
- Grade-appropriate difficulty for a {grade}th grader following NGSS MS-PS2/PS3/PS4 \
standards
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


def generate_question_batch(topic: str, unit: str, grade: int, batch_size: int, avoid_stems: list[str]) -> list[dict]:
    base_prompt = QUESTIONS_PROMPT.format(
        grade=grade, topic=topic, unit=unit, n=batch_size, question_types=QUESTION_TYPES,
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


def generate_questions(topic: str, unit: str, grade: int) -> list[dict]:
    n = QUESTIONS_PER_TOPIC
    assert n % BATCH_SIZE == 0
    all_qs: list[dict] = []
    stems_seen: list[str] = []
    for _ in range(n // BATCH_SIZE):
        batch = generate_question_batch(topic, unit, grade, BATCH_SIZE, stems_seen)
        all_qs.extend(batch)
        stems_seen.extend(q["stem"] for q in batch)
        time.sleep(1)
    return all_qs


# ── Seed ──────────────────────────────────────────────────────────────────────

total_topics = sum(
    len(unit["topics"])
    for subj in CURRICULUM
    for unit in subj["units"]
)

print(f"\nStudy Buddy — Physics Curriculum Seeder")
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
        print(f"\nSubject Physics Grade {grade} already exists (id={subject.id}) — adding missing topics only")
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
        print(f"\nCreated subject: Physics Grade {grade} (id={subject.id})")

    existing_topics = {
        t.name: t
        for t in db.query(models.Topic).filter(models.Topic.subject_id == subject.id).all()
    }
    order = db.query(models.Topic).filter(models.Topic.subject_id == subject.id).count()

    print(f"\n{'-' * 60}")

    for unit_data in subj_data["units"]:
        unit_name = unit_data["name"]
        term = unit_data["term"]
        print(f"\n  Unit: {unit_name}  (Term {term})")

        for topic_name in unit_data["topics"]:
            topic_num += 1
            prefix = f"  [{topic_num:>2}/{total_topics}]"

            topic = existing_topics.get(topic_name)
            if topic is None:
                order += 1
                topic = models.Topic(
                    subject_id=subject.id,
                    name=topic_name,
                    order=order,
                    term=term,
                    unit=unit_name,
                )
                db.add(topic)
                db.flush()  # get topic.id

            has_lesson = db.query(models.Lesson).filter(models.Lesson.topic_id == topic.id).count() > 0
            has_questions = db.query(models.Question).filter(models.Question.topic_id == topic.id).count() >= QUESTIONS_PER_TOPIC

            if has_lesson and has_questions:
                print(f"{prefix} {topic_name} -- already complete, skipping")
                continue

            print(f"{prefix} {topic_name}", end="  ", flush=True)

            # Generate lesson (only if missing)
            if not has_lesson:
                try:
                    content = generate_lesson(topic_name, unit_name, grade)
                    words = len(content.split())
                    db.add(models.Lesson(
                        topic_id=topic.id,
                        title=topic_name,
                        content=content,
                        order=1,
                    ))
                    db.commit()
                    print(f"lesson OK ({words}w)", end="  ", flush=True)
                except Exception as e:
                    db.rollback()
                    failed.append(f"Grade {grade} / {topic_name} — lesson: {e}")
                    print(f"lesson FAILED: {e}")
                    continue
            else:
                print("lesson already done", end="  ", flush=True)

            if has_questions:
                print("| questions already done")
                continue

            # Generate questions
            try:
                qs = generate_questions(topic_name, unit_name, grade)
                db.query(models.Question).filter(models.Question.topic_id == topic.id).delete()
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
