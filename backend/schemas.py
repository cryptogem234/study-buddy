from datetime import datetime
from pydantic import BaseModel


class SubjectOut(BaseModel):
    id: int
    name: str
    grade: int
    description: str
    icon: str
    topic_count: int = 0

    model_config = {"from_attributes": True}


class TopicOut(BaseModel):
    id: int
    subject_id: int
    name: str
    order: int
    term: int
    unit: str
    lesson_count: int = 0
    question_count: int = 0
    lessons_completed: int = 0
    best_score: float | None = None
    status: str = "not_started"   # not_started | in_progress | completed

    model_config = {"from_attributes": True}


class LessonOut(BaseModel):
    id: int
    topic_id: int
    title: str
    content: str
    order: int
    completed: bool = False

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: int
    topic_id: int
    stem: str
    options: list[str]
    correct_index: int
    explanation: str

    model_config = {"from_attributes": True}


class QuizAttemptIn(BaseModel):
    topic_id: int
    score: int
    total: int


class QuizAttemptOut(BaseModel):
    id: int
    topic_id: int
    score: int
    total: int
    attempted_at: datetime

    model_config = {"from_attributes": True}


class LessonProgressIn(BaseModel):
    lesson_id: int


class TopicProgress(BaseModel):
    topic_id: int
    topic_name: str
    unit: str
    term: int
    status: str
    best_score: float | None
    lessons_completed: int
    lesson_count: int
    question_count: int


class SubjectProgress(BaseModel):
    subject_id: int
    subject_name: str
    grade: int
    icon: str
    topics: list[TopicProgress]
    completed_count: int
    total_count: int


class ProgressSummary(BaseModel):
    total_subjects: int
    total_topics: int
    lessons_completed: int
    total_lessons: int
    quizzes_taken: int
    average_score: float | None
    current_streak: int
    recent_attempts: list[QuizAttemptOut]
