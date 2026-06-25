from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=gen_uuid)
    candidate_name = Column(String, nullable=True)
    role = Column(String, nullable=False)
    resume_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=list)
    extracted_technologies = Column(JSON, default=list)
    status = Column(String, default="active")  # active, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")
    summary = relationship("SessionSummary", back_populates="session", uselist=False, cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    context_used = Column(Text, nullable=True)
    topic = Column(String, nullable=True)
    difficulty = Column(String, default="medium")  # easy, medium, hard
    order_index = Column(Integer, default=0)
    answer = Column(Text, nullable=True)
    answer_score = Column(Float, nullable=True)
    answer_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="questions")


class SessionSummary(Base):
    __tablename__ = "session_summaries"

    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, unique=True)
    overall_score = Column(Float, nullable=True)
    strengths = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    recommendation = Column(String, nullable=True)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="summary")
