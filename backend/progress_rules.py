"""Shared rules for when a topic counts as completed and when Level Up unlocks."""
from datetime import datetime
from sqlalchemy.orm import Session
from models import Topic, Question, QuizAttempt, LessonProgress

PASS_SCORE = 0.8
# Quizzes taken before the pass mark went up to 80% still count at the old 70%.
OLD_PASS_SCORE = 0.7
PASS_MARK_RAISED_ON = datetime(2026, 10, 12)


def is_pass(attempt: QuizAttempt) -> bool:
    pct = attempt.score / attempt.total
    if attempt.attempted_at < PASS_MARK_RAISED_ON:
        return pct >= OLD_PASS_SCORE
    return pct >= PASS_SCORE


def is_level_up_question(q: Question) -> bool:
    return q.difficulty == "challenge"


def topic_state(topic: Topic, db: Session) -> dict:
    attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.topic_id == topic.id)
        .order_by(QuizAttempt.attempted_at.desc())
        .all()
    )
    core = [a for a in attempts if (a.level or "core") == "core"]
    level_up = [a for a in attempts if a.level == "level_up"]
    completed_ids = {
        lp.lesson_id
        for lp in db.query(LessonProgress).filter(LessonProgress.topic_id == topic.id).all()
    }
    questions = db.query(Question).filter(Question.topic_id == topic.id).all()
    core_count = sum(not is_level_up_question(q) for q in questions)
    level_up_count = len(questions) - core_count

    core_passed = any(is_pass(a) for a in core)
    lessons_done = len(topic.lessons) == 0 or len(completed_ids) >= len(topic.lessons)
    if not completed_ids and not attempts:
        status = "not_started"
    elif lessons_done and (core_passed or core_count == 0):
        status = "completed"
    else:
        status = "in_progress"

    return dict(
        status=status,
        attempts=attempts,
        core_attempts=core,
        best_score=max((a.score / a.total * 100 for a in core), default=None),
        lessons_completed=len(completed_ids),
        lesson_count=len(topic.lessons),
        question_count=core_count,
        level_up_count=level_up_count,
        level_up_unlocked=core_passed,
        has_level_up_lesson=any((l.extras or {}).get("level_up") for l in topic.lessons),
        level_up_best=max((a.score / a.total * 100 for a in level_up), default=None),
        level_up_passed=any(a.score / a.total >= PASS_SCORE for a in level_up),
    )
