from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import grader
from models import Passage, PassageQuestion, PassageAttempt
from progress_rules import PASS_SCORE
from schemas import (
    PassageSummary, PassageOut, PassageAttemptIn, WrittenAnswerIn, WrittenResult,
    ReadingProgress, SkillStat,
)

router = APIRouter(tags=["reading"])

# Level Up (Grade 9) passages open once this many Core passages are passed
CORE_PASSES_TO_UNLOCK = 3


def passed(attempt: PassageAttempt) -> bool:
    return attempt.score / attempt.total >= PASS_SCORE


def core_passes(db: Session) -> int:
    attempts = db.query(PassageAttempt).join(Passage).filter(Passage.level == "core").all()
    return len({a.passage_id for a in attempts if passed(a)})


@router.get("/passages", response_model=list[PassageSummary])
def list_passages(db: Session = Depends(get_db)):
    level_up_open = core_passes(db) >= CORE_PASSES_TO_UNLOCK
    result = []
    for p in db.query(Passage).order_by(Passage.level, Passage.position).all():
        result.append(PassageSummary(
            id=p.id, title=p.title, level=p.level, genre=p.genre, word_count=p.word_count,
            position=p.position,
            best_score=max((a.score / a.total * 100 for a in p.attempts), default=None),
            attempt_count=len(p.attempts),
            passed=any(passed(a) for a in p.attempts),
            unlocked=p.level == "core" or level_up_open,
        ))
    return result


@router.get("/passages/{passage_id}", response_model=PassageOut)
def get_passage(passage_id: int, db: Session = Depends(get_db)):
    p = db.get(Passage, passage_id)
    if not p:
        raise HTTPException(404, "Passage not found")
    out = PassageOut.model_validate(p)
    out.unlocked = p.level == "core" or core_passes(db) >= CORE_PASSES_TO_UNLOCK
    return out


@router.post("/passage-attempts")
def save_passage_attempt(body: PassageAttemptIn, db: Session = Depends(get_db)):
    skills = {
        q.id: q.skill
        for q in db.query(PassageQuestion).filter(PassageQuestion.passage_id == body.passage_id).all()
    }
    attempt = PassageAttempt(
        passage_id=body.passage_id, score=body.score, total=body.total,
        answers=[{"question_id": a.question_id, "skill": skills.get(a.question_id, ""), "correct": a.correct}
                 for a in body.answers],
    )
    db.add(attempt)
    db.commit()
    return {"id": attempt.id}


@router.post("/passage-attempts/{attempt_id}/written", response_model=WrittenResult)
def grade_written(attempt_id: int, body: WrittenAnswerIn, db: Session = Depends(get_db)):
    attempt = db.get(PassageAttempt, attempt_id)
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    p = attempt.passage
    attempt.written_answer = body.answer
    result = grader.grade(p.text, p.written_prompt, p.rubric, p.model_answer, body.answer) if body.answer.strip() else None
    if result:
        attempt.written_score = result["score"]
        attempt.written_feedback = f"{result['went_well']}\n\n{result['to_improve']}"
    db.commit()
    if not result:
        return WrittenResult(graded=False)
    return WrittenResult(graded=True, score=result["score"], feedback=attempt.written_feedback)


@router.get("/reading-progress", response_model=ReadingProgress)
def reading_progress(db: Session = Depends(get_db)):
    passages = db.query(Passage).all()
    attempts = db.query(PassageAttempt).all()
    by_skill: dict[str, list[int]] = {}
    for a in attempts:
        for ans in a.answers or []:
            if ans.get("skill"):
                stat = by_skill.setdefault(ans["skill"], [0, 0])
                stat[0] += bool(ans["correct"])
                stat[1] += 1
    written = [a.written_score for a in attempts if a.written_score is not None]
    passes = core_passes(db)
    return ReadingProgress(
        passages_total=len(passages),
        passages_done=len({a.passage_id for a in attempts}),
        passages_passed=len({a.passage_id for a in attempts if passed(a)}),
        average_score=sum(a.score / a.total * 100 for a in attempts) / len(attempts) if attempts else None,
        written_average=sum(written) / len(written) if written else None,
        written_count=len(written),
        level_up_unlocked=passes >= CORE_PASSES_TO_UNLOCK,
        core_passed_needed=max(0, CORE_PASSES_TO_UNLOCK - passes),
        skills=sorted(
            (SkillStat(skill=k, correct=v[0], total=v[1]) for k, v in by_skill.items()),
            key=lambda s: s.correct / s.total,
        ),
    )
