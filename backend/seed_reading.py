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
import json
import re
import sys
import time

import anthropic

from database import SessionLocal, ensure_schema
import models
from expand_questions import (
    PRICES, BudgetExceeded, Spend, call_json, correct_is_longest, length_giveaway, normalize,
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
    # Second set (positions continue after the first 30)
    ("core", "Realistic fiction", "A girl on her school's robotics team freezes during the regional competition, and a quiet teammate helps in an unexpected way. Theme: courage and teamwork."),
    ("core", "Historical fiction", "A boy in Lexington, Massachusetts, on the night of April 18, 1775, whose family is divided between Patriots and Loyalists. Accurate to the history."),
    ("core", "Realistic fiction", "Twin sisters try out for the single open spot on the debate team; told by the younger twin. Theme: rivalry and loyalty."),
    ("core", "Fantasy", "A town library that lends out other people's memories instead of books; a girl borrows one that changes how she sees her grandfather."),
    ("core", "Science fiction", "A student's AI tutor starts giving slightly wrong answers on purpose to see whether she is really thinking. Theme: independent thinking."),
    ("core", "Realistic fiction", "A soccer goalie benched after a costly mistake learns something from her grandmother's story about failure."),
    ("core", "Mystery", "Strange tracks in fresh snow on a Vermont farm; the narrator and her cousin work out what made them. Built for inference."),
    ("core", "Informational (science)", "How honeybees communicate the location of flowers with the waggle dance, and how scientists decoded it."),
    ("core", "Informational (science)", "Why the Leaning Tower of Pisa leans, and how engineers kept it from falling (center of gravity, soil, forces)."),
    ("core", "Informational (science)", "The chemistry of baking: how yeast, carbon dioxide and gluten make bread rise."),
    ("core", "Informational (history)", "The Boston Tea Party: what actually happened in December 1773 and why it mattered. Accurate to the history."),
    ("core", "Informational (history)", "Clara Barton of Oxford, Massachusetts: battlefield nurse and founder of the American Red Cross. Accurate to the history."),
    ("core", "Informational (science)", "How noise-cancelling headphones use sound waves to cancel noise (wave interference), explained clearly."),
    ("core", "Biography", "Mae Jemison, physician, engineer and the first African American woman in space. Accurate to the history."),
    ("core", "Argumentative essay", "Should schools replace letter grades with written feedback? A student's argument with a counterclaim and rebuttal."),
    ("core", "Argumentative essay", "Should cities add protected bike lanes even when it means removing street parking?"),
    ("core", "Opinion editorial", "Should kids under 14 be allowed to have social media accounts? An editorial that takes a clear position."),
    ("core", "Persuasive speech", "A student's speech asking the school committee to start a cafeteria composting program, using data and personal appeal."),
    ("core", "Poem (free verse)", "A free-verse poem about the first snow of the year on a New England morning; strong sensory imagery."),
    ("core", "Poem (structured)", "A 14-line rhymed poem about a public library at closing time, with a turn near the end."),
    ("level_up", "Literary fiction", "A story told in the second person (\"you\") about the first day at a new high school; the unusual point of view is central to its effect."),
    ("level_up", "Literary fiction", "An older woman walks through her childhood home before it is sold; the story moves between present and memory (nonlinear structure)."),
    ("level_up", "Satire", "A satirical, news-style story about a town council that bans boredom; irony and exaggeration make a serious point."),
    ("level_up", "Science fiction", "A scientist finds she can talk to her teenage self over an old radio for five minutes a night; theme of regret and choice."),
    ("level_up", "Informational (science)", "Antibiotic resistance: how natural selection in bacteria makes some medicines stop working, and what can be done."),
    ("level_up", "Informational (science)", "Nuclear fusion: how it powers the Sun and why building a fusion power plant on Earth is so hard."),
    ("level_up", "Informational (history and science)", "The women 'computers' of the Harvard College Observatory, including Henrietta Leavitt and Annie Jump Cannon, and what they discovered. Accurate to the history."),
    ("level_up", "Speech (rhetoric)", "A speech to high school seniors about why voting matters, using ethos, pathos and logos and anticipating objections."),
    ("level_up", "Argumentative essay", "Is it ever right to break a rule? A nuanced essay that weighs examples, makes concessions and reaches a qualified claim."),
    ("level_up", "Poem (dramatic monologue)", "A dramatic monologue spoken by an old oak tree the night before it is cut down; the speaker is clearly not the poet."),
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


VERIFY_SYSTEM = [{"type": "text", "text": "You are a careful English teacher checking a reading quiz answer key."}]


def verify_prompt(text: str, qs: list[dict]) -> str:
    listing = []
    for i, q in enumerate(qs, 1):
        opts = "\n".join(f"  {j}. {o}" for j, o in enumerate(q["options"]))
        listing.append(f"Question {i}:\n{q['stem']}\n{opts}")
    return (
        f"<passage>\n{numbered_text(text)}\n</passage>\n\n"
        "Answer each question about the passage. Give the number, the index (0-3) of the "
        "best option, and set ambiguous=true if more than one option could reasonably be "
        "defended or none is correct, with a one-sentence note.\n\n" + "\n\n".join(listing)
    )


def judge(qs: list[dict], answers: list[dict]) -> list[tuple[dict, str | None]]:
    """(question, None) if the blind answer matches the key, else (question, note)."""
    by_num = {a["number"]: a for a in answers}
    out = []
    for i, q in enumerate(qs, 1):
        a = by_num.get(i)
        ok = a and a["choice"] == q["correct_index"] and not a["ambiguous"]
        out.append((q, None if ok else (a["note"] if a else "no answer")))
    return out


def fix_prompt(text: str, flagged: list[tuple[dict, str]]) -> str:
    return (
        f"<passage>\n{numbered_text(text)}\n</passage>\n\n"
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


def verify(client, spend, text: str, qs: list[dict]) -> list[tuple[dict, str | None]]:
    answers = call_json(client, spend, VERIFIER_MODEL, "medium", VERIFY_SYSTEM, verify_prompt(text, qs), VERIFY_SCHEMA)["answers"]
    return judge(qs, answers)


def make_passage(client, spend, level: str, genre: str, brief: str) -> dict:
    base = base_prompt(level, genre, brief)
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
        fixed = call_json(client, spend, WRITER_MODEL, "medium", system, fix_prompt(data["text"], flagged), FIX_SCHEMA)["questions"]
        fixed = [q for q in fixed if len(q["options"]) == 4 and 0 <= q["correct_index"] <= 3]
        good += [q for q, note in verify(client, spend, data["text"], fixed) if not note] if fixed else []
    if len(good) < 6:
        raise ValueError(f"only {len(good)} questions passed the answer check")
    data["questions"] = good
    data["dropped"] = 7 - len(good) if len(good) < 7 else 0
    return data


def base_prompt(level: str, genre: str, brief: str) -> str:
    level_label, words, _, poem_words = LEVELS[level]
    return PROMPT.format(
        level_label=level_label, genre=genre, brief=brief, words=words,
        poem_words=poem_words, skills=", ".join(SKILLS),
    )


def save_passage(db, level: str, genre: str, pos: int, data: dict) -> models.Passage:
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
    return passage


def missing_specs(db, only):
    """(spec number, level, genre, brief, position) for every passage not yet in the database."""
    positions = {"core": 0, "level_up": 0}
    out = []
    for n, (level, genre, brief) in enumerate(SPECS, 1):
        positions[level] += 1
        if only and n not in only:
            continue
        if not db.query(models.Passage).filter_by(level=level, position=positions[level]).first():
            out.append((n, level, genre, brief, positions[level]))
    return out


# ── Batch mode: same steps as make_passage, sent through the Message Batches API ──
# at half price. Each step is one batch for all passages that need it.

BATCH_DISCOUNT = 0.5


def batch_cost(model: str, usage) -> float:
    inp, out = PRICES[model]
    return BATCH_DISCOUNT * (
        usage.input_tokens * inp
        + (usage.cache_creation_input_tokens or 0) * inp * 1.25
        + (usage.cache_read_input_tokens or 0) * inp * 0.1
        + usage.output_tokens * out
    ) / 1_000_000


def run_batch(client, label: str, items: dict) -> tuple[dict, float]:
    """items: custom_id -> (model, system, prompt, schema). Returns (custom_id -> parsed JSON, cost)."""
    if not items:
        return {}, 0.0
    requests = [
        {
            "custom_id": cid,
            "params": {
                "model": model,
                "max_tokens": 16000,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
                "output_config": {"effort": "medium", "format": {"type": "json_schema", "schema": schema}},
            },
        }
        for cid, (model, system, prompt, schema) in items.items()
    ]
    batch = client.messages.batches.create(requests=requests)
    print(f"  {label}: sent {len(requests)} requests (batch {batch.id}) ", end="", flush=True)
    while batch.processing_status != "ended":
        time.sleep(30)
        batch = client.messages.batches.retrieve(batch.id)
        print(".", end="", flush=True)
    results, cost = {}, 0.0
    for r in client.messages.batches.results(batch.id):
        if r.result.type != "succeeded":
            continue
        msg = r.result.message
        cost += batch_cost(items[r.custom_id][0], msg.usage)
        if msg.stop_reason in ("refusal", "max_tokens"):
            continue
        try:
            results[r.custom_id] = json.loads(next(b.text for b in msg.content if b.type == "text"))
        except (StopIteration, json.JSONDecodeError):
            continue
    print(f" {len(results)} ok, ${cost:.2f}", flush=True)
    return results, cost


def run_batch_mode(client, db, specs, budget: float):
    system = [{"type": "text", "text": SYSTEM}]
    total = 0.0
    info = {str(n): (level, genre, brief, pos) for n, level, genre, brief, pos in specs}
    feedback: dict[str, list[str]] = {}
    drafts: dict[str, dict] = {}

    # 1. Write passages; anything that fails validation is resent with the reasons (up to 3 rounds)
    pending = set(info)
    for round_no in range(1, 4):
        if not pending or total > budget:
            break
        items = {}
        for cid in pending:
            level, genre, brief, _ = info[cid]
            prompt = base_prompt(level, genre, brief)
            if feedback.get(cid):
                prompt += "\n\nYour previous attempt was rejected:\n" + "\n".join(f"- {p}" for p in feedback[cid])
            items[cid] = (WRITER_MODEL, system, prompt, PASSAGE_SCHEMA)
        results, cost = run_batch(client, f"write passages (round {round_no})", items)
        total += cost
        for cid, data in results.items():
            problems = validate(data, info[cid][0], info[cid][1])
            if problems:
                feedback[cid] = problems
            else:
                drafts[cid] = data
                pending.discard(cid)

    # 2. Second model answers every question blind
    results, cost = run_batch(client, "check answer keys", {
        cid: (VERIFIER_MODEL, VERIFY_SYSTEM, verify_prompt(d["text"], d["questions"]), VERIFY_SCHEMA)
        for cid, d in drafts.items()
    })
    total += cost
    good: dict[str, list[dict]] = {}
    flagged: dict[str, list[tuple[dict, str]]] = {}
    for cid, d in drafts.items():
        if cid not in results:
            continue
        checked = judge(d["questions"], results[cid]["answers"])
        good[cid] = [q for q, note in checked if not note]
        bad = [(q, note) for q, note in checked if note]
        if bad:
            flagged[cid] = bad

    # 3. Rewrite flagged questions once, then check the rewrites
    if flagged and total <= budget:
        fixes, cost = run_batch(client, "rewrite flagged questions", {
            cid: (WRITER_MODEL, system, fix_prompt(drafts[cid]["text"], bad), FIX_SCHEMA)
            for cid, bad in flagged.items()
        })
        total += cost
        fixed = {
            cid: [q for q in f["questions"] if len(q["options"]) == 4 and 0 <= q["correct_index"] <= 3]
            for cid, f in fixes.items()
        }
        fixed = {cid: qs for cid, qs in fixed.items() if qs}
        results, cost = run_batch(client, "check rewrites", {
            cid: (VERIFIER_MODEL, VERIFY_SYSTEM, verify_prompt(drafts[cid]["text"], qs), VERIFY_SCHEMA)
            for cid, qs in fixed.items()
        })
        total += cost
        for cid, qs in fixed.items():
            if cid in results:
                good[cid] += [q for q, note in judge(qs, results[cid]["answers"]) if not note]

    # 4. Save every passage with at least 6 checked questions
    saved = 0
    for cid in sorted(good, key=int):
        level, genre, _, pos = info[cid]
        if len(good[cid]) < 6:
            print(f"[{cid}] dropped — only {len(good[cid])} questions passed the answer check")
            continue
        data = dict(drafts[cid], questions=good[cid])
        p = save_passage(db, level, genre, pos, data)
        saved += 1
        print(f"[{cid}/{len(SPECS)}] {level} · {genre}: '{p.title}' {p.word_count} words, {len(good[cid])} questions")
    for cid in sorted(set(info) - set(good), key=int):
        print(f"[{cid}] FAILED — {'; '.join(feedback.get(cid, ['no valid draft']))}")
    print(f"\nSaved {saved} of {len(info)} passages. Total API cost: ${total:.2f}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=float, required=True)
    parser.add_argument("--only", type=int, nargs="+", help="spec numbers to generate")
    parser.add_argument("--batch", action="store_true", help="use the Message Batches API (half price, slower)")
    args = parser.parse_args()

    ensure_schema()
    client = anthropic.Anthropic()
    db = SessionLocal()
    specs = missing_specs(db, args.only)
    if args.batch:
        try:
            run_batch_mode(client, db, specs, args.budget)
        finally:
            db.close()
        return

    spend = Spend(args.budget)
    try:
        for n, level, genre, brief, pos in specs:
            print(f"[{n}/{len(SPECS)}] {level} · {genre} ... ", end="", flush=True)
            before = spend.total
            try:
                data = make_passage(client, spend, level, genre, brief)
            except BudgetExceeded:
                raise
            except Exception as e:
                print(f"FAILED — {e}", flush=True)
                continue
            passage = save_passage(db, level, genre, pos, data)
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
