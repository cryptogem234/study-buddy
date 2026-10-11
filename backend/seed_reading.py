"""
seed_reading.py
Creates the Reading Comprehension section: original passages at Core (Grade 8)
and Level Up (Grade 9) level, each with 7 multiple-choice questions tagged by
reading skill, a glossary of hard words, and an MCAS-style written response
prompt with a rubric and a model answer.

Each answer key is checked by a second model answering blind; questions it
disagrees with get one rewrite, and any that still fail are dropped.

Passages already in the database (matched by level and position) are skipped,
so the script can be re-run.

Run from the backend folder:
    python seed_reading.py --budget 8
    python seed_reading.py --only 1 --budget 1
"""
import argparse
import re
import sys

import anthropic

from database import SessionLocal, ensure_schema
import models
from expand_questions import (
    BudgetExceeded, Spend, call_json, correct_is_longest, length_giveaway, normalize,
)

WRITER_MODEL = "claude-opus-5-5"
VERIFIER_MODEL = "claude-sonnet-5-5"

SKILLS = [
    "central_idea", "inference", "textual_evidence", "vocabulary_in_context",
    "author_purpose", "text_structure", "point_of_view", "figurative_language",
    "argument_rhetoric", "character_plot",
]

# (level, genre, brief) — position is the index within its level, starting at 1
SPECS = [
    ("core", "Realistic fiction", "A 13-year-old helping at her family's diner makes a costly mistake on a busy Saturday and must decide whether to admit it. Theme: honesty and responsibility."),
    ("core", "Science fiction", "A boy on a generation spaceship discovers the 'sky' in the ship's park is a screen, and must decide whether to tell the younger kids. Theme: truth versus comfort."),
    ("core", "Historical fiction", "A 14-year-old girl working in a textile mill in Lawrence, Massachusetts, during the 1912 'Bread and Roses' strike. Accurate to the history."),
    ("core", "Mystery", "A missing science-fair trophy; the narrator solves it through small clues the reader can also notice. Built for inference."),
    ("core", "Realistic fiction", "A teen whose grandmother visits from abroad for the first time; they connect through cooking despite a language gap. Theme: connection and identity."),
    ("core", "Adventure", "Two friends on a coastal kayaking trip in Maine face a sudden fog and must make careful decisions to get back safely."),
    ("core", "Humorous fiction", "A school talent show act goes wrong in a series of escalating, funny ways, and the narrator learns something unexpected. Rich in tone and irony."),
    ("core", "Informational (science)", "How octopuses change color and texture to camouflage, and what scientists still don't understand about it."),
    ("core", "Informational (history and science)", "The Great Molasses Flood in Boston, 1919: what happened, and the physics of why a wave of molasses was so deadly (pressure, density, viscosity)."),
    ("core", "Informational (history)", "Frederick Douglass's years in New Bedford, Massachusetts, and how they shaped his life as a speaker and writer. Accurate to the history."),
    ("core", "Informational (science)", "How vaccines train the immune system, explained through a clear analogy, including how scientists test them for safety."),
    ("core", "Informational (science)", "Lightning: how static charge builds up in storm clouds, why lightning strikes where it does, and how to stay safe."),
    ("core", "Biography", "Katherine Johnson, the NASA mathematician whose calculations helped send astronauts into orbit and to the Moon. Accurate to the history."),
    ("core", "Argumentative essay", "Should towns ban gas-powered leaf blowers? A student's argument with a claim, evidence, a counterclaim and a rebuttal."),
    ("core", "Argumentative essay", "Should zoos exist? A balanced argument that weighs conservation work against animal welfare and reaches a clear claim."),
    ("core", "Opinion editorial", "Should students be paid for good grades? An editorial that takes a position and addresses the strongest objection."),
    ("core", "Persuasive speech", "A student's speech to the town council asking for darker streetlights to reduce light pollution, using science and personal appeal."),
    ("core", "Poem (free verse)", "A free-verse poem about a grandfather's hands working in a garden; vivid imagery and a turn at the end."),
    ("core", "Poem (narrative, rhymed)", "A narrative poem in rhymed quatrains about a lighthouse keeper on the night of a storm."),
    ("core", "Poem (structured)", "A poem with a clear repeating structure about running a cross-country race, built on one central metaphor."),
    ("level_up", "Literary fiction", "A story told by an unreliable narrator who insists he is not jealous of his talented younger sister; the reader sees more than he admits."),
    ("level_up", "Literary fiction", "A story told in two alternating first-person sections by two strangers on the same subway car; dramatic irony from what each doesn't know."),
    ("level_up", "Gothic fiction", "An atmospheric, slightly eerie story about a girl who inherits an old clock that runs backward; mood, foreshadowing and an ambiguous ending."),
    ("level_up", "Informational (science and ethics)", "CRISPR gene editing: how it works, what it might cure, and the ethical questions scientists are debating."),
    ("level_up", "Informational (history)", "The 1918 influenza pandemic in Boston: how it spread, how the city responded, and what historians learned. Accurate to the history."),
    ("level_up", "Informational (science)", "How scientists figured out the age of the universe, from Hubble's observations to the cosmic microwave background."),
    ("level_up", "Speech (rhetoric)", "A commencement speech to a graduating 8th grade class about why failure is necessary; strong use of ethos, pathos and logos."),
    ("level_up", "Argumentative essay", "Should students be allowed to use AI to help write school essays? A nuanced argument with concessions and a qualified claim."),
    ("level_up", "Poem (extended metaphor)", "A poem that builds one extended metaphor comparing memory to a house with many rooms; the speaker differs from the poet."),
    ("level_up", "Paired texts (historical, fictional)", "Two short original texts set in 1840s Lowell, Massachusetts: a mill owner's newspaper letter praising factory life, then a young mill worker's reply. Label them Text 1 and Text 2. For synthesizing across texts."),
]

LEVELS = {
    "core": ("Grade 8 (Common Core ELA Grade 8, Massachusetts MCAS)", "600-900", (550, 1000), "150-350"),
    "level_up": ("Grade 9 (Common Core ELA Grades 9-10)", "800-1200", (750, 1300), "200-400"),
}

QUESTION_ITEM = {
    "type": "object",
    "properties": {
        "stem": {"type": "string"},
        "options": {"type": "array", "items": {"type": "string"}},
        "correct_index": {"type": "integer"},
        "explanation": {"type": "string"},
        "skill": {"type": "string", "enum": SKILLS},
    },
    "required": ["stem", "options", "correct_index", "explanation", "skill"],
    "additionalProperties": False,
}
PASSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "text": {"type": "string"},
        "glossary": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"word": {"type": "string"}, "definition": {"type": "string"}},
                "required": ["word", "definition"],
                "additionalProperties": False,
            },
        },
        "questions": {"type": "array", "items": QUESTION_ITEM},
        "written_prompt": {"type": "string"},
        "rubric": {"type": "array", "items": {"type": "string"}},
        "model_answer": {"type": "string"},
    },
    "required": ["title", "text", "glossary", "questions", "written_prompt", "rubric", "model_answer"],
    "additionalProperties": False,
}
FIX_SCHEMA = {
    "type": "object",
    "properties": {"questions": {"type": "array", "items": QUESTION_ITEM}},
    "required": ["questions"],
    "additionalProperties": False,
}
VERIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "answers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer"},
                    "choice": {"type": "integer"},
                    "ambiguous": {"type": "boolean"},
                    "note": {"type": "string"},
                },
                "required": ["number", "choice", "ambiguous", "note"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["answers"],
    "additionalProperties": False,
}

SYSTEM = """\
You write reading comprehension practice for Study Buddy, an app used daily by a \
motivated 8th grade student in Massachusetts whose parent wants her English to be \
excellent and stretched toward 9th-grade level. Everything you write is original: \
never reproduce or closely imitate copyrighted text. Historical and scientific facts \
must be accurate."""

PROMPT = """\
Write one reading passage with questions.

Level: {level_label}
Genre: {genre}
Brief: {brief}
Length: {words} words for prose ({poem_words} words for a poem).

Passage (text):
- Plain text. Separate paragraphs (or stanzas, for poems) with one blank line. Inside \
a poem, put each line on its own line. No headings, markdown or numbering in the text.
- Write something a strong student would genuinely enjoy reading: specific details, \
real tension or a clear point, and language worth analyzing at this level.

glossary: 5-7 challenging words or phrases that appear exactly as written in the \
text, with short definitions that fit how they are used.

questions: exactly 7 multiple-choice questions in the style of the MCAS.
- Cover at least 5 different skills from: {skills}. Include at least one \
textual_evidence question ("Which sentence from the passage best supports...") whose \
options are quotations from the passage, and at least one vocabulary_in_context question.
- Every question must require reading this passage; refer to paragraphs (or stanzas) \
by number when useful, counting from 1.
- Exactly 4 options, one clearly correct. Distractors are plausible misreadings. All \
options about the same length; in most questions a WRONG option should be the longest. \
Options are shuffled when shown: never "both A and B", "all of the above", or letters.
- explanation: 2-3 sentences for a 13-year-old saying why the answer is right and why \
the most tempting wrong option is wrong.

written_prompt: one MCAS-style short-response question (answered in about 5-8 \
sentences) that asks her to make a claim about the passage and support it with at \
least two pieces of evidence from the text.
rubric: exactly 4 short criteria a teacher would use to score the response.
model_answer: a strong 5-8 sentence answer an excellent 8th grader could write."""


def word_count(text: str) -> int:
    return len(text.split())


def validate(data: dict, level: str, genre: str) -> list[str]:
    problems = []
    lo, hi = LEVELS[level][2]
    if "Poem" in genre:
        lo, hi = (120, 420)
    wc = word_count(data["text"])
    if not lo <= wc <= hi:
        problems.append(f"the passage is {wc} words; it must be within the requested length")
    qs = data["questions"]
    if len(qs) != 7:
        problems.append(f"expected exactly 7 questions, got {len(qs)}")
    if len({q["skill"] for q in qs}) < 5:
        problems.append("questions must cover at least 5 different skills")
    for i, q in enumerate(qs, 1):
        if len(q["options"]) != 4 or not 0 <= q["correct_index"] <= 3:
            problems.append(f"question {i} needs exactly 4 options and correct_index 0-3")
        elif len({normalize(o) for o in q["options"]}) != 4:
            problems.append(f"question {i} has duplicate options")
    well_formed = [q for q in qs if len(q["options"]) == 4 and 0 <= q["correct_index"] <= 3]
    longest = sum(correct_is_longest(q) for q in well_formed)
    if longest > 2 or any(length_giveaway(q) for q in well_formed):
        problems.append(
            f"in {longest} questions the correct option is the longest; in at least 5 of the 7, "
            "make a WRONG option the longest"
        )
    lower = data["text"].lower()
    missing = [g["word"] for g in data["glossary"] if g["word"].lower() not in lower]
    if missing:
        problems.append(f"glossary words not found exactly in the text: {', '.join(missing)}")
    if not 5 <= len(data["glossary"]) <= 7:
        problems.append("glossary needs 5-7 entries")
    if len(data["rubric"]) != 4:
        problems.append("rubric needs exactly 4 criteria")
    return problems


def numbered_text(text: str) -> str:
    paras = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    return "\n\n".join(f"[{i}] {p}" for i, p in enumerate(paras, 1))


def verify(client, spend, text: str, qs: list[dict]) -> list[tuple[dict, str | None]]:
    """Returns (question, None) if the blind answer matches, else (question, note)."""
    listing = []
    for i, q in enumerate(qs, 1):
        opts = "\n".join(f"  {j}. {o}" for j, o in enumerate(q["options"]))
        listing.append(f"Question {i}:\n{q['stem']}\n{opts}")
    user = (
        f"<passage>\n{numbered_text(text)}\n</passage>\n\n"
        "Answer each question about the passage. Give the number, the index (0-3) of the "
        "best option, and set ambiguous=true if more than one option could reasonably be "
        "defended or none is correct, with a one-sentence note.\n\n" + "\n\n".join(listing)
    )
    system = [{"type": "text", "text": "You are a careful English teacher checking a reading quiz answer key."}]
    answers = call_json(client, spend, VERIFIER_MODEL, "medium", system, user, VERIFY_SCHEMA)["answers"]
    by_num = {a["number"]: a for a in answers}
    out = []
    for i, q in enumerate(qs, 1):
        a = by_num.get(i)
        ok = a and a["choice"] == q["correct_index"] and not a["ambiguous"]
        out.append((q, None if ok else (a["note"] if a else "no answer")))
    return out


def make_passage(client, spend, level: str, genre: str, brief: str) -> dict:
    level_label, words, _, poem_words = LEVELS[level]
    base = PROMPT.format(
        level_label=level_label, genre=genre, brief=brief, words=words,
        poem_words=poem_words, skills=", ".join(SKILLS),
    )
    system = [{"type": "text", "text": SYSTEM}]
    prompt = base
    for _ in range(3):
        data = call_json(client, spend, WRITER_MODEL, "medium", system, prompt, PASSAGE_SCHEMA)
        problems = validate(data, level, genre)
        if not problems:
            break
        prompt = base + "\n\nYour previous attempt was rejected:\n" + "\n".join(f"- {p}" for p in problems)
    else:
        raise ValueError("failed validation: " + "; ".join(problems))

    checked = verify(client, spend, data["text"], data["questions"])
    flagged = [(q, note) for q, note in checked if note]
    good = [q for q, note in checked if not note]
    if flagged:
        fix_prompt = (
            f"<passage>\n{numbered_text(data['text'])}\n</passage>\n\n"
            "A second teacher answered these questions without the key and disagreed or found "
            "them ambiguous. Rewrite each so exactly one option is clearly correct, keeping the "
            "same skill and the same rules (4 options of similar length, a wrong option usually "
            "the longest, no letters or 'all of the above').\n\n"
            + "\n\n".join(
                f"Question: {q['stem']}\nOptions: {q['options']}\nKeyed answer: {q['options'][q['correct_index']]}\n"
                f"Teacher's note: {note}"
                for q, note in flagged
            )
        )
        fixed = call_json(client, spend, WRITER_MODEL, "medium", system, fix_prompt, FIX_SCHEMA)["questions"]
        fixed = [q for q in fixed if len(q["options"]) == 4 and 0 <= q["correct_index"] <= 3]
        good += [q for q, note in verify(client, spend, data["text"], fixed) if not note] if fixed else []
    if len(good) < 6:
        raise ValueError(f"only {len(good)} questions passed the answer check")
    data["questions"] = good
    data["dropped"] = 7 - len(good) if len(good) < 7 else 0
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=float, required=True)
    parser.add_argument("--only", type=int, nargs="+", help="spec numbers (1-30) to generate")
    args = parser.parse_args()

    ensure_schema()
    client = anthropic.Anthropic()
    db = SessionLocal()
    spend = Spend(args.budget)
    positions = {"core": 0, "level_up": 0}
    try:
        for n, (level, genre, brief) in enumerate(SPECS, 1):
            positions[level] += 1
            pos = positions[level]
            if args.only and n not in args.only:
                continue
            if db.query(models.Passage).filter_by(level=level, position=pos).first():
                continue
            print(f"[{n}/{len(SPECS)}] {level} · {genre} ... ", end="", flush=True)
            before = spend.total
            try:
                data = make_passage(client, spend, level, genre, brief)
            except BudgetExceeded:
                raise
            except Exception as e:
                print(f"FAILED — {e}", flush=True)
                continue
            passage = models.Passage(
                title=data["title"], level=level, genre=genre, text=data["text"].strip(),
                word_count=word_count(data["text"]), position=pos, glossary=data["glossary"],
                written_prompt=data["written_prompt"], rubric=data["rubric"], model_answer=data["model_answer"],
            )
            for i, q in enumerate(data["questions"], 1):
                passage.questions.append(models.PassageQuestion(
                    stem=q["stem"], options=q["options"], correct_index=q["correct_index"],
                    explanation=q["explanation"], skill=q["skill"], position=i,
                ))
            db.add(passage)
            db.commit()
            print(f"'{data['title']}' {passage.word_count} words, {len(data['questions'])} questions, "
                  f"${spend.total - before:.2f} (total ${spend.total:.2f})", flush=True)
    except BudgetExceeded as e:
        print(f"\nSTOPPED — {e}", flush=True)
    finally:
        print(f"\nTotal API cost: ${spend.total:.2f}", flush=True)
        db.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
