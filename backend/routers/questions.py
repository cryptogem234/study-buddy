from typing import Literal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Question
from progress_rules import is_level_up_question
from schemas import QuestionOut

router = APIRouter(tags=["questions"])


@router.get("/topics/{topic_id}/questions", response_model=list[QuestionOut])
def list_questions(topic_id: int, level: Literal["core", "level_up"] = "core", db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.topic_id == topic_id).all()
    want_level_up = level == "level_up"
    return [q for q in questions if is_level_up_question(q) == want_level_up]
