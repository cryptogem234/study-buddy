from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import QuizSession, Answer

router = APIRouter()


class ProgressSummary(BaseModel):
    total_questions_answered: int
    overall_accuracy: float
    total_sessions: int
    current_streak: int


class SubjectBreakdown(BaseModel):
    subject: str
    total_questions: int
    correct: int
    accuracy: float


class ChartPoint(BaseModel):
    date: str
    score: float
    sessions: int


@router.get("/progress/summary", response_model=ProgressSummary)
def get_summary(db: Session = Depends(get_db)):
    answers = db.query(Answer).all()
    total = len(answers)
    correct = sum(1 for a in answers if a.is_correct)
    accuracy = round((correct / total * 100), 1) if total > 0 else 0.0

    completed_sessions = (
        db.query(QuizSession)
        .filter(QuizSession.completed_at.isnot(None))
        .order_by(QuizSession.completed_at.desc())
        .all()
    )
    total_sessions = len(completed_sessions)

    # Calculate streak: consecutive days with at least one completed session
    streak = 0
    if completed_sessions:
        today = datetime.utcnow().date()
        check_date = today
        session_dates = set(s.completed_at.date() for s in completed_sessions if s.completed_at)

        # Allow streak to start from today or yesterday
        if check_date not in session_dates:
            check_date -= timedelta(days=1)

        while check_date in session_dates:
            streak += 1
            check_date -= timedelta(days=1)

    return ProgressSummary(
        total_questions_answered=total,
        overall_accuracy=accuracy,
        total_sessions=total_sessions,
        current_streak=streak,
    )


@router.get("/progress/by-subject", response_model=list[SubjectBreakdown])
def get_by_subject(db: Session = Depends(get_db)):
    sessions = db.query(QuizSession).filter(QuizSession.completed_at.isnot(None)).all()

    subject_map: dict[str, dict] = {}
    for session in sessions:
        subj = session.subject
        if subj not in subject_map:
            subject_map[subj] = {"total": 0, "correct": 0}
        for answer in session.answers:
            subject_map[subj]["total"] += 1
            if answer.is_correct:
                subject_map[subj]["correct"] += 1

    result = []
    for subj, data in subject_map.items():
        total = data["total"]
        correct = data["correct"]
        result.append(
            SubjectBreakdown(
                subject=subj,
                total_questions=total,
                correct=correct,
                accuracy=round((correct / total * 100), 1) if total > 0 else 0.0,
            )
        )
    return result


@router.get("/progress/chart", response_model=list[ChartPoint])
def get_chart(db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=30)
    sessions = (
        db.query(QuizSession)
        .filter(
            QuizSession.completed_at.isnot(None),
            QuizSession.completed_at >= since,
        )
        .all()
    )

    daily: dict[str, dict] = {}
    for session in sessions:
        if not session.completed_at or not session.total_questions:
            continue
        date_str = session.completed_at.date().isoformat()
        if date_str not in daily:
            daily[date_str] = {"total_score": 0, "total_possible": 0, "sessions": 0}
        daily[date_str]["total_score"] += session.score or 0
        daily[date_str]["total_possible"] += session.total_questions
        daily[date_str]["sessions"] += 1

    result = []
    for date_str in sorted(daily.keys()):
        d = daily[date_str]
        pct = round((d["total_score"] / d["total_possible"] * 100), 1) if d["total_possible"] > 0 else 0.0
        result.append(ChartPoint(date=date_str, score=pct, sessions=d["sessions"]))

    return result
