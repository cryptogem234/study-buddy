"""
seed_vocabulary.py
Generates vocabulary words for every lesson using Claude Haiku 4.5.

Run from the backend folder:
    python seed_vocabulary.py

Skips lessons that already have vocabulary words seeded.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import anthropic
from database import SessionLocal
from models import Lesson, VocabularyWord
import models  # noqa: F401 — ensures all models are registered

from database import engine, Base

load_dotenv(Path(__file__).parent / ".env")

# Create any missing tables (idempotent)
Base.metadata.create_all(bind=engine)

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in backend/.env")
    exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

SYSTEM = (
    "You are a vocabulary tutor for 7th and 8th grade students. "
    "Extract key vocabulary from lessons and write clear, grade-appropriate definitions."
)

PROMPT = """\
Extract 6-10 key vocabulary words from the lesson below.

For each word return a JSON object with these exact fields:
- "word": the vocabulary word or short phrase
- "definition": a clear definition written for a 13-year-old (1-2 sentences)
- "part_of_speech": noun / verb / adjective / adverb / phrase
- "example_sentence": one sentence using the word meaningfully in context

Return ONLY a valid JSON array — no explanation, no markdown fences.

Lesson:
{content}"""


def seed():
    db = SessionLocal()
    lessons = db.query(Lesson).order_by(Lesson.topic_id, Lesson.order).all()
    total = len(lessons)
    skipped = 0
    generated = 0

    for i, lesson in enumerate(lessons, 1):
        existing = db.query(VocabularyWord).filter(VocabularyWord.lesson_id == lesson.id).count()
        if existing > 0:
            print(f"[{i}/{total}] Skip (already done): {lesson.title}")
            skipped += 1
            continue

        print(f"[{i}/{total}] Generating: {lesson.title} ...", end=" ", flush=True)
        try:
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=SYSTEM,
                messages=[{
                    "role": "user",
                    "content": PROMPT.format(content=lesson.content[:5000]),
                }],
            )
            raw = response.content[0].text.strip()
            # Strip accidental markdown fences if Claude adds them
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            words = json.loads(raw)
            for w in words:
                db.add(VocabularyWord(
                    lesson_id=lesson.id,
                    word=w.get("word", "").strip(),
                    definition=w.get("definition", "").strip(),
                    part_of_speech=w.get("part_of_speech", "").strip(),
                    example_sentence=w.get("example_sentence", "").strip(),
                ))
            db.commit()
            print(f"{len(words)} words")
            generated += len(words)
        except Exception as e:
            db.rollback()
            print(f"ERROR — {e}")

    db.close()
    print(f"\nDone. {generated} words generated across {total - skipped} lessons ({skipped} skipped).")


if __name__ == "__main__":
    seed()
