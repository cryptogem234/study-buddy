from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class SubjectOut(BaseModel):
    id: int
    name: str
    grade: int
    description: str
    icon: str
    topic_count: int = 0
    archived: bool = False

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
    has_level_up_lesson: bool = False
    level_up_count: int = 0
    level_up_unlocked: bool = False
    level_up_best: float | None = None
    level_up_passed: bool = False

    model_config = {"from_attributes": True}


class LessonOut(BaseModel):
    id: int
    topic_id: int
    title: str
    content: str
    order: int
    completed: bool = False
    extras: dict | None = None
    level_up_unlocked: bool = False
    level_up_count: int = 0

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: int
    topic_id: int
    stem: str
    options: list[str]
    correct_index: int
    explanation: str

    model_config = {"from_attributes": True}


class AnswerRecord(BaseModel):
    question_id: int
    correct: bool


class QuizAttemptIn(BaseModel):
    topic_id: int
    score: int
    total: int
    level: Literal["core", "level_up"] = "core"
    answers: list[AnswerRecord] | None = None


class QuizAttemptOut(BaseModel):
    id: int
    topic_id: int
    score: int
    total: int
    attempted_at: datetime
    level: str | None = "core"

    model_config = {"from_attributes": True}


class LessonProgressIn(BaseModel):
    lesson_id: int


class VocabularyWordOut(BaseModel):
    id: int
    lesson_id: int
    word: str
    definition: str
    part_of_speech: str
    example_sentence: str
    level: str | None = ""

    model_config = {"from_attributes": True}


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
    attempts: list[QuizAttemptOut] = []
    trend: str | None = None   # "up" | "down" | "flat" | None (fewer than 2 attempts)
    hidden: bool = False
    level_up_count: int = 0
    level_up_unlocked: bool = False
    level_up_best: float | None = None
    level_up_passed: bool = False


class SubjectProgress(BaseModel):
    subject_id: int
    subject_name: str
    grade: int
    icon: str
    topics: list[TopicProgress]
    completed_count: int
    total_count: int
    archived: bool = False
    level_up_passed_count: int = 0
    level_up_total: int = 0


class ProgressSummary(BaseModel):
    total_subjects: int
    total_topics: int
    lessons_completed: int
    total_lessons: int
    quizzes_taken: int
    average_score: float | None
    current_streak: int
    recent_attempts: list[QuizAttemptOut]


class PassageSummary(BaseModel):
    id: int
    title: str
    level: str
    genre: str
    word_count: int
    position: int
    best_score: float | None = None
    attempt_count: int = 0
    passed: bool = False
    unlocked: bool = True


class PassageQuestionOut(BaseModel):
    id: int
    stem: str
    options: list[str]
    correct_index: int
    explanation: str
    skill: str

    model_config = {"from_attributes": True}


class PassageOut(BaseModel):
    id: int
    title: str
    level: str
    genre: str
    text: str
    word_count: int
    glossary: list[dict]
    written_prompt: str
    rubric: list[str]
    model_answer: str
    questions: list[PassageQuestionOut]
    unlocked: bool = True

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class PassageAttemptIn(BaseModel):
    passage_id: int
    score: int
    total: int
    answers: list[AnswerRecord]


class WrittenAnswerIn(BaseModel):
    answer: str


class WrittenResult(BaseModel):
    graded: bool
    score: int | None = None
    feedback: str = ""


class SkillStat(BaseModel):
    skill: str
    correct: int
    total: int


class ReadingProgress(BaseModel):
    passages_total: int
    passages_done: int
    passages_passed: int
    average_score: float | None
    written_average: float | None
    written_count: int
    level_up_unlocked: bool
    core_passed_needed: int
    skills: list[SkillStat]
