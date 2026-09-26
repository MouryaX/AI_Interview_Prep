from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- INTERVIEW SCHEMAS ---
class InterviewStartRequest(BaseModel):
    user_id: Optional[int] = None
    role_category: str
    difficulty_level: int = 1
    max_questions: int = 3

class InterviewResponse(BaseModel):
    id: int
    role_category: str
    difficulty_level: int
    first_question: str
    created_at: datetime

    class Config:
        from_attributes = True

class AnswerSubmitRequest(BaseModel):
    interview_id: int
    answer: str

class AnswerSubmitResponse(BaseModel):
    next_question: Optional[str] = None
    is_completed: bool = False
    score: Optional[float] = None
    feedback: Optional[str] = None
    transcript: List[Dict[str, Any]] = []
