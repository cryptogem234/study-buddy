from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Topic, Question, QuizAttempt, LessonProgress
from schemas import TopicOut

router = APIRouter(prefix="/subjects", tags=["topics"])


def compute_status(topic, completed_lesson_ids, attempts, has_questions):
    has_activity = len(completed_lesson_ids) > 0 or len(attempts) > 0
    if not has_activity:
        return "not_started"
    lessons_done = len(topic.lessons) == 0 or len(completed_lesson_ids) >= len(topic.lessons)
    quiz_passed = any(a.score / a.total >= 0.7 for a in attempts) if attempts else False
    if lessons_done and (quiz_passed or not has_questions):
        return "completed"
    return "in_progress"


@router.get("/{subject_id}/topics", response_model=list[TopicOut])
def list_topics(subject_id: int, db: Session = Depends(get_db)):
    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.order)
        .all()
    )

    result = []
    for t in topics:
        attempts = db.query(QuizAttempt).filter(QuizAttempt.topic_id == t.id).all()
        best_score = max((a.score / a.total * 100 for a in attempts), default=None)

        completed_ids = {
            lp.lesson_id
            for lp in db.query(LessonProgress).filter(LessonProgress.topic_id == t.id).all()
        }
        q_count = db.query(Question).filter(Question.topic_id == t.id).count()
        status = compute_status(t, completed_ids, attempts, q_count > 0)

        result.append(TopicOut(
            id=t.id,
            subject_id=t.subject_id,
            name=t.name,
            order=t.order,
            term=t.term,
            unit=t.unit,
            lesson_count=len(t.lessons),
            question_count=q_count,
            lessons_completed=len(completed_ids),
            best_score=best_score,
            status=status,
        ))
    return result
