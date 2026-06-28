from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import Subject, Topic, Lesson, Question, LessonProgress, QuizAttempt
from schemas import QuizAttemptIn, QuizAttemptOut, ProgressSummary, SubjectProgress, TopicProgress

router = APIRouter(tags=["progress"])


def calc_streak(db: Session) -> int:
    quiz_dates = db.query(func.date(QuizAttempt.attempted_at)).distinct().all()
    lesson_dates = db.query(func.date(LessonProgress.completed_at)).distinct().all()

    all_dates: set[date] = set()
    for (d,) in quiz_dates:
        all_dates.add(d if isinstance(d, date) else date.fromisoformat(str(d)))
    for (d,) in lesson_dates:
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


def topic_status(topic, db: Session) -> tuple[str, float | None, int, list[QuizAttempt]]:
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.topic_id == topic.id)
        .order_by(QuizAttempt.attempted_at.desc())
        .all()
    )
    completed_ids = {
        lp.lesson_id
        for lp in db.query(LessonProgress).filter(LessonProgress.topic_id == topic.id).all()
    }
    has_questions = db.query(Question).filter(Question.topic_id == topic.id).count() > 0
    best = max((a.score / a.total * 100 for a in attempts), default=None)

    has_activity = len(completed_ids) > 0 or len(attempts) > 0
    if not has_activity:
        return "not_started", best, len(completed_ids), attempts

    lessons_done = len(topic.lessons) == 0 or len(completed_ids) >= len(topic.lessons)
    quiz_passed = any(a.score / a.total >= 0.7 for a in attempts) if attempts else False
    if lessons_done and (quiz_passed or not has_questions):
        return "completed", best, len(completed_ids), attempts
    return "in_progress", best, len(completed_ids), attempts


@router.post("/quiz-attempts", response_model=QuizAttemptOut)
def save_quiz_attempt(body: QuizAttemptIn, db: Session = Depends(get_db)):
    attempt = QuizAttempt(topic_id=body.topic_id, score=body.score, total=body.total)
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
    return ProgressSummary(
        total_subjects=db.query(Subject).count(),
        total_topics=db.query(Topic).count(),
        total_lessons=db.query(Lesson).count(),
        lessons_completed=db.query(LessonProgress).count(),
        quizzes_taken=len(attempts),
        average_score=avg_score,
        current_streak=calc_streak(db),
        recent_attempts=[QuizAttemptOut.model_validate(a) for a in attempts[:10]],
    )


@router.get("/progress/subjects", response_model=list[SubjectProgress])
def get_subject_progress(db: Session = Depends(get_db)):
    subjects = db.query(Subject).order_by(Subject.grade).all()
    result = []
    for s in subjects:
        topics = db.query(Topic).filter(Topic.subject_id == s.id).order_by(Topic.order).all()
        topic_list = []
        completed = 0
        for t in topics:
            status, best, lessons_done, attempts = topic_status(t, db)
            if status == "completed":
                completed += 1
            q_count = db.query(Question).filter(Question.topic_id == t.id).count()
            topic_list.append(TopicProgress(
                topic_id=t.id,
                topic_name=t.name,
                unit=t.unit,
                term=t.term,
                status=status,
                best_score=best,
                lessons_completed=lessons_done,
                lesson_count=len(t.lessons),
                question_count=q_count,
                attempts=[QuizAttemptOut.model_validate(a) for a in attempts],
                trend=attempt_trend(attempts),
            ))
        result.append(SubjectProgress(
            subject_id=s.id,
            subject_name=s.name,
            grade=s.grade,
            icon=s.icon,
            topics=topic_list,
            completed_count=completed,
            total_count=len(topics),
        ))
    return result
