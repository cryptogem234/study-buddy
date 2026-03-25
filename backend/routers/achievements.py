from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import Achievement, QuizSession, Answer, TopicMastery

router = APIRouter()


class AchievementOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon_emoji: str
    unlocked_at: Optional[datetime]

    class Config:
        from_attributes = True


class AchievementCheckResponse(BaseModel):
    newly_unlocked: list[str]


@router.get("/achievements", response_model=list[AchievementOut])
def get_achievements(db: Session = Depends(get_db)):
    return db.query(Achievement).order_by(Achievement.id).all()


@router.post("/achievements/check", response_model=AchievementCheckResponse)
def check_achievements(db: Session = Depends(get_db)):
    completed = (
        db.query(QuizSession)
        .filter(QuizSession.completed_at.isnot(None))
        .all()
    )

    total_sessions     = len(completed)
    total_answers      = db.query(Answer).count()
    correct_answers    = db.query(Answer).filter(Answer.is_correct == True).count()

    english_sessions   = [s for s in completed if s.subject and s.subject.lower() == "english"]
    science_sessions   = [s for s in completed if s.subject and s.subject.lower() == "science"]

    def pct(s):
        return (s.score / s.total_questions * 100) if s.total_questions else 0

    perfect_sessions   = [s for s in completed if pct(s) == 100]
    eng_perfect        = [s for s in english_sessions if pct(s) == 100]
    sci_perfect        = [s for s in science_sessions if pct(s) == 100]
    eng_80_plus        = [s for s in english_sessions if pct(s) >= 80]
    sci_80_plus        = [s for s in science_sessions if pct(s) >= 80]

    # Distinct calendar days with a completed session
    distinct_days = len({
        s.completed_at.date()
        for s in completed if s.completed_at
    })

    # Study streak (consecutive days ending today or yesterday)
    from datetime import date, timedelta
    day_set = {s.completed_at.date() for s in completed if s.completed_at}
    streak = 0
    check_day = date.today()
    if check_day not in day_set:
        check_day = check_day - timedelta(days=1)
    while check_day in day_set:
        streak += 1
        check_day -= timedelta(days=1)

    # Topic mastery
    has_mastered_topic = (
        db.query(TopicMastery)
        .filter(TopicMastery.mastery_level == "mastered")
        .first()
    ) is not None

    # Comeback kid: 80%+ after a sub-60% session in same subject
    comeback = False
    for subj_sessions in [english_sessions, science_sessions]:
        scores = [pct(s) for s in sorted(subj_sessions, key=lambda x: x.completed_at)]
        for i, sc in enumerate(scores):
            if sc < 60 and any(s2 >= 80 for s2 in scores[i+1:]):
                comeback = True
                break

    newly_unlocked: list[str] = []

    def unlock(slug: str):
        ach = db.query(Achievement).filter(Achievement.slug == slug).first()
        if ach and ach.unlocked_at is None:
            ach.unlocked_at = datetime.utcnow()
            db.commit()
            newly_unlocked.append(slug)

    if total_sessions >= 1:         unlock("first-quiz")
    if len(perfect_sessions) >= 1:  unlock("perfect-score")
    if total_sessions >= 5:         unlock("on-a-roll")
    if total_sessions >= 10:        unlock("quiz-marathon")
    if total_answers >= 50:         unlock("half-century")
    if total_answers >= 100:        unlock("century")
    if streak >= 3:                 unlock("streak-3")
    if streak >= 7:                 unlock("streak-7")
    if len(sci_80_plus) >= 5:       unlock("science-star")
    if len(eng_80_plus) >= 5:       unlock("word-wizard")
    if has_mastered_topic:          unlock("topic-master")
    if comeback:                    unlock("comeback-kid")
    if len(eng_perfect) >= 1:       unlock("ace-english")
    if len(sci_perfect) >= 1:       unlock("ace-science")
    if distinct_days >= 7:          unlock("dedicated")

    return AchievementCheckResponse(newly_unlocked=newly_unlocked)
