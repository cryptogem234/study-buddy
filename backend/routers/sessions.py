from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import QuizSession

router = APIRouter()


class SessionCreate(BaseModel):
    subject: str


class SessionComplete(BaseModel):
    score: int
    total_questions: int


class SessionOut(BaseModel):
    id: int
    subject: str
    started_at: datetime
    completed_at: Optional[datetime]
    score: Optional[int]
    total_questions: Optional[int]

    class Config:
        from_attributes = True


@router.post("/sessions", response_model=SessionOut)
def start_session(payload: SessionCreate, db: Session = Depends(get_db)):
    session = QuizSession(subject=payload.subject)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.put("/sessions/{session_id}/complete", response_model=SessionOut)
def complete_session(session_id: int, payload: SessionComplete, db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.completed_at = datetime.utcnow()
    session.score = payload.score
    session.total_questions = payload.total_questions
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=list[SessionOut])
def get_sessions(db: Session = Depends(get_db)):
    return (
        db.query(QuizSession)
        .filter(QuizSession.completed_at.isnot(None))
        .order_by(QuizSession.completed_at.desc())
        .all()
    )
