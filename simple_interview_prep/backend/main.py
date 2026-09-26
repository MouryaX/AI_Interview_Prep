from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from database import engine, Base, get_db
import models, schemas, crud
from gemini_service import gemini_service

# Auto-create table schemas on startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Simple Interview Preparation API",
    description="Minimal AI-Powered Mock Interview Platform",
    version="1.0.0"
)

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Simple Interview Prep API"}

@app.post("/users", response_model=schemas.UserResponse)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_data.email)
    if existing:
        return existing
    return crud.create_user(db, user_data)

@app.post("/interviews/start", response_model=schemas.InterviewResponse)
async def start_interview(data: schemas.InterviewStartRequest, db: Session = Depends(get_db)):
    # 1. Generate opening question via Gemini
    first_question = await gemini_service.generate_first_question(
        role=data.role_category,
        difficulty=data.difficulty_level
    )
    
    # 2. Persist new session in PostgreSQL
    session = crud.create_interview_session(db, data, first_question)
    
    return {
        "id": session.id,
        "role_category": session.role_category,
        "difficulty_level": session.difficulty_level,
        "first_question": first_question,
        "created_at": session.created_at
    }

@app.post("/interviews/submit-answer", response_model=schemas.AnswerSubmitResponse)
async def submit_answer(data: schemas.AnswerSubmitRequest, db: Session = Depends(get_db)):
    # 1. Fetch current interview session
    session = crud.get_interview_session(db, data.interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    if session.overall_status == "completed":
        return {
            "next_question": None,
            "is_completed": True,
            "score": session.score,
            "feedback": session.feedback,
            "transcript": session.transcript
        }
    
    # 2. Check if this is the final question
    next_question_num = session.questions_count + 1
    
    if next_question_num >= session.max_questions:
        # Final Question Answered ➔ Run Gemini Evaluation & Complete Interview
        temp_transcript = list(session.transcript) + [{"role": "user", "content": data.answer}]
        eval_data = await gemini_service.evaluate_interview(session.role_category, temp_transcript)
        
        updated_session = crud.complete_interview_session(db, session, data.answer, eval_data)
        
        return {
            "next_question": None,
            "is_completed": True,
            "score": updated_session.score,
            "feedback": updated_session.feedback,
            "transcript": updated_session.transcript
        }
    else:
        # Generate next follow-up question
        temp_transcript = list(session.transcript) + [{"role": "user", "content": data.answer}]
        next_question = await gemini_service.generate_next_question(session.role_category, temp_transcript)
        
        updated_session = crud.save_answer_and_question(db, session, data.answer, next_question)
        
        return {
            "next_question": next_question,
            "is_completed": False,
            "score": None,
            "feedback": None,
            "transcript": updated_session.transcript
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
