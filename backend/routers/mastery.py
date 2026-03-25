from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
import random
import json

from database import get_db
from models import Question, TopicMastery, LessonCard

router = APIRouter()


# ─── helpers ──────────────────────────────────────────────────────────────────

def _difficulty_pool(mastery_level: str) -> list:
    return {
        "beginner":   ["easy"],
        "developing": ["easy", "medium"],
        "proficient": ["medium", "hard"],
        "mastered":   ["hard"],
    }.get(mastery_level, ["easy"])


def recalculate_mastery(mastery: TopicMastery) -> TopicMastery:
    """Update mastery_level and current_difficulty based on accuracy."""
    if mastery.total_attempts == 0:
        return mastery
    accuracy = mastery.correct_count / mastery.total_attempts
    mastery.needs_review = accuracy < 0.65 and mastery.total_attempts >= 5

    if accuracy >= 0.85 and mastery.total_attempts >= 5:
        mastery.mastery_level    = "mastered"
        mastery.current_difficulty = "hard"
    elif accuracy >= 0.65:
        mastery.mastery_level    = "proficient"
        mastery.current_difficulty = "hard" if accuracy >= 0.80 else "medium"
    elif accuracy >= 0.40:
        mastery.mastery_level    = "developing"
        mastery.current_difficulty = "medium" if accuracy >= 0.55 else "easy"
    else:
        mastery.mastery_level    = "beginner"
        mastery.current_difficulty = "easy"
    return mastery


# ─── schema ───────────────────────────────────────────────────────────────────

class TopicMasteryOut(BaseModel):
    id: int
    subject: str
    topic: str
    total_attempts: int
    correct_count: int
    mastery_level: str
    current_difficulty: str
    needs_review: bool
    streak: int
    accuracy: float

    class Config:
        from_attributes = True


# ─── routes ───────────────────────────────────────────────────────────────────

@router.get("/mastery", response_model=list[TopicMasteryOut])
def get_mastery(
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Return all topic-mastery records (optionally filtered by subject)."""
    q = db.query(TopicMastery)
    if subject:
        q = q.filter(func.lower(TopicMastery.subject) == subject.lower())
    result = []
    for m in q.all():
        acc = m.correct_count / m.total_attempts if m.total_attempts else 0.0
        result.append(TopicMasteryOut(
            id=m.id, subject=m.subject, topic=m.topic,
            total_attempts=m.total_attempts, correct_count=m.correct_count,
            mastery_level=m.mastery_level, current_difficulty=m.current_difficulty,
            needs_review=m.needs_review, streak=m.streak,
            accuracy=round(acc * 100, 1),
        ))
    return result


@router.get("/quiz/adaptive")
def build_adaptive_quiz(
    subject: str = Query(...),
    limit: int = Query(10, ge=5, le=20),
    db: Session = Depends(get_db),
):
    """
    Return a personalised list of questions for the given subject.

    Composition (best-effort):
      • 40 %  from weak / needs-review topics  (accuracy < 65 %)
      • 30 %  from topics in progress          (developing / proficient)
      • 20 %  from topics never attempted       (new)
      •  10%  from mastered topics              (review)

    Falls back to random questions from the subject if not enough content
    exists for a given bucket.
    """
    masteries: dict[str, TopicMastery] = {
        m.topic: m
        for m in db.query(TopicMastery).filter(
            func.lower(TopicMastery.subject) == subject.lower()
        ).all()
    }

    topics: list[str] = [
        t[0] for t in db.query(Question.topic)
        .filter(func.lower(Question.subject) == subject.lower())
        .distinct().all()
    ]

    weak, new_t, developing, proficient, mastered = [], [], [], [], []
    for topic in topics:
        if topic not in masteries:
            new_t.append(topic)
        else:
            m = masteries[topic]
            acc = m.correct_count / m.total_attempts if m.total_attempts else 0.0
            if m.needs_review or (acc < 0.65 and m.total_attempts >= 3):
                weak.append(topic)
            elif m.mastery_level == "mastered":
                mastered.append(topic)
            elif m.mastery_level == "proficient":
                proficient.append(topic)
            else:
                developing.append(topic)

    selected: list[Question] = []
    used_ids: set[int] = set()

    def pick(topic_list: list, diffs: Optional[list], cap: int):
        random.shuffle(topic_list)
        for topic in topic_list:
            if len(selected) >= cap:
                break
            m = masteries.get(topic)
            pool = diffs if diffs else _difficulty_pool(
                m.mastery_level if m else "beginner"
            )
            q = (
                db.query(Question)
                .filter(
                    func.lower(Question.subject) == subject.lower(),
                    Question.topic == topic,
                    Question.difficulty.in_(pool),
                )
                .all()
            )
            if used_ids:
                q = [x for x in q if x.id not in used_ids]
            random.shuffle(q)
            for item in q[:2]:
                if len(selected) < cap:
                    selected.append(item)
                    used_ids.add(item.id)

    pick(weak,        None,     int(limit * 0.40))
    pick(developing,  None,     int(limit * 0.70))
    pick(new_t,       ["easy"], int(limit * 0.90))
    pick(proficient,  None,     int(limit * 0.95))
    pick(mastered,    ["hard"], limit)

    # fill any remaining slots with random questions not yet selected
    if len(selected) < limit:
        rest = (
            db.query(Question)
            .filter(func.lower(Question.subject) == subject.lower())
            .all()
        )
        rest = [x for x in rest if x.id not in used_ids]
        random.shuffle(rest)
        selected.extend(rest[: limit - len(selected)])

    random.shuffle(selected)
    return [
        {
            "id": q.id, "subject": q.subject, "topic": q.topic,
            "difficulty": q.difficulty, "question_text": q.question_text,
            "option_a": q.option_a, "option_b": q.option_b,
            "option_c": q.option_c, "option_d": q.option_d,
        }
        for q in selected[:limit]
    ]


@router.get("/lessons")
def get_lesson(
    subject: str = Query(...),
    topic: str = Query(...),
    db: Session = Depends(get_db),
):
    """Return the lesson card for a subject/topic, or null if none exists."""
    lesson = (
        db.query(LessonCard)
        .filter(
            func.lower(LessonCard.subject) == subject.lower(),
            func.lower(LessonCard.topic) == topic.lower(),
        )
        .first()
    )
    if not lesson:
        return None
    return {
        "id": lesson.id,
        "subject": lesson.subject,
        "topic": lesson.topic,
        "title": lesson.title,
        "content": lesson.content,
        "key_points": json.loads(lesson.key_points),
        "example": lesson.example,
    }


@router.get("/topics")
def get_topics(
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Return all distinct topics (with mastery info) for a subject."""
    q = db.query(Question.subject, Question.topic).distinct()
    if subject:
        q = q.filter(func.lower(Question.subject) == subject.lower())

    rows = q.all()
    masteries = {
        (m.subject, m.topic): m
        for m in db.query(TopicMastery).all()
    }

    result = []
    for subj, topic in rows:
        m = masteries.get((subj, topic))
        acc = (m.correct_count / m.total_attempts * 100) if m and m.total_attempts else 0.0
        result.append({
            "subject": subj,
            "topic": topic,
            "mastery_level": m.mastery_level if m else "not_started",
            "accuracy": round(acc, 1),
            "total_attempts": m.total_attempts if m else 0,
            "needs_review": m.needs_review if m else False,
        })
    result.sort(key=lambda x: (x["subject"], x["topic"]))
    return result
