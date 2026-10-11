"""
enrich_lessons.py
Adds the same study features to every lesson in ELA 8, Physics, Chemistry and
Biology, without rewriting the lesson itself:
- Check Yourself: 3 quick questions with tap-to-reveal answers
- Model answers for the lesson's "Think About It" questions
- Level Up (Grade 9): a short next-step section with a worked example and
  2 check questions, unlocked after the Core quiz is passed
- 3 Level Up vocabulary words (added to the flashcards)

A second model then fact-checks the lesson and the additions; clear errors
whose exact text can be found are corrected, and every finding is logged to
generated/lesson-factcheck.md.

Lessons that already have additions are skipped, so the script can be re-run.

Run from the backend folder:
    python enrich_lessons.py --budget 14
    python enrich_lessons.py --topics 108 160 --budget 1
"""
import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import anthropic

from database import ensure_schema
import models  # noqa: F401
from expand_questions import BudgetExceeded, Spend, call_json

HERE = Path(__file__).parent
DB_PATH = HERE / "study_buddy.db"
LOG_PATH = HERE / "generated" / "lesson-factcheck.md"

WRITER_MODEL = "claude-opus-5-5"
WRITER_EFFORT = "medium"
CHECKER_MODEL = "claude-sonnet-5-5"
CHECKER_EFFORT = "medium"

# (subject name, grade) -> (core standard, Grade 9 standard)
SUBJECTS = {
    ("ELA", 8): ("Common Core ELA Grade 8", "Common Core ELA Grades 9-10"),
    ("Physics", 8): ("NGSS MS-PS2/PS3/PS4", "NGSS High School Physical Science (HS-PS2, HS-PS3, HS-PS4)"),
    ("Chemistry", 8): ("NGSS MS-PS1", "NGSS High School Chemistry (HS-PS1)"),
    ("Biology", 8): ("NGSS MS-LS", "NGSS High School Life Science (HS-LS)"),
}

QA = {
    "type": "object",
    "properties": {"question": {"type": "string"}, "answer": {"type": "string"}},
    "required": ["question", "answer"],
    "additionalProperties": False,
}
EXTRAS_SCHEMA = {
    "type": "object",
    "properties": {
        "check_yourself": {"type": "array", "items": QA},
        "think_answers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"number": {"type": "integer"}, "answer": {"type": "string"}},
                "required": ["number", "answer"],
                "additionalProperties": False,
            },
        },
        "level_up": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "standard": {"type": "string"},
                "content": {"type": "string"},
                "checks": {"type": "array", "items": QA},
            },
            "required": ["title", "standard", "content", "checks"],
            "additionalProperties": False,
        },
        "level_up_vocab": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "word": {"type": "string"},
                    "part_of_speech": {"type": "string"},
                    "definition": {"type": "string"},
                    "example_sentence": {"type": "string"},
                },
                "required": ["word", "part_of_speech", "definition", "example_sentence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["check_yourself", "think_answers", "level_up", "level_up_vocab"],
    "additionalProperties": False,
}
FACTCHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "quote": {"type": "string"},
                    "correction": {"type": "string"},
                    "reason": {"type": "string"},
                    "definitely_wrong": {"type": "boolean"},
                },
                "required": ["quote", "correction", "reason", "definitely_wrong"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["issues"],
    "additionalProperties": False,
}

WRITER_SYSTEM = """\
You add study features to an existing lesson in Study Buddy, an app used daily by \
an 8th grade student in Massachusetts who is being stretched toward 9th-grade level. \
Do not rewrite the lesson; write only the additions requested. Plain, friendly \
language for a 13-year-old. Everything must be accurate."""

WRITER_PROMPT = """\
Subject: {subject} (Grade 8, {core_standard}). Topic: "{topic}" (unit: {unit}).

<lesson>
{lesson}
</lesson>

Write these additions:

1. check_yourself: exactly 3 short questions that check understanding of the lesson's \
core ideas, placed partway through the lesson. Each answer is 1-3 sentences. Ask \
"why" or "how" questions, not just definitions.

2. think_answers: {think_instruction}

3. level_up: a "Level Up" section that takes this topic one step into Grade 9 \
({grade9_standard}).
   - title: short and specific (e.g. "Solving F = ma Problems"), without the words "Level Up".
   - standard: the Grade 9 standard it connects to, as a short label.
   - content: 350-550 words of Markdown. Teach ONE next-step idea that 9th grade builds \
on this topic; do not repeat the lesson. Use ### subheadings, **bold** key terms, and \
include one worked example: {worked_example}
   - checks: exactly 2 questions with answers (2-4 sentences each) about the Level Up \
idea, at least one requiring her to apply it.

4. level_up_vocab: exactly 3 Grade 9 words or terms introduced in the Level Up section, \
each with part of speech, a clear definition, and an example sentence."""

FACTCHECK_PROMPT = """\
You are checking a Grade 8 {subject} lesson and its add-on sections for errors before \
a student reads them. Report only clear factual or conceptual errors, wrong answers, \
or wrong calculations that a teacher would mark as wrong. Do not report style, \
simplifications that are appropriate for Grade 8, or matters of opinion.

For each error give: quote = the exact wrong text copied character-for-character \
(short, but unique enough to find), correction = the replacement text for that exact \
quote, reason = one sentence, definitely_wrong = true only if the original text is actually wrong. Never list text that is correct. Return an empty list if there are no errors.

<lesson>
{lesson}
</lesson>

<additions>
{extras}
</additions>"""


def think_section(content: str) -> str:
    """Text of the lesson's 'Think About It' section, or '' if it has none."""
    m = re.search(r"^## Think About It\s*$(.*?)(?=^## |\Z)", content, flags=re.M | re.S)
    return m.group(1).strip() if m else ""


def validate(extras: dict, has_think: bool) -> list[str]:
    problems = []
    if len(extras["check_yourself"]) != 3:
        problems.append(f"check_yourself needs exactly 3 items, got {len(extras['check_yourself'])}")
    if len(extras["level_up"]["checks"]) != 2:
        problems.append(f"level_up.checks needs exactly 2 items, got {len(extras['level_up']['checks'])}")
    if len(extras["level_up_vocab"]) != 3:
        problems.append(f"level_up_vocab needs exactly 3 words, got {len(extras['level_up_vocab'])}")
    words = len(extras["level_up"]["content"].split())
    if not 300 <= words <= 650:
        problems.append(f"level_up.content is {words} words; it must be 350-550")
    numbers = [a["number"] for a in extras["think_answers"]]
    if has_think and numbers != list(range(1, len(numbers) + 1)) or has_think != bool(numbers):
        problems.append("think_answers must answer each Think About It prompt in order, numbered 1, 2, 3...")
    return problems


def write_extras(client, spend, lesson: dict) -> dict:
    core_standard, grade9_standard = SUBJECTS[(lesson["subject"], lesson["grade"])]
    has_think = bool(think_section(lesson["content"]))
    think_instruction = (
        "give a model answer (3-5 sentences) to each separate question or scenario in the "
        "lesson's \"Think About It\" section, in order, numbered 1, 2, 3..."
        if has_think else "the lesson has no \"Think About It\" section; return an empty list."
    )
    worked_example = (
        "a short model passage or sentence followed by a step-by-step analysis."
        if lesson["subject"] == "ELA"
        else "a step-by-step problem, with a calculation using real numbers where the idea allows it."
    )
    base = WRITER_PROMPT.format(
        subject=lesson["subject"], core_standard=core_standard, topic=lesson["topic"],
        unit=lesson["unit"], lesson=lesson["content"], think_instruction=think_instruction,
        grade9_standard=grade9_standard, worked_example=worked_example,
    )
    system = [{"type": "text", "text": WRITER_SYSTEM}]
    prompt, best = base, None
    for _ in range(3):
        extras = call_json(client, spend, WRITER_MODEL, WRITER_EFFORT, system, prompt, EXTRAS_SCHEMA)
        problems = validate(extras, has_think)
        if not problems:
            return extras
        best = best or extras
        prompt = base + "\n\nYour previous attempt was rejected:\n" + "\n".join(f"- {p}" for p in problems)
    raise ValueError("additions failed validation: " + "; ".join(problems))


def replace_in_strings(obj, quote: str, correction: str) -> int:
    """Replace quote inside any string in a nested JSON structure. Returns replacements made."""
    count = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and quote in v:
                obj[k] = v.replace(quote, correction, 1)
                count += 1
            else:
                count += replace_in_strings(v, quote, correction)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and quote in v:
                obj[i] = v.replace(quote, correction, 1)
                count += 1
            else:
                count += replace_in_strings(v, quote, correction)
    return count


def fact_check(client, spend, lesson: dict, extras: dict) -> tuple[str, dict, list[str]]:
    system = [{"type": "text", "text": "You are a careful subject-matter expert and teacher."}]
    prompt = FACTCHECK_PROMPT.format(
        subject=lesson["subject"], lesson=lesson["content"], extras=json.dumps(extras, indent=1, ensure_ascii=False),
    )
    issues = call_json(client, spend, CHECKER_MODEL, CHECKER_EFFORT, system, prompt, FACTCHECK_SCHEMA)["issues"]
    content = lesson["content"]
    log = []
    for issue in issues:
        q, fix = issue["quote"], issue["correction"]
        if not issue["definitely_wrong"] or q.strip() == fix.strip():
            continue
        if q and content.count(q) == 1:
            content = content.replace(q, fix)
            status = "fixed in lesson"
        elif q and replace_in_strings(extras, q, fix):
            status = "fixed in additions"
        else:
            status = "NOT FIXED (text not found exactly)"
        log.append(f"- **{status}** — \"{q}\" → \"{fix}\" ({issue['reason']})")
    return content, extras, log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", type=int, nargs="+")
    parser.add_argument("--subjects", nargs="+", help="e.g. Physics Chemistry")
    parser.add_argument("--budget", type=float, required=True)
    args = parser.parse_args()

    ensure_schema()
    client = anthropic.Anthropic()
    conn = sqlite3.connect(DB_PATH)
    subject_filter = " or ".join("(s.name = ? and s.grade = ?)" for _ in SUBJECTS)
    params = [v for key in SUBJECTS for v in key]
    sql = (
        "select l.id, l.content, t.id, t.name, t.unit, s.name, s.grade from lessons l "
        "join topics t on t.id = l.topic_id join subjects s on s.id = t.subject_id "
        f"where l.extras is null and t.hidden = 0 and ({subject_filter})"
    )
    if args.topics:
        sql += f" and t.id in ({','.join('?' * len(args.topics))})"
        params += args.topics
    if args.subjects:
        sql += f" and s.name in ({','.join('?' * len(args.subjects))})"
        params += args.subjects
    sql += ' order by s.position, t."order"'
    lessons = [
        dict(id=r[0], content=r[1], topic_id=r[2], topic=r[3], unit=r[4], subject=r[5], grade=r[6])
        for r in conn.execute(sql, params)
    ]

    LOG_PATH.parent.mkdir(exist_ok=True)
    spend = Spend(args.budget)
    done = 0
    try:
        for i, lesson in enumerate(lessons, 1):
            # Another worker may have done this lesson since the list was read
            if conn.execute("select extras is not null from lessons where id = ?", (lesson["id"],)).fetchone()[0]:
                continue
            print(f"[{i}/{len(lessons)}] {lesson['subject']}: {lesson['topic']} ... ", end="", flush=True)
            before = spend.total
            try:
                extras = write_extras(client, spend, lesson)
                content, extras, log = fact_check(client, spend, lesson, extras)
            except BudgetExceeded:
                raise
            except Exception as e:
                print(f"FAILED — {e}", flush=True)
                continue
            vocab = extras.pop("level_up_vocab")
            with conn:
                conn.execute(
                    "update lessons set content = ?, extras = ? where id = ?",
                    (content, json.dumps(extras, ensure_ascii=False), lesson["id"]),
                )
                conn.executemany(
                    "insert into vocabulary_words (lesson_id, word, definition, part_of_speech, example_sentence, level)"
                    " values (?, ?, ?, ?, ?, 'level_up')",
                    [(lesson["id"], v["word"], v["definition"], v["part_of_speech"], v["example_sentence"]) for v in vocab],
                )
            with LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(f"\n## {lesson['subject']} — {lesson['topic']} ({datetime.now():%Y-%m-%d %H:%M})\n")
                f.write("\n".join(log) + "\n" if log else "- no errors found\n")
            done += 1
            fixes = sum("fixed" in l and "NOT" not in l for l in log)
            print(f"ok, {fixes} fact-check fixes, ${spend.total - before:.2f} (total ${spend.total:.2f})", flush=True)
    except BudgetExceeded as e:
        print(f"\nSTOPPED — {e}", flush=True)
    finally:
        print(f"\nEnriched {done} lessons. Total API cost: ${spend.total:.2f}", flush=True)
        conn.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
