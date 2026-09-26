from sqlalchemy.orm import Session
import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_data: schemas.UserCreate):
    db_user = models.User(email=user_data.email, full_name=user_data.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_interview_session(db: Session, data: schemas.InterviewStartRequest, first_question: str):
    new_session = models.InterviewSession(
        user_id=data.user_id,
        role_category=data.role_category,
        difficulty_level=data.difficulty_level,
        max_questions=data.max_questions,
        questions_count=0,
        overall_status="in_progress",
        transcript=[{"role": "assistant", "content": first_question}]
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_interview_session(db: Session, interview_id: int):
    return db.query(models.InterviewSession).filter(models.InterviewSession.id == interview_id).first()

def save_answer_and_question(db: Session, session: models.InterviewSession, answer: str, next_question: str):
    # Re-assign transcript list to trigger SQLAlchemy JSON mutation detection
    updated_transcript = list(session.transcript)
    updated_transcript.append({"role": "user", "content": answer})
    updated_transcript.append({"role": "assistant", "content": next_question})
    
    session.transcript = updated_transcript
    session.questions_count += 1
    db.commit()
    db.refresh(session)
    return session

def complete_interview_session(db: Session, session: models.InterviewSession, answer: str, eval_data: dict):
    updated_transcript = list(session.transcript)
    updated_transcript.append({"role": "user", "content": answer})
    
    session.transcript = updated_transcript
    session.questions_count += 1
    session.overall_status = "completed"
    session.score = eval_data.get("score", 7.0)
    session.feedback = eval_data.get("feedback", "Interview completed.")
    db.commit()
    db.refresh(session)
    return session
