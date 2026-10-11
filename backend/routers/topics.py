from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Topic
from progress_rules import topic_state
from schemas import TopicOut

router = APIRouter(prefix="/subjects", tags=["topics"])


@router.get("/{subject_id}/topics", response_model=list[TopicOut])
def list_topics(subject_id: int, db: Session = Depends(get_db)):
    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id, Topic.hidden == 0)
        .order_by(Topic.order)
        .all()
    )

    result = []
    for t in topics:
        st = topic_state(t, db)
        result.append(TopicOut(
            id=t.id,
            subject_id=t.subject_id,
            name=t.name,
            order=t.order,
            term=t.term,
            unit=t.unit,
            lesson_count=st["lesson_count"],
            question_count=st["question_count"],
            lessons_completed=st["lessons_completed"],
            best_score=st["best_score"],
            status=st["status"],
            level_up_count=st["level_up_count"],
            has_level_up_lesson=st["has_level_up_lesson"],
            level_up_unlocked=st["level_up_unlocked"],
            level_up_best=st["level_up_best"],
            level_up_passed=st["level_up_passed"],
        ))
    return result
