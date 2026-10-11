from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import Subject, Topic, Lesson, LessonProgress, QuizAttempt, PassageAttempt
from progress_rules import topic_state
from schemas import QuizAttemptIn, QuizAttemptOut, ProgressSummary, SubjectProgress, TopicProgress

router = APIRouter(tags=["progress"])


def calc_streak(db: Session) -> int:
    all_dates: set[date] = set()
    for column in (QuizAttempt.attempted_at, LessonProgress.completed_at, PassageAttempt.attempted_at):
        for (d,) in db.query(func.date(column)).distinct().all():
            all_dates.add(d if isinstance(d, date) else date.fromisoformat(str(d)))

    if not all_dates:
        return 0

    today = date.today()
    sorted_dates = sorted(all_dates, reverse=True)

    if sorted_dates[0] < today - timedelta(days=1):
        return 0

    streak = 1
    for i in range(len(sorted_dates) - 1):
        if sorted_dates[i] - sorted_dates[i + 1] == timedelta(days=1):
            streak += 1
        else:
            break
    return streak


def attempt_trend(attempts: list[QuizAttempt]) -> str | None:
    if len(attempts) < 2:
        return None
    latest, previous = attempts[0], attempts[1]
    latest_pct = latest.score / latest.total
    previous_pct = previous.score / previous.total
    if latest_pct > previous_pct:
        return "up"
    if latest_pct < previous_pct:
        return "down"
    return "flat"


@router.post("/quiz-attempts", response_model=QuizAttemptOut)
def save_quiz_attempt(body: QuizAttemptIn, db: Session = Depends(get_db)):
    attempt = QuizAttempt(
        topic_id=body.topic_id, score=body.score, total=body.total, level=body.level,
        answers=[a.model_dump() for a in body.answers] if body.answers else None,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/progress", response_model=ProgressSummary)
def get_progress(db: Session = Depends(get_db)):
    attempts = db.query(QuizAttempt).order_by(QuizAttempt.attempted_at.desc()).all()
    avg_score = (
        sum(a.score / a.total * 100 for a in attempts) / len(attempts)
        if attempts else None
    )
    completed_lesson_ids = {lp.lesson_id for lp in db.query(LessonProgress).all()}
    # Lessons in hidden duplicate topics only count once they have been read
    lesson_rows = db.query(Lesson.id, Topic.hidden).join(Topic, Topic.id == Lesson.topic_id).all()
    total_lessons = sum(1 for lid, hidden in lesson_rows if not hidden or lid in completed_lesson_ids)
    return ProgressSummary(
        total_subjects=db.query(Subject).count(),
        total_topics=db.query(Topic).filter(Topic.hidden == 0).count(),
        total_lessons=total_lessons,
        lessons_completed=len(completed_lesson_ids),
        quizzes_taken=len(attempts),
        average_score=avg_score,
        current_streak=calc_streak(db),
        recent_attempts=[QuizAttemptOut.model_validate(a) for a in attempts[:10]],
    )


@router.get("/progress/subjects", response_model=list[SubjectProgress])
def get_subject_progress(db: Session = Depends(get_db)):
    subjects = db.query(Subject).order_by(Subject.position, Subject.grade).all()
    result = []
    for s in subjects:
        topics = db.query(Topic).filter(Topic.subject_id == s.id).order_by(Topic.order).all()
        topic_list = []
        completed = 0
        level_up_passed = 0
        level_up_total = 0
        for t in topics:
            st = topic_state(t, db)
            # Hidden duplicates appear only if she already worked on them
            if t.hidden and st["status"] == "not_started":
                continue
            if st["status"] == "completed":
                completed += 1
            if st["level_up_count"]:
                level_up_total += 1
                level_up_passed += st["level_up_passed"]
            topic_list.append(TopicProgress(
                topic_id=t.id,
                topic_name=t.name,
                unit=t.unit,
                term=t.term,
                status=st["status"],
                best_score=st["best_score"],
                lessons_completed=st["lessons_completed"],
                lesson_count=st["lesson_count"],
                question_count=st["question_count"],
                attempts=[QuizAttemptOut.model_validate(a) for a in st["attempts"]],
                trend=attempt_trend(st["core_attempts"]),
                hidden=bool(t.hidden),
                level_up_count=st["level_up_count"],
                level_up_unlocked=st["level_up_unlocked"],
                level_up_best=st["level_up_best"],
                level_up_passed=st["level_up_passed"],
            ))
        result.append(SubjectProgress(
            subject_id=s.id,
            subject_name=s.name,
            grade=s.grade,
            icon=s.icon,
            topics=topic_list,
            completed_count=completed,
            total_count=len(topic_list),
            archived=bool(s.archived),
            level_up_passed_count=level_up_passed,
            level_up_total=level_up_total,
        ))
    return result
