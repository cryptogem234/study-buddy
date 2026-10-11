"""
expand_questions.py
Writes a larger, harder-to-guess quiz pool (20 questions) for topics Aashi has
NOT started yet in ELA 8, Chemistry and Biology. Each question is tagged with a
skill and a difficulty level (foundation / on_grade / challenge, where
challenge = 9th-grade level), and each answer key is double-checked by a second
model that answers the questions blind.

Generation never touches the database. It writes a JSON file plus a readable
Markdown review file into backend/generated/. A separate --save step loads an
approved JSON file into the DB, so reviewed questions are never paid for twice.

Run from the backend folder:
    # generate (no DB changes)
    python expand_questions.py generate --topics 108 150
    python expand_questions.py generate --subject ELA8 --budget 15

    # save an approved file into the DB (backs up the DB first)
    python expand_questions.py save generated/<file>.json

Requires backend/.env:
    ANTHROPIC_API_KEY=sk-ant-...
"""
import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import anthropic

HERE = Path(__file__).parent
DB_PATH = HERE / "study_buddy.db"
OUT_DIR = HERE / "generated"

load_dotenv(HERE / ".env")

QUESTIONS_PER_TOPIC = 20
BATCH_SIZE = 5
MAX_BATCH_ATTEMPTS = 3

# Mix per batch of 5 -> totals 5 foundation, 9 on_grade, 6 challenge
DIFFICULTY_PLAN = [
    {"foundation": 3, "on_grade": 2, "challenge": 0},
    {"foundation": 1, "on_grade": 3, "challenge": 1},
    {"foundation": 1, "on_grade": 2, "challenge": 2},
    {"foundation": 0, "on_grade": 2, "challenge": 3},
]

GENERATOR_EFFORT = "medium"
VERIFIER_MODEL = "claude-sonnet-5-5"
VERIFIER_EFFORT = "medium"

# $ per million tokens: (input, output). Cache writes bill at 1.25x input, reads at 0.1x.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-opus-5": (5.00, 25.00),
}

ELA_SKILLS = [
    "inference", "textual_evidence", "central_idea", "vocabulary_in_context",
    "author_purpose", "argument_rhetoric", "text_structure", "point_of_view",
    "figurative_language", "grammar_usage", "punctuation", "writing_craft",
]
SCIENCE_SKILLS = [
    "core_concept", "application", "data_interpretation", "cause_effect",
    "misconception", "real_world", "scientific_vocabulary", "experimental_design",
]

# slug -> (db subject name, grade, model, standard, skills, subject guidance)
SUBJECT_CONFIG = {
    "ELA8": (
        "ELA", 8, "claude-opus-5-5",
        "Common Core ELA Grade 8 (Massachusetts Curriculum Framework)",
        ELA_SKILLS,
        """\
- Make most questions passage-based, like the MCAS: write a short ORIGINAL passage \
(3-8 sentences) inside the stem, then ask about it. Vary passage types: argument, \
speech, news-style article, narrative, letter, poem excerpt.
- Ask questions that require reading closely, not recalling a definition: what can be \
inferred, which sentence best supports a claim, how a word's meaning is shaped by \
context, why the author included a detail, how a paragraph is organized.
- For grammar or writing topics, show a sentence or short paragraph and ask which \
revision is correct or most effective.""",
    ),
    "Chemistry": (
        "Chemistry", 8, "claude-opus-5-5", "NGSS MS-PS1 (Grade 8)",
        SCIENCE_SKILLS,
        """\
- Favor understanding over memorization: why something happens, what would change \
if a condition changed, which explanation fits the evidence.
- Use original lab or everyday scenarios. When data is needed, describe it in the \
stem as short text (e.g. "Trial 1: 20 g ... Trial 2: 35 g ...") since no images \
can be shown.
- Include experimental-design questions (variables, controls, fair tests).""",
    ),
    "Biology": (
        "Biology", 8, "claude-opus-5-5", "NGSS MS-LS (Grade 8)",
        SCIENCE_SKILLS,
        """\
- Favor understanding over memorization: how structures support functions, cause \
and effect in body systems and ecosystems, what evidence supports a claim.
- Use original lab, health or nature scenarios. When data is needed, describe it in \
the stem as short text since no images can be shown.
- Include experimental-design questions (variables, controls, fair tests).""",
    ),
}

SYSTEM_TEMPLATE = """\
You write quiz questions for Study Buddy, a study app used daily by an 8th grade \
student in Massachusetts. She is motivated and her parent wants her stretched toward \
9th-grade level. Standard: {standard}.

The topic is "{topic}" (unit: {unit}). She has read the lesson below before taking \
the quiz. Base questions on what the lesson teaches; challenge questions may go a \
step beyond it but must be answerable by reasoning from it.

Difficulty levels:
- foundation: checks the core ideas of the lesson directly.
- on_grade: typical 8th grade test question; requires applying the idea.
- challenge: 9th-grade level (Common Core grades 9-10 / NGSS high school); multi-step \
reasoning, subtler distractors, or an unfamiliar context.

Subject guidance:
{guidance}

Rules for every question:
- Exactly 4 answer options with ONE clearly correct answer. Distractors must be \
plausible and reflect real mistakes students make.
- All 4 options must be about the same length and level of detail (within a few words \
of each other). A student must not be able to find the answer by picking the \
longest, most specific or most qualified option. In most questions a WRONG option \
should be the longest one; the correct answer should be the longest in no more than \
about one question out of four.
- Options are shuffled when shown, so never write "both A and B", "all of the \
above" or "none of the above", and never refer to options by letter.
- Plain text only: no markdown, asterisks or bold. Put quoted words or passages in \
double quotes. Use a blank line between a passage and the question.
- explanation: 2-3 sentences in a friendly tone for a 13-year-old. Say why the \
answer is correct and why the most tempting wrong option is wrong.
- skill: the single best tag from: {skills}.
- All passages and scenarios must be original. Do not reproduce copyrighted text.

<lesson>
{lesson}
</lesson>"""

BATCH_TEMPLATE = """\
Write exactly {n} new questions with this difficulty mix: {mix}.
Use a variety of skills; do not test the same idea twice.{avoid}"""

QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "stem": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}},
                    "correct_index": {"type": "integer"},
                    "explanation": {"type": "string"},
                    "skill": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["foundation", "on_grade", "challenge"]},
                },
                "required": ["stem", "options", "correct_index", "explanation", "skill", "difficulty"],
                "additionalProperties": False,
            },
        }
    },
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


class BudgetExceeded(Exception):
    pass


class Spend:
    def __init__(self, budget: float | None):
        self.budget = budget
        self.total = 0.0

    def add(self, requested_model: str, response) -> float:
        model = response.model if response.model in PRICES else requested_model
        inp, out = PRICES[model]
        u = response.usage
        cost = (
            u.input_tokens * inp
            + (u.cache_creation_input_tokens or 0) * inp * 1.25
            + (u.cache_read_input_tokens or 0) * inp * 0.1
            + u.output_tokens * out
        ) / 1_000_000
        self.total += cost
        if self.budget is not None and self.total > self.budget:
            raise BudgetExceeded(f"Spent ${self.total:.2f}, over the ${self.budget:.2f} budget")
        return cost


def call_json(client, spend: Spend, model: str, effort: str, system: list, user: str, schema: dict) -> dict:
    response = client.beta.messages.create(
        model=model,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        betas=["server-side-fallback-2026-07-01"],
        extra_body={"fallbacks": "default"},
    )
    spend.add(model, response)
    if response.stop_reason == "refusal":
        raise ValueError("model declined the request")
    if response.stop_reason == "max_tokens":
        raise ValueError("response was cut off at max_tokens")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def words(s: str) -> int:
    return len(s.split())


def length_giveaway(q: dict) -> bool:
    """True if the correct option is clearly the longest one (a guessable pattern)."""
    lens = [words(o) for o in q["options"]]
    correct = lens[q["correct_index"]]
    others = [l for i, l in enumerate(lens) if i != q["correct_index"]]
    return correct > max(others) and correct >= 1.25 * (sum(others) / len(others))


def correct_is_longest(q: dict) -> bool:
    """True if the correct option has the most characters (ties count). By chance this is ~25%."""
    lens = [len(o) for o in q["options"]]
    return lens[q["correct_index"]] == max(lens)


def validate(qs: list[dict], n: int, mix: dict, skills: list[str], seen: set[str]) -> list[str]:
    problems = []
    if len(qs) != n:
        problems.append(f"expected {n} questions, got {len(qs)}")
    counts = {k: 0 for k in mix}
    for i, q in enumerate(qs, 1):
        if len(q["options"]) != 4:
            problems.append(f"question {i} has {len(q['options'])} options, needs exactly 4")
            continue
        if not 0 <= q["correct_index"] <= 3:
            problems.append(f"question {i} has correct_index {q['correct_index']}, must be 0-3")
        if len({normalize(o) for o in q["options"]}) != 4:
            problems.append(f"question {i} has duplicate options")
        if q["skill"] not in skills:
            problems.append(f"question {i} skill '{q['skill']}' is not in the allowed list")
        if normalize(q["stem"]) in seen:
            problems.append(f"question {i} repeats an earlier question")
        counts[q["difficulty"]] = counts.get(q["difficulty"], 0) + 1
    if counts != mix:
        problems.append(f"difficulty mix was {counts}, needed {mix}")
    well_formed = [q for q in qs if len(q["options"]) == 4 and 0 <= q["correct_index"] <= 3]
    giveaways = sum(length_giveaway(q) for q in well_formed)
    longest = sum(correct_is_longest(q) for q in well_formed)
    if giveaways > 0 or longest > max(1, len(qs) * 2 // 5):
        problems.append(
            f"in {longest} of {len(qs)} questions the correct option is the longest (by character "
            f"count), so a student could guess by picking the longest. In at least {len(qs) - max(1, len(qs) * 2 // 5)} "
            f"of the {len(qs)} questions, make a WRONG option the longest one"
        )
    return problems


def generate_batch(client, spend, model, system, n, mix, skills, seen_stems: list[str]) -> list[dict]:
    mix_text = ", ".join(f"{v} {k}" for k, v in mix.items() if v)
    avoid = ""
    if seen_stems:
        listed = "\n".join(f"- {s[:160]}" for s in seen_stems)
        avoid = f"\n\nThese questions already exist; do not repeat or closely rephrase them:\n{listed}"
    base = BATCH_TEMPLATE.format(n=n, mix=mix_text, avoid=avoid)
    seen = {normalize(s) for s in seen_stems}

    prompt, best, best_problems = base, None, None
    for _ in range(MAX_BATCH_ATTEMPTS):
        qs = call_json(client, spend, model, GENERATOR_EFFORT, system, prompt, QUESTION_SCHEMA)["questions"]
        problems = validate(qs, n, mix, skills, seen)
        if not problems:
            return qs
        if best is None or len(problems) < len(best_problems):
            best, best_problems = qs, problems
        prompt = base + "\n\nYour previous attempt was rejected:\n" + "\n".join(f"- {p}" for p in problems)
    # Keep only the individually valid questions from the best attempt
    return [
        q for q in best
        if len(q["options"]) == 4 and 0 <= q["correct_index"] <= 3
        and q["skill"] in skills and normalize(q["stem"]) not in seen
        and len({normalize(o) for o in q["options"]}) == 4
    ]


def verify(client, spend, qs: list[dict]) -> list[dict]:
    """A second model answers blind. Returns qs annotated with verifier results."""
    listing = []
    for i, q in enumerate(qs, 1):
        opts = "\n".join(f"  {j}. {o}" for j, o in enumerate(q["options"]))
        listing.append(f"Question {i}:\n{q['stem']}\n{opts}")
    user = (
        "Answer each multiple-choice question below. For each, give the number, the index "
        "(0-3) of the best option, and set ambiguous=true if more than one option could "
        "reasonably be defended or none is correct, with a one-sentence note.\n\n"
        + "\n\n".join(listing)
    )
    system = [{"type": "text", "text": "You are a careful teacher checking a quiz answer key."}]
    answers = call_json(client, spend, VERIFIER_MODEL, VERIFIER_EFFORT, system, user, VERIFY_SCHEMA)["answers"]
    by_num = {a["number"]: a for a in answers}
    for i, q in enumerate(qs, 1):
        a = by_num.get(i)
        q["verified"] = bool(a) and a["choice"] == q["correct_index"] and not a["ambiguous"]
        q["verifier_note"] = "" if q["verified"] else (a["note"] if a else "no verifier answer")
    return qs


def load_topic(conn, topic_id: int):
    row = conn.execute(
        """select t.id, t.name, t.unit, s.name, s.grade,
                  (select count(*) from quiz_attempts a where a.topic_id = t.id),
                  (select group_concat(content, char(10) || char(10)) from lessons l where l.topic_id = t.id)
           from topics t join subjects s on s.id = t.subject_id where t.id = ?""",
        (topic_id,),
    ).fetchone()
    if not row:
        raise SystemExit(f"Topic {topic_id} not found")
    return dict(id=row[0], name=row[1], unit=row[2], subject=row[3], grade=row[4], attempts=row[5], lesson=row[6] or "")


def slug_for(topic) -> str:
    for slug, cfg in SUBJECT_CONFIG.items():
        if cfg[0] == topic["subject"] and cfg[1] == topic["grade"]:
            return slug
    raise SystemExit(f"Topic {topic['id']} ({topic['subject']} {topic['grade']}) is not in an expandable subject")


def generate_topic(client, spend, topic) -> list[dict]:
    _, _, model, standard, skills, guidance = SUBJECT_CONFIG[slug_for(topic)]
    system = [{
        "type": "text",
        "text": SYSTEM_TEMPLATE.format(
            standard=standard, topic=topic["name"], unit=topic["unit"],
            guidance=guidance, skills=", ".join(skills), lesson=topic["lesson"],
        ),
        "cache_control": {"type": "ephemeral"},
    }]

    kept: list[dict] = []
    for mix in DIFFICULTY_PLAN:
        batch = generate_batch(client, spend, model, system, BATCH_SIZE, mix, skills, [q["stem"] for q in kept])
        kept.extend(verify(client, spend, batch))

    # One top-up round to replace questions the verifier disagreed with
    flagged = [q for q in kept if not q["verified"]]
    if flagged:
        mix = {"foundation": 0, "on_grade": 0, "challenge": 0}
        for q in flagged:
            mix[q["difficulty"]] += 1
        good = [q for q in kept if q["verified"]]
        replacements = generate_batch(
            client, spend, model, system, len(flagged), mix, skills, [q["stem"] for q in kept]
        )
        good.extend(q for q in verify(client, spend, replacements) if q["verified"])
        kept = good + [q for q in flagged]  # flagged stay in the file for review, but are not saved
    return kept


def write_review(path: Path, results: list[dict], spend: Spend):
    lines = [f"# Question review — {datetime.now():%Y-%m-%d %H:%M}", "", f"Total API cost: ${spend.total:.2f}", ""]
    for r in results:
        qs = r["questions"]
        ok = [q for q in qs if q["verified"]]
        longest = sum(correct_is_longest(q) for q in ok)
        diff = {d: sum(q["difficulty"] == d for q in ok) for d in ("foundation", "on_grade", "challenge")}
        lines += [
            f"## {r['subject']} {r['grade']} — {r['topic_name']} (topic {r['topic_id']})", "",
            f"- Verified questions: {len(ok)} (flagged and excluded: {len(qs) - len(ok)})",
            f"- Difficulty: {diff['foundation']} foundation, {diff['on_grade']} on grade, {diff['challenge']} challenge",
            f"- Correct answer is the longest option: {longest} of {len(ok)} (fair is about 25%)",
            f"- Cost: ${r['cost']:.2f}", "",
        ]
        for i, q in enumerate(qs, 1):
            tag = "" if q["verified"] else f"  **FLAGGED — {q['verifier_note']}**"
            lines.append(f"### {i}. [{q['difficulty']} · {q['skill']}]{tag}")
            lines.append("")
            lines.append(q["stem"])
            lines.append("")
            for j, o in enumerate(q["options"]):
                mark = " ✅" if j == q["correct_index"] else ""
                lines.append(f"- {'ABCD'[j]}. {o}{mark}")
            lines += ["", f"*{q['explanation']}*", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def cmd_generate(args):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ERROR: ANTHROPIC_API_KEY not found in backend/.env")
    client = anthropic.Anthropic()
    conn = sqlite3.connect(DB_PATH)

    if args.topics:
        topic_ids = args.topics
    else:
        name, grade = SUBJECT_CONFIG[args.subject][:2]
        topic_ids = [r[0] for r in conn.execute(
            """select t.id from topics t join subjects s on s.id = t.subject_id
               where s.name = ? and s.grade = ? order by t."order" """, (name, grade))]

    topics = [load_topic(conn, t) for t in topic_ids]
    conn.close()
    started = [t for t in topics if t["attempts"] > 0]
    topics = [t for t in topics if t["attempts"] == 0]
    for t in started:
        print(f"Skipping '{t['name']}' — Aashi has already taken its quiz.")

    OUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    json_path = OUT_DIR / f"questions-{stamp}.json"
    md_path = OUT_DIR / f"questions-{stamp}.md"

    spend = Spend(args.budget)
    results = []
    try:
        for i, t in enumerate(topics, 1):
            print(f"[{i}/{len(topics)}] {t['subject']} {t['grade']}: {t['name']} ... ", end="", flush=True)
            before = spend.total
            try:
                qs = generate_topic(client, spend, t)
            except BudgetExceeded:
                raise
            except Exception as e:
                print(f"FAILED — {e}")
                continue
            results.append(dict(
                topic_id=t["id"], topic_name=t["name"], subject=t["subject"], grade=t["grade"],
                cost=spend.total - before, questions=qs,
            ))
            ok = sum(q["verified"] for q in qs)
            print(f"{ok} verified, {len(qs) - ok} flagged, ${spend.total - before:.2f} (total ${spend.total:.2f})")
            json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    except BudgetExceeded as e:
        print(f"\nSTOPPED — {e}")
    finally:
        if results:
            json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            write_review(md_path, results, spend)
            print(f"\nWrote {json_path.name} and {md_path.name}")
        print(f"Total API cost: ${spend.total:.2f}")


def cmd_save(args):
    results = json.loads(Path(args.file).read_text(encoding="utf-8"))
    backup = DB_PATH.with_name(f"study_buddy.backup-{datetime.now():%Y%m%d-%H%M%S}.db")
    shutil.copy2(DB_PATH, backup)
    print(f"Backed up database to {backup.name}")

    conn = sqlite3.connect(DB_PATH)
    cols = {r[1] for r in conn.execute("pragma table_info(questions)")}
    with conn:
        if "skill" not in cols:
            conn.execute("alter table questions add column skill varchar(50) default ''")
        if "difficulty" not in cols:
            conn.execute("alter table questions add column difficulty varchar(20) default ''")
        for r in results:
            attempts = conn.execute("select count(*) from quiz_attempts where topic_id = ?", (r["topic_id"],)).fetchone()[0]
            if attempts:
                print(f"Skipping '{r['topic_name']}' — Aashi has taken this quiz since it was generated.")
                continue
            qs = [q for q in r["questions"] if q["verified"]]
            if len(qs) < 10:
                print(f"Skipping '{r['topic_name']}' — only {len(qs)} verified questions.")
                continue
            conn.execute("delete from questions where topic_id = ?", (r["topic_id"],))
            conn.executemany(
                "insert into questions (topic_id, stem, options, correct_index, explanation, skill, difficulty)"
                " values (?, ?, ?, ?, ?, ?, ?)",
                [(r["topic_id"], q["stem"], json.dumps(q["options"], ensure_ascii=False), q["correct_index"],
                  q["explanation"], q["skill"], q["difficulty"]) for q in qs],
            )
            print(f"Saved {len(qs)} questions for '{r['topic_name']}'")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    group = g.add_mutually_exclusive_group(required=True)
    group.add_argument("--topics", type=int, nargs="+")
    group.add_argument("--subject", choices=SUBJECT_CONFIG)
    g.add_argument("--budget", type=float, default=None, help="stop if API cost exceeds this many dollars")
    s = sub.add_parser("save")
    s.add_argument("file")
    args = parser.parse_args()
    {"generate": cmd_generate, "save": cmd_save}[args.cmd](args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
