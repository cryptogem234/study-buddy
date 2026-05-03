"""
enrich_curriculum.py
  1. Rewrites each lesson to be engaging and student-friendly (grade 7/8)
  2. Generates 18 MCQs per topic (6 easy / 6 medium / 6 hard)

Run from the backend folder:
    python enrich_curriculum.py

Requires backend/.env containing:
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

MODEL = "claude-haiku-4-5-20251001"


def expand_lesson(topic_name, grade, current_content):
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1400,
        messages=[{
            "role": "user",
            "content": f"""Rewrite the following as an exciting, student-friendly science lesson for a {grade}th grader.

Topic: {topic_name}
Source material:
{current_content[:2500]}

Requirements:
- Open with a 1-2 sentence real-world hook that grabs attention (e.g. "Have you ever wondered why...")
- Use ## markdown headers for at least 3 clear sections
- **Bold** every key vocabulary term the first time it appears
- Include exactly one blockquote like this:
  > 💡 **Did You Know?** [surprising or cool fact]
- Use bullet points or numbered steps where helpful
- Include a relatable real-world example (sports, food, phones, nature, etc.)
- End with a "## Key Takeaways" section listing 4-5 bullet points
- Tone: enthusiastic, clear, never dry or textbook-boring
- Length: 500-750 words

Return only the markdown lesson, no preamble or commentary."""
        }]
    )
    return resp.content[0].text.strip()


def generate_questions(topic_name, grade, lesson_content):
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4500,
        messages=[{
            "role": "user",
            "content": f"""Generate exactly 18 multiple-choice quiz questions for a {grade}th grade student about "{topic_name}".

Base your questions on this lesson:
{lesson_content[:2200]}

Rules:
- First 6 questions: EASY — direct recall of facts from the lesson
- Next 6 questions: MEDIUM — requires understanding and simple application
- Last 6 questions: HARD — analysis, comparison, or real-world application
- Each question has exactly 4 answer choices
- Vary which position (0, 1, 2, or 3) is correct — do NOT always use the same index
- Each explanation is 1-2 sentences explaining why the answer is correct
- Questions must be different from each other — no repetition

Return ONLY a valid JSON array with no markdown fences, no extra text:
[
  {{
    "stem": "Question text ending with a question mark?",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_index": 2,
    "explanation": "One or two sentences explaining why this is correct."
  }}
]"""
        }]
    )
    return resp.content[0].text.strip()


def parse_json_questions(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\[[\s\S]*\]', raw)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return []


topics = (
    db.query(models.Topic)
    .join(models.Subject)
    .order_by(models.Subject.grade, models.Topic.order)
    .all()
)

total = len(topics)
print(f"Enriching {total} topics with Claude {MODEL}...\n")

for i, topic in enumerate(topics, 1):
    grade = topic.subject.grade
    lesson = db.query(models.Lesson).filter(models.Lesson.topic_id == topic.id).first()

    if not lesson:
        print(f"[{i}/{total}] {topic.name} — no lesson, skipping")
        continue

    print(f"[{i}/{total}] {topic.name} (Grade {grade})")

    # ── Expand lesson ──────────────────────────────────────────────────────
    print(f"         Expanding lesson...", end=" ", flush=True)
    try:
        lesson.content = expand_lesson(topic.name, grade, lesson.content)
        db.flush()
        print("OK")
    except Exception as e:
        print(f"FAILED — {e}")

    # ── Generate questions ─────────────────────────────────────────────────
    print(f"         Generating 18 questions...", end=" ", flush=True)
    try:
        raw = generate_questions(topic.name, grade, lesson.content)
        questions = parse_json_questions(raw)

        if questions:
            db.query(models.Question).filter(models.Question.topic_id == topic.id).delete()
            for q in questions:
                db.add(models.Question(
                    topic_id=topic.id,
                    stem=q["stem"],
                    options=q["options"],
                    correct_index=int(q["correct_index"]),
                    explanation=q.get("explanation", ""),
                ))
            db.flush()
            print(f"OK ({len(questions)} questions)")
        else:
            print("FAILED — could not parse JSON response")
    except Exception as e:
        print(f"FAILED — {e}")

    db.commit()
    time.sleep(0.5)

db.close()
print(f"\nDone! All {total} topics enriched.")
