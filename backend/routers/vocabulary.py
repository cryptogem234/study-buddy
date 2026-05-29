from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import VocabularyWord, Lesson
from schemas import VocabularyWordOut

router = APIRouter(tags=["vocabulary"])


@router.get("/topics/{topic_id}/vocabulary", response_model=list[VocabularyWordOut])
def get_topic_vocabulary(topic_id: int, db: Session = Depends(get_db)):
    lesson_ids = [
        row[0]
        for row in db.query(Lesson.id).filter(Lesson.topic_id == topic_id).all()
    ]
    if not lesson_ids:
        return []
    return (
        db.query(VocabularyWord)
        .filter(VocabularyWord.lesson_id.in_(lesson_ids))
        .order_by(VocabularyWord.lesson_id, VocabularyWord.id)
        .all()
    )
