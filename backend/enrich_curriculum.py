"""
enrich_curriculum.py
  Rewrites every lesson into a rich, chapter-depth markdown lesson (~1500-2000 words).
  Questions are left untouched.

Run from the backend folder:
    python enrich_curriculum.py

Requires backend/.env containing:
    ANTHROPIC_API_KEY=sk-ant-...
"""
import os
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

MODEL = "claude-haiku-4-5-20251001"

LESSON_PROMPT = """\
You are writing a science textbook chapter for a {grade}th grader in a US public school (Massachusetts, NGSS curriculum).

Topic: {topic}

Write a COMPLETE, DETAILED chapter-length lesson in markdown. This is NOT a summary or overview — it is the full lesson the student will read to actually learn the topic. Aim for 1500–2000 words.

STRUCTURE (use these exact ## headers):

## Introduction
Open with a vivid 3–5 sentence real-world scenario or story that puts the student right in the middle of the concept. No questions — just a compelling scene. Then explain what this chapter will cover and why it matters in their life.

## Background: Why This Matters
Explain the broader context. Connect this topic to something the student already knows or experiences daily. Give historical context or a surprising real-world application that makes this feel relevant.

## Core Concepts

Break this into 2–4 subsections using ### headers, one per major idea. For each subsection:
- Define the concept clearly in plain language
- Use a concrete analogy comparing it to something familiar (food, sports, phones, the human body, everyday objects)
- Explain the mechanism or process step by step where applicable
- **Bold** every key vocabulary term the first time it appears, followed immediately by a plain-English definition in parentheses

## Real-World Connections
Give 2–3 specific, detailed examples of this topic in action in the real world. These should feel exciting and relevant to a 12–13 year old. Include at least one example from technology, medicine, environment, or sports.

> 💡 **Did You Know?** [One genuinely surprising, specific fact that will make the student say "wow"]

## Think About It
Present 2 thought-provoking questions or mini-scenarios (no answers given) that push the student to apply what they just learned. Phrase them like "What do you think would happen if..." or "Imagine you are a scientist and..."

## Key Vocabulary
List every bolded term from the lesson as a bulleted glossary with a 1–2 sentence definition each.

## Summary
Write 5–7 bullet points covering the most important ideas from the chapter. Each bullet should be a complete, informative sentence — not just a label.

---

Tone: Enthusiastic, clear, conversational — like a great teacher who loves their subject. Never dry, never condescending. Speak directly to the student as "you."

Return only the markdown lesson. No preamble, no "here is the lesson", no closing remarks.
"""


def expand_lesson(topic_name: str, grade: int) -> str:
    prompt = LESSON_PROMPT.format(
        grade=grade,
        topic=topic_name,
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return resp.content[0].text.strip()


topics = (
    db.query(models.Topic)
    .join(models.Subject)
    .order_by(models.Subject.grade, models.Topic.order)
    .all()
)

total = len(topics)
print(f"Re-enriching lessons for {total} topics with Claude {MODEL}...\n")
print("(Questions are not being changed)\n")

failed = []

for i, topic in enumerate(topics, 1):
    grade = topic.subject.grade
    lesson = db.query(models.Lesson).filter(models.Lesson.topic_id == topic.id).first()

    if not lesson:
        print(f"[{i}/{total}] {topic.name} — no lesson found, skipping")
        continue

    print(f"[{i}/{total}] {topic.name} (Grade {grade}) ... ", end="", flush=True)

    try:
        lesson.content = expand_lesson(topic.name, grade)
        db.commit()
        # estimate word count
        word_count = len(lesson.content.split())
        print(f"OK  (~{word_count} words)")
    except Exception as e:
        db.rollback()
        failed.append(topic.name)
        print(f"FAILED — {e}")

    time.sleep(0.3)

db.close()

print(f"\n{'='*50}")
print(f"Done. {total - len(failed)}/{total} lessons enriched.")
if failed:
    print(f"\nFailed topics ({len(failed)}):")
    for name in failed:
        print(f"  - {name}")
