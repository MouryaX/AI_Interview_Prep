from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "simple_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    interviews = relationship("InterviewSession", back_populates="user")


class InterviewSession(Base):
    __tablename__ = "simple_interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("simple_users.id"), nullable=True)
    role_category = Column(String)
    difficulty_level = Column(Integer, default=1)
    questions_count = Column(Integer, default=0)
    max_questions = Column(Integer, default=3)
    overall_status = Column(String, default="in_progress")
    transcript = Column(JSON, default=[])
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="interviews")
