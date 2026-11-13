# Data & user management: my profile, my request history (logs), and feedback.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User 


router = APIRouter(tags=['Data & User Management'])

# Users 
@router.get("/users/me", response_model=schemas.UserOut)
def read_me(user: User = Depends(get_current_user)):
    """Who am I? Returns the logged-in user's profile."""
    return user 

# Logs 
@router.get("/logs", response_model=list[schemas.LogOut])
def my_logs(limit: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """My latest ML / RAG requests (newes first)"""
    return crud.get_logs(db, user.id, limit)

# Feedback 
@router.post("/feedback", response_model=schemas.FeedbackOut)
def give_feedback(fb: schemas.FeedbackCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Rate an answer (1-5). Pass Log_id from the /rag/chat response to link it."""
    if fb.log_id is not None:
        log = crud.get_log(db, fb.log_id)
        if log is None or log.user_id != user.id:
            raise HTTPException(status_code=404, detail="Log not found")

    return crud.create_feedback(db, user.id, fb.rating, fb.comment, fb.log_id)

@router.get("/feedback", response_model=list[schemas.FeedbackOut])
def my_feedback(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """All feedback I have given."""
    return crud.get_feedback(db, user.id)

