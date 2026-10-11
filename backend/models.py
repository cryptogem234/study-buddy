from datetime import datetime
from sqlalchemy import ForeignKey, String, Integer, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)  # 7 or 8
    description: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(10), default="🔬")
    archived: Mapped[int] = mapped_column(Integer, default=0)  # 1 = finished grade, shown under Review
    position: Mapped[int] = mapped_column(Integer, default=0)

    topics: Mapped[list["Topic"]] = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    term: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str] = mapped_column(String(200), default="")
    hidden: Mapped[int] = mapped_column(Integer, default=0)  # 1 = duplicate of a topic in another subject

    subject: Mapped["Subject"] = relationship("Subject", back_populates="topics")
    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="topic", cascade="all, delete-orphan")
    questions: Mapped[list["Question"]] = relationship("Question", back_populates="topic", cascade="all, delete-orphan")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship("QuizAttempt", back_populates="topic", cascade="all, delete-orphan")
    lesson_progress: Mapped[list["LessonProgress"]] = relationship("LessonProgress", back_populates="topic", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    # {"check_yourself": [{question, answer}], "think_answers": [{number, answer}],
    #  "level_up": {title, standard, content, checks: [{question, answer}]}}
    extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="lessons")
    vocabulary_words: Mapped[list["VocabularyWord"]] = relationship("VocabularyWord", back_populates="lesson", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=False)  # list of strings (4 shown per quiz)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-based index into options
    explanation: Mapped[str] = mapped_column(Text, default="")
    skill: Mapped[str] = mapped_column(String(50), default="")
    difficulty: Mapped[str] = mapped_column(String(20), default="")  # foundation | on_grade | challenge ('' = older core question)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    level: Mapped[str] = mapped_column(String(20), default="core")  # core | level_up
    answers: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{question_id, correct}]

    topic: Mapped["Topic"] = relationship("Topic", back_populates="quiz_attempts")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="lesson_progress")


class VocabularyWord(Base):
    __tablename__ = "vocabulary_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    part_of_speech: Mapped[str] = mapped_column(String(50), default="")
    example_sentence: Mapped[str] = mapped_column(Text, default="")
    level: Mapped[str] = mapped_column(String(20), default="")  # level_up for Grade 9 words

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="vocabulary_words")


class Passage(Base):
    __tablename__ = "passages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # core (Grade 8) | level_up (Grade 9)
    genre: Mapped[str] = mapped_column(String(50), default="")
    text: Mapped[str] = mapped_column(Text, nullable=False)  # paragraphs separated by blank lines
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(Integer, default=0)
    glossary: Mapped[list] = mapped_column(JSON, default=list)  # [{word, definition}]
    written_prompt: Mapped[str] = mapped_column(Text, default="")
    rubric: Mapped[list] = mapped_column(JSON, default=list)  # list of criteria strings
    model_answer: Mapped[str] = mapped_column(Text, default="")

    questions: Mapped[list["PassageQuestion"]] = relationship(
        "PassageQuestion", back_populates="passage", cascade="all, delete-orphan", order_by="PassageQuestion.position"
    )
    attempts: Mapped[list["PassageAttempt"]] = relationship(
        "PassageAttempt", back_populates="passage", cascade="all, delete-orphan"
    )


class PassageQuestion(Base):
    __tablename__ = "passage_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passage_id: Mapped[int] = mapped_column(ForeignKey("passages.id"), nullable=False)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="")
    skill: Mapped[str] = mapped_column(String(50), default="")
    position: Mapped[int] = mapped_column(Integer, default=0)

    passage: Mapped["Passage"] = relationship("Passage", back_populates="questions")


class PassageAttempt(Base):
    __tablename__ = "passage_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passage_id: Mapped[int] = mapped_column(ForeignKey("passages.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    answers: Mapped[list] = mapped_column(JSON, default=list)  # [{question_id, skill, correct}]
    written_answer: Mapped[str] = mapped_column(Text, default="")
    written_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-4, None if not graded
    written_feedback: Mapped[str] = mapped_column(Text, default="")
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    passage: Mapped["Passage"] = relationship("Passage", back_populates="attempts")
