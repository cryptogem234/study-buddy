"""
seed_ela.py
Seeds ELA Grade 7 and Grade 8 into the study_buddy DB.
Generates detailed lessons and mixed ELA questions via Claude Sonnet.

Run from the backend folder:
    python seed_ela.py

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
        "name": "ELA",
        "grade": 7,
        "icon": "📝",
        "description": "English Language Arts — Reading, Writing, Grammar & Vocabulary",
        "units": [
            {
                "name": "Reading Literature",
                "term": 1,
                "topics": [
                    "Plot Structure & Story Arc",
                    "Character Development & Motivation",
                    "Theme & Central Message",
                    "Point of View & Narrator",
                    "Tone & Mood in Fiction",
                    "Conflict: Internal vs. External",
                ],
            },
            {
                "name": "Vocabulary & Word Study",
                "term": 1,
                "topics": [
                    "Context Clues",
                    "Greek & Latin Roots",
                    "Prefixes & Suffixes",
                    "Figurative Language: Simile, Metaphor & Personification",
                    "Connotation & Denotation",
                    "Idioms, Adages & Proverbs",
                ],
            },
            {
                "name": "Informational Text",
                "term": 2,
                "topics": [
                    "Main Idea & Supporting Details",
                    "Text Structure: Cause & Effect, Compare & Contrast, Problem & Solution",
                    "Author's Purpose & Perspective",
                    "Evaluating Evidence & Reasoning",
                    "Summarizing vs. Paraphrasing",
                    "Fact vs. Opinion",
                ],
            },
            {
                "name": "Grammar & Conventions",
                "term": 2,
                "topics": [
                    "Parts of Speech",
                    "Phrases & Clauses",
                    "Sentence Types & Sentence Variety",
                    "Punctuation: Commas, Semicolons & Colons",
                    "Subject-Verb Agreement",
                    "Pronoun-Antecedent Agreement",
                ],
            },
            {
                "name": "Writing Craft",
                "term": 3,
                "topics": [
                    "Narrative Writing: Story Structure & Voice",
                    "Argumentative Writing: Claims & Evidence",
                    "Informational & Explanatory Writing",
                    "Revision & Editing Strategies",
                    "Transitions & Sentence Fluency",
                ],
            },
            {
                "name": "Poetry",
                "term": 3,
                "topics": [
                    "Poetic Forms & Structure",
                    "Rhyme, Rhythm & Sound Devices",
                    "Imagery & Sensory Details",
                    "Analyzing a Poem: Theme & Meaning",
                ],
            },
        ],
    },
    {
        "name": "ELA",
        "grade": 8,
        "icon": "📝",
        "description": "English Language Arts — Reading, Writing, Grammar & Vocabulary",
        "units": [
            {
                "name": "Advanced Literary Reading",
                "term": 1,
                "topics": [
                    "Complex Character Analysis",
                    "Irony: Verbal, Situational & Dramatic",
                    "Symbolism & Allegory",
                    "Comparing Texts & Adaptations",
                    "Author's Craft & Style",
                    "Universal Themes Across Literature",
                ],
            },
            {
                "name": "Advanced Vocabulary",
                "term": 1,
                "topics": [
                    "Academic Vocabulary in Context",
                    "Etymology & Word Origins",
                    "Nuance & Shades of Meaning",
                    "Analogies & Word Relationships",
                    "Domain-Specific Vocabulary",
                ],
            },
            {
                "name": "Informational & Argumentative Text",
                "term": 2,
                "topics": [
                    "Argument, Claim & Counterclaim",
                    "Evaluating Sources & Credibility",
                    "Synthesizing Information Across Texts",
                    "Bias, Perspective & Point of View",
                    "Rhetorical Devices: Ethos, Pathos & Logos",
                    "Deductive vs. Inductive Reasoning",
                ],
            },
            {
                "name": "Advanced Grammar",
                "term": 2,
                "topics": [
                    "Misplaced & Dangling Modifiers",
                    "Parallel Structure",
                    "Advanced Punctuation: Dashes, Parentheses & Ellipses",
                    "Verb Moods: Indicative, Imperative & Subjunctive",
                    "Active vs. Passive Voice",
                ],
            },
            {
                "name": "Advanced Writing",
                "term": 3,
                "topics": [
                    "Research Writing & MLA Citations",
                    "Argumentative Essay Structure",
                    "Counterargument & Rebuttal",
                    "Precise Language & Formal Style",
                    "Integrating Quotations & Evidence",
                    "Writing a Literary Analysis Essay",
                ],
            },
            {
                "name": "Poetry & Literary Analysis",
                "term": 3,
                "topics": [
                    "Extended Metaphor & Conceit",
                    "Speaker vs. Poet",
                    "Analyzing Poetic Structure & Form",
                    "Comparing Poems",
                    "Writing About Literature",
                ],
            },
        ],
    },
]

# ── Prompts ───────────────────────────────────────────────────────────────────

LESSON_PROMPT = """\
You are writing an ELA lesson for a {grade}th grader in Massachusetts \
(Massachusetts ELA Curriculum Frameworks, aligned with Common Core ELA Standards).

Topic: {topic}
Unit: {unit}

Write a COMPLETE, DETAILED lesson in markdown. This should genuinely teach the \
student the skill with rich examples from real literature, writing, and everyday \
language. Aim for 1500–2000 words.

STRUCTURE (use these exact ## headers):

## Introduction
Open with a vivid, relatable scenario directly connected to this skill — a moment \
of reading confusion, a writing challenge, a funny misunderstanding, or a real scene \
from school or life. No generic "In this lesson..." openings. Pull the reader in. \
Then explain what the student will learn and why it genuinely matters for reading \
and writing.

## Background: Why This Matters
Connect this skill to real reading, writing, and communication. How does understanding \
this make you a sharper reader or stronger writer? Reference actual books, authors, \
or genres a {grade}th grader would know (e.g., The Giver, Wonder, The Outsiders, \
Hatchet, Diary of a Wimpy Kid, Harry Potter, Percy Jackson). Give context for why \
this skill is used by real writers and why it shows up on tests like the MCAS.

## Core Concepts

Break into 2–4 subsections using ### headers, one per major idea. For each:
- Define the concept in plain, clear language
- Give a concrete example using an original sentence, short passage, or quote
- Walk through the thinking process step by step — show HOW a student applies this
- **Bold** every key term the first time with a plain-English definition in parentheses

## Real-World Connections
Give 2–3 specific, detailed examples of this skill in published literature, \
journalism, speeches, or everyday life. Quote short original passages or examples. \
Connect to things a {grade}th grader finds interesting — sports, social media, \
music, movies, science, school life.

> 💡 **Did You Know?** [A genuinely surprising, specific fact about language, \
writing, or literature that will make the student say "wow"]

## Practice It
Present 2 mini-practice scenarios with full guided walk-throughs. Show the student's \
thinking process step by step — not just the answer, but HOW to arrive at it. \
Include the actual text or example the student is analyzing.

## Key Vocabulary
Bulleted glossary of every bolded term from the lesson, with a clear 1–2 sentence \
definition each.

## Summary
5–7 bullet points covering the most important ideas. Each bullet should be a \
complete, informative sentence — not just a label.

---
Tone: Enthusiastic, clear, conversational — like the best English teacher the \
student ever had. Speak directly to the student as "you." Use real examples. \
Never vague or generic. Make every sentence earn its place.

Return only the markdown lesson. No preamble, no "here is the lesson," no \
closing remarks.
"""

QUESTIONS_PROMPT = """\
Generate exactly 6 multiple-choice questions for a {grade}th grade ELA lesson \
on "{topic}" (unit: {unit}).

Use this EXACT mix of question types in this order:

Q1 — VOCABULARY IN CONTEXT: Write an original sentence using a word directly \
related to "{topic}". Ask what the word means, what a synonym would be, or what \
its connotation is. The sentence should be vivid and grade-appropriate.

Q2 — VOCABULARY IN CONTEXT: A second vocabulary question — focus on a word root, \
prefix/suffix, or the connotation/denotation distinction, depending on what is \
most relevant to "{topic}".

Q3 — READING COMPREHENSION: Write an original 4–7 sentence passage (narrative OR \
informational — your choice) that directly illustrates something related to \
"{topic}". Embed the passage in the question stem, then ask about main idea, \
inference, author's purpose, tone, or a specific detail. The passage must be \
original — do not reproduce any copyrighted text.

Q4 — READING COMPREHENSION: Write a DIFFERENT original 4–7 sentence passage \
(use the other text type from Q3 — if Q3 was narrative, make Q4 informational, \
or vice versa). Ask a different comprehension skill than Q3.

Q5 — GRAMMAR: Present 4 sentences as options. Ask the student to identify \
which sentence contains a grammatical or mechanical error, OR which sentence \
is correctly written. Make it clearly tied to {topic} if possible; otherwise \
use a clear grammar concept appropriate for grade {grade}.

Q6 — LITERARY/RHETORICAL ANALYSIS: Include a short original quote or example \
(1–3 sentences) in the stem. Ask what literary or rhetorical device it uses, \
what it reveals about character/theme/tone, or how it affects the reader.

Rules for ALL questions:
- Exactly 4 answer options each (no more, no less)
- One clearly correct answer; the 3 distractors must be plausible but wrong
- correct_index is 0-based (0 = first option, 1 = second, etc.)
- Include a 2–3 sentence explanation for the correct answer — explain WHY it \
is correct and why the distractors are wrong
- Grade-appropriate difficulty and reading level for a {grade}th grader
- All passages and examples must be original — do not reproduce copyrighted material
- Questions should feel like real MCAS or Common Core ELA standardized test practice

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


def generate_questions(topic: str, unit: str, grade: int) -> list[dict]:
    prompt = QUESTIONS_PROMPT.format(grade=grade, topic=topic, unit=unit)
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


# ── Seed ──────────────────────────────────────────────────────────────────────

total_topics = sum(
    len(unit["topics"])
    for subj in CURRICULUM
    for unit in subj["units"]
)

print(f"\nStudy Buddy — ELA Curriculum Seeder")
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
        print(f"\nSubject ELA Grade {grade} already exists (id={subject.id}) — adding missing topics only")
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
        print(f"\nCreated subject: ELA Grade {grade} (id={subject.id})")

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
