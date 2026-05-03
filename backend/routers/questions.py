from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Question
from schemas import QuestionOut

router = APIRouter(tags=["questions"])


@router.get("/topics/{topic_id}/questions", response_model=list[QuestionOut])
def list_questions(topic_id: int, db: Session = Depends(get_db)):
    return db.query(Question).filter(Question.topic_id == topic_id).all()
