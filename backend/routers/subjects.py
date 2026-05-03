from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Subject
from schemas import SubjectOut

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).order_by(Subject.grade, Subject.name).all()
    result = []
    for s in subjects:
        result.append(SubjectOut(
            id=s.id,
            name=s.name,
            grade=s.grade,
            description=s.description,
            icon=s.icon,
            topic_count=len(s.topics),
        ))
    return result
