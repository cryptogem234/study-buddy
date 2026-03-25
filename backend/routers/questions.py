from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import random

from database import get_db
from models import Question, Answer, QuizSession, TopicMastery

router = APIRouter()


class QuestionOut(BaseModel):
    id: int
    subject: str
    topic: str
    difficulty: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True


class CheckAnswerRequest(BaseModel):
    question_id: int
    answer: str
    session_id: Optional[int] = None


class CheckAnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    explanation: str


@router.get("/questions", response_model=list[QuestionOut])
def get_questions(
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(Question)
    if subject:
        query = query.filter(func.lower(Question.subject) == subject.lower())
    if topic:
        query = query.filter(func.lower(Question.topic) == topic.lower())
    questions = query.all()
    random.shuffle(questions)
    return questions[:limit]


@router.post("/questions/check", response_model=CheckAnswerResponse)
def check_answer(payload: CheckAnswerRequest, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = payload.answer.upper() == question.correct_answer.upper()

    if payload.session_id:
        # Record the individual answer
        db.add(Answer(
            session_id=payload.session_id,
            question_id=payload.question_id,
            selected=payload.answer.upper(),
            is_correct=is_correct,
        ))

        # Update (or create) topic mastery
        mastery = (
            db.query(TopicMastery)
            .filter(
                TopicMastery.subject == question.subject,
                TopicMastery.topic == question.topic,
            )
            .first()
        )
        if not mastery:
            mastery = TopicMastery(subject=question.subject, topic=question.topic)
            db.add(mastery)
            db.flush()

        mastery.total_attempts += 1
        if is_correct:
            mastery.correct_count += 1
            mastery.streak += 1
        else:
            mastery.streak = 0

        mastery.last_practiced = datetime.utcnow()

        # recalculate mastery level
        if mastery.total_attempts > 0:
            acc = mastery.correct_count / mastery.total_attempts
            mastery.needs_review = acc < 0.65 and mastery.total_attempts >= 5
            if acc >= 0.85 and mastery.total_attempts >= 5:
                mastery.mastery_level = "mastered";      mastery.current_difficulty = "hard"
            elif acc >= 0.65:
                mastery.mastery_level = "proficient";    mastery.current_difficulty = "hard" if acc >= 0.80 else "medium"
            elif acc >= 0.40:
                mastery.mastery_level = "developing";    mastery.current_difficulty = "medium" if acc >= 0.55 else "easy"
            else:
                mastery.mastery_level = "beginner";      mastery.current_difficulty = "easy"

        db.commit()

    return CheckAnswerResponse(
        correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
    )
