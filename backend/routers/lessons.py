from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Lesson, LessonProgress
from schemas import LessonOut, LessonProgressIn

router = APIRouter(tags=["lessons"])


@router.get("/topics/{topic_id}/lessons", response_model=list[LessonOut])
def list_lessons(topic_id: int, db: Session = Depends(get_db)):
    lessons = (
        db.query(Lesson)
        .filter(Lesson.topic_id == topic_id)
        .order_by(Lesson.order)
        .all()
    )
    completed_ids = {
        lp.lesson_id
        for lp in db.query(LessonProgress).filter(LessonProgress.topic_id == topic_id).all()
    }
    return [
        LessonOut(
            id=l.id,
            topic_id=l.topic_id,
            title=l.title,
            content=l.content,
            order=l.order,
            completed=l.id in completed_ids,
        )
        for l in lessons
    ]


@router.post("/topics/{topic_id}/lesson-progress")
def mark_lesson_complete(topic_id: int, body: LessonProgressIn, db: Session = Depends(get_db)):
    existing = (
        db.query(LessonProgress)
        .filter(LessonProgress.topic_id == topic_id, LessonProgress.lesson_id == body.lesson_id)
        .first()
    )
    if not existing:
        db.add(LessonProgress(topic_id=topic_id, lesson_id=body.lesson_id))
        db.commit()
    return {"ok": True}
