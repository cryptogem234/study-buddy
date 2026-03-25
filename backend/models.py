from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False)
    difficulty = Column(String, default="medium")  # easy / medium / hard
    question_text = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)  # "A", "B", "C", or "D"
    explanation = Column(Text, nullable=False)

    answers = relationship("Answer", back_populates="question")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=True)

    answers = relationship("Answer", back_populates="session")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("QuizSession", back_populates="answers")
    question = relationship("Question", back_populates="answers")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon_emoji = Column(String, nullable=False)
    unlocked_at = Column(DateTime, nullable=True)


class TopicMastery(Base):
    __tablename__ = "topic_mastery"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False, index=True)
    total_attempts = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    mastery_level = Column(String, default="beginner")  # beginner / developing / proficient / mastered
    current_difficulty = Column(String, default="easy")
    needs_review = Column(Boolean, default=False)
    streak = Column(Integer, default=0)  # consecutive correct answers
    last_practiced = Column(DateTime, nullable=True)


class LessonCard(Base):
    __tablename__ = "lesson_cards"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    key_points = Column(Text, nullable=False)  # JSON array of strings
    example = Column(Text, nullable=True)
